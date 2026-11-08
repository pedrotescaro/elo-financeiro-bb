import http.cookiejar
import json
from pathlib import Path
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import Request, build_opener, HTTPCookieProcessor
from elo.server import DemoServer


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # A suíte compartilha o IP local; limites de requisições têm testes próprios.
        cls.server = DemoServer(("127.0.0.1", 0), rate_limit=1000)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = "http://127.0.0.1:" + str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.jar = http.cookiejar.CookieJar()
        self.client = build_opener(HTTPCookieProcessor(self.jar))
        with self.client.open(self.base + "/api/state") as response:
            self.state = json.load(response)

    def post(self, path, payload, token=None):
        request = Request(
            self.base + path,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "X-Demo-CSRF": token or self.state["csrf"]},
        )
        with self.client.open(request) as response:
            return json.load(response)

    def test_complete_consent_approval_monitoring_flow(self):
        state = self.post("/api/consent", {"enabled": True})
        state = self.post("/api/approve", {"report_id": state["report"]["report_id"], "action_id": "budget-plan"})
        self.assertEqual(state["report"]["results"]["cashflow"]["minimum_cents"], 20000)
        state = self.post("/api/monitor", {})
        self.assertEqual(state["report"]["results"]["cashflow"]["minimum_cents"], 5000)

    def test_invalid_csrf_rejected(self):
        with self.assertRaises(HTTPError) as error:
            self.post("/api/consent", {"enabled": True}, "wrong")
        self.assertEqual(error.exception.code, 403)

    def test_invalid_body_rejected(self):
        with self.assertRaises(HTTPError) as error:
            self.post("/api/consent", {"enabled": "yes"})
        self.assertEqual(error.exception.code, 400)

    def test_static_path_traversal_rejected(self):
        for path in ["/../data/scenarios.json", "/assets/../data/scenarios.json", "/assets/unknown.png"]:
            with self.subTest(path=path):
                with self.assertRaises(HTTPError) as error:
                    self.client.open(self.base + path)
                self.assertEqual(error.exception.code, 404)
                error.exception.close()

    def test_readme_logo_is_served_as_original_png(self):
        logo = Path(__file__).resolve().parents[1] / "assets" / "logo-elo-financeiro.png"
        with self.client.open(self.base + "/assets/logo-elo-financeiro.png") as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers["Content-Type"], "image/png")
            self.assertEqual(response.read(), logo.read_bytes())

    # ── T4: stale approval via HTTP ──────────────────────────────────────────
    def test_stale_report_id_returns_400(self):
        state = self.post("/api/consent", {"enabled": True})
        stale_id = state["report"]["report_id"]
        self.post("/api/monitor", {})
        with self.assertRaises(HTTPError) as error:
            self.post("/api/approve", {"report_id": stale_id, "action_id": "budget-plan"})
        self.assertEqual(error.exception.code, 400)
        error.exception.close()

    # ── T5: consent revoke mid-flow via HTTP ──────────────────────────────────
    def test_revoke_consent_then_approve_is_rejected(self):
        state = self.post("/api/consent", {"enabled": True})
        rid = state["report"]["report_id"]
        # Revoke consent
        self.post("/api/consent", {"enabled": False})
        # Attempt approval after revoke — must be rejected with 403
        with self.assertRaises(HTTPError) as error:
            self.post("/api/approve", {"report_id": rid, "action_id": "budget-plan"})
        self.assertEqual(error.exception.code, 403)

    def test_invalid_scenario_name_returns_400(self):
        with self.assertRaises(HTTPError) as error:
            self.post("/api/scenario", {"name": None})
        self.assertEqual(error.exception.code, 400)

    def test_unknown_scenario_name_returns_400(self):
        with self.assertRaises(HTTPError) as error:
            self.post("/api/scenario", {"name": "nonexistent"})
        self.assertEqual(error.exception.code, 400)

    def test_decline_action_records_without_altering_projection(self):
        state = self.post("/api/consent", {"enabled": True})
        rid = state["report"]["report_id"]
        minimum_before = state["report"]["results"]["cashflow"]["minimum_cents"]
        result = self.post("/api/decline", {"report_id": rid, "action_id": "budget-plan"})
        # Projection must remain unchanged
        self.assertEqual(result["report"]["results"]["cashflow"]["minimum_cents"], minimum_before)
        # Decline must appear in history
        declined = [h for h in result["history"] if h.get("status") == "declined"]
        self.assertEqual(len(declined), 1)
        self.assertEqual(declined[0]["action"], "budget-plan")

    def test_decline_stale_report_id_returns_400(self):
        state = self.post("/api/consent", {"enabled": True})
        stale_id = state["report"]["report_id"]
        self.post("/api/monitor", {})
        with self.assertRaises(HTTPError) as error:
            self.post("/api/decline", {"report_id": stale_id, "action_id": "budget-plan"})
        self.assertEqual(error.exception.code, 400)
        error.exception.close()

    def test_decline_without_consent_returns_403(self):
        with self.assertRaises(HTTPError) as error:
            self.post("/api/decline", {"report_id": "any", "action_id": "budget-plan"})
        self.assertEqual(error.exception.code, 403)
        error.exception.close()

    def test_purchase_goal_approval_flow(self):
        """Purchase scenario: approve purchase-goal action via HTTP."""
        self.post("/api/scenario", {"name": "purchase"})
        state = self.post("/api/consent", {"enabled": True})
        rid = state["report"]["report_id"]
        actions = state["report"]["actions"]
        goal_action = next((a for a in actions if a["id"] == "purchase-goal"), None)
        self.assertIsNotNone(goal_action)
        result = self.post("/api/approve", {"report_id": rid, "action_id": "purchase-goal"})
        self.assertEqual(len(result["goals"]), 1)
        self.assertEqual(result["goals"][0]["label"], "Celular")

    # ── Testes do endpoint /api/preview ──────────────────────────────────────

    def test_preview_via_endpoint_returns_projected_minimum(self):
        """Prévia calculada no servidor retorna menor saldo e campos obrigatórios."""
        state = self.post("/api/consent", {"enabled": True})
        rid = state["report"]["report_id"]
        # Obtém total de flexíveis para usar uma redução válida.
        flexible = state["report"]["results"]["cashflow"]["flexible_cents"]
        self.assertGreater(flexible, 0, "Cenário month deve ter gastos flexíveis.")
        reduction = max(1, flexible // 2)
        result = self.post("/api/preview", {"report_id": rid, "reduction_cents": reduction})
        preview = result["preview"]
        self.assertIn("minimum_cents", preview)
        self.assertIn("gap_to_buffer_cents", preview)
        self.assertIn("meets_buffer", preview)
        self.assertIn("flexible_total_cents", preview)
        self.assertEqual(preview["reduction_cents"], reduction)
        # A prévia não deve modificar o orçamento.
        self.assertEqual(
            result["report"]["results"]["cashflow"]["minimum_cents"],
            state["report"]["results"]["cashflow"]["minimum_cents"],
        )

    def test_preview_approval_with_correct_version_applies_custom_reduction(self):
        """Aprovação após prévia aplica a redução personalizada ao orçamento."""
        state = self.post("/api/consent", {"enabled": True})
        rid = state["report"]["report_id"]
        flexible = state["report"]["results"]["cashflow"]["flexible_cents"]
        self.assertGreater(flexible, 0)
        custom_reduction = max(1, flexible // 4)
        # Calcula a prévia.
        preview_state = self.post("/api/preview", {"report_id": rid, "reduction_cents": custom_reduction})
        # Aprova a redução personalizada.
        result = self.post("/api/approve", {
            "report_id": rid, "action_id": "budget-plan",
            "preview_id": preview_state["preview"]["preview_id"],
        })
        # O saldo deve refletir a redução personalizada.
        new_min = result["report"]["results"]["cashflow"]["minimum_cents"]
        original_min = state["report"]["results"]["cashflow"]["minimum_cents"]
        self.assertGreater(new_min, original_min)
        self.assertEqual(new_min, preview_state["preview"]["minimum_cents"])
        self.assertEqual(result["history"][-1]["applied_cents"], custom_reduction)
        # O ajuste pendente deve ter sido limpo.
        self.assertIsNone(result.get("pending_adjustment"))

    def test_preview_rejected_with_stale_report_id(self):
        """Prévia com report_id desatualizado deve retornar 400."""
        state = self.post("/api/consent", {"enabled": True})
        stale_id = state["report"]["report_id"]
        # Atualiza o estado do servidor simulando uma nova despesa.
        self.post("/api/monitor", {})
        with self.assertRaises(HTTPError) as error:
            self.post("/api/preview", {"report_id": stale_id, "reduction_cents": 100})
        self.assertEqual(error.exception.code, 400)
        error.exception.close()

    def test_preview_rejects_invalid_reduction_non_integer(self):
        """Redução com tipo inválido deve retornar 400."""
        state = self.post("/api/consent", {"enabled": True})
        rid = state["report"]["report_id"]
        with self.assertRaises(HTTPError) as error:
            self.post("/api/preview", {"report_id": rid, "reduction_cents": "cem"})
        self.assertEqual(error.exception.code, 400)
        error.exception.close()

    def test_preview_rejects_negative_reduction(self):
        """Redução negativa deve retornar 400."""
        state = self.post("/api/consent", {"enabled": True})
        rid = state["report"]["report_id"]
        with self.assertRaises(HTTPError) as error:
            self.post("/api/preview", {"report_id": rid, "reduction_cents": -1})
        self.assertEqual(error.exception.code, 400)
        error.exception.close()

    def test_preview_rejects_reduction_above_flexible_total(self):
        """Redução acima do total flexível deve retornar 400."""
        state = self.post("/api/consent", {"enabled": True})
        rid = state["report"]["report_id"]
        flexible = state["report"]["results"]["cashflow"]["flexible_cents"]
        with self.assertRaises(HTTPError) as error:
            self.post("/api/preview", {"report_id": rid, "reduction_cents": flexible + 1})
        self.assertEqual(error.exception.code, 400)
        error.exception.close()

    def test_preview_requires_csrf(self):
        """Prévia sem token CSRF válido deve retornar 403."""
        state = self.post("/api/consent", {"enabled": True})
        rid = state["report"]["report_id"]
        with self.assertRaises(HTTPError) as error:
            self.post("/api/preview", {"report_id": rid, "reduction_cents": 100}, token="wrong")
        self.assertEqual(error.exception.code, 403)
        error.exception.close()

    def test_preview_requires_consent(self):
        """Prévia sem consentimento deve retornar 403."""
        state = self.state  # consentimento não foi dado ainda
        rid = state["report"].get("report_id", "noop")
        with self.assertRaises(HTTPError) as error:
            self.post("/api/preview", {"report_id": rid, "reduction_cents": 100})
        self.assertEqual(error.exception.code, 403)
        error.exception.close()

    def test_preview_does_not_modify_budget_before_approval(self):
        """A prévia nunca deve alterar o orçamento sem aprovação explícita."""
        state = self.post("/api/consent", {"enabled": True})
        rid = state["report"]["report_id"]
        flexible = state["report"]["results"]["cashflow"]["flexible_cents"]
        self.assertGreater(flexible, 0)
        min_before = state["report"]["results"]["cashflow"]["minimum_cents"]
        # Calcula a prévia mas não aprova.
        self.post("/api/preview", {"report_id": rid, "reduction_cents": max(1, flexible // 2)})
        # Obtém o estado atual sem novas ações.
        current = self.post("/api/consent", {"enabled": True})
        # O saldo mínimo não deve ter mudado.
        self.assertEqual(current["report"]["results"]["cashflow"]["minimum_cents"], min_before)


    # ── T: /api/preview/discard persiste no servidor ─────────────────────────
    def test_discard_preview_clears_pending_adjustment_on_server(self):
        """POST /api/preview/discard cancela a prévia; estado posterior não deve ter pending_adjustment."""
        state = self.post("/api/consent", {"enabled": True})
        rid = state["report"]["report_id"]
        flexible = state["report"]["results"]["cashflow"]["flexible_cents"]
        self.assertGreater(flexible, 0)
        # Calcula prévia.
        self.post("/api/preview", {"report_id": rid, "reduction_cents": max(1, flexible // 2)})
        # Verifica que existe ajuste pendente.
        mid_state = self.post("/api/consent", {"enabled": True})
        self.assertIsNotNone(mid_state["pending_adjustment"])
        # Descarta no servidor.
        after = self.post("/api/preview/discard", {})
        self.assertIsNone(after["pending_adjustment"])

    def test_discard_preview_survives_state_reload(self):
        """Após descarte, GET /api/state não deve devolver pending_adjustment."""
        state = self.post("/api/consent", {"enabled": True})
        rid = state["report"]["report_id"]
        flexible = state["report"]["results"]["cashflow"]["flexible_cents"]
        self.assertGreater(flexible, 0)
        self.post("/api/preview", {"report_id": rid, "reduction_cents": max(1, flexible // 2)})
        self.post("/api/preview/discard", {})
        import urllib.request
        req = urllib.request.Request(self.base + "/api/state")
        with self.client.open(req) as resp:
            reload_state = json.load(resp)
        self.assertIsNone(reload_state["pending_adjustment"])

    # ── T: versionamento de prévia (two-tab) ─────────────────────────────────
    def test_approve_with_stale_preview_id_returns_400(self):
        """Aprovação com preview_id desatualizado (sobreposição de outra aba) deve retornar 400."""
        state = self.post("/api/consent", {"enabled": True})
        rid = state["report"]["report_id"]
        flexible = state["report"]["results"]["cashflow"]["flexible_cents"]
        self.assertGreater(flexible, 0, "Precisa de gastos flexíveis.")
        # Aba A: gera primeira prévia.
        r1 = self.post("/api/preview", {"report_id": rid, "reduction_cents": max(1, flexible // 4)})
        pid1 = r1["preview"]["preview_id"]
        # Aba B: sobrescreve com segunda prévia.
        self.post("/api/preview", {"report_id": rid, "reduction_cents": max(1, flexible // 2)})
        # Aba A tenta aprovar com preview_id antigo.
        from urllib.error import HTTPError
        with self.assertRaises(HTTPError) as error:
            self.post("/api/approve", {"report_id": rid, "action_id": "budget-plan", "preview_id": pid1})
        self.assertEqual(error.exception.code, 400)
        error.exception.close()

    def test_approve_with_current_preview_id_succeeds(self):
        """Aprovação com preview_id correto (sem sobreposição) deve ser aceita."""
        state = self.post("/api/consent", {"enabled": True})
        rid = state["report"]["report_id"]
        flexible = state["report"]["results"]["cashflow"]["flexible_cents"]
        self.assertGreater(flexible, 0)
        r = self.post("/api/preview", {"report_id": rid, "reduction_cents": max(1, flexible // 2)})
        pid = r["preview"]["preview_id"]
        result = self.post("/api/approve", {"report_id": rid, "action_id": "budget-plan", "preview_id": pid})
        self.assertIsNone(result["pending_adjustment"])
        history = [h for h in result["history"] if h.get("kind") == "custom"]
        self.assertEqual(len(history), 1)

    def test_standard_approval_does_not_apply_pending_custom_reduction(self):
        """O botão padrão aplica o valor mostrado na proposta, mesmo havendo prévia."""
        state = self.post("/api/consent", {"enabled": True})
        rid = state["report"]["report_id"]
        action = next(a for a in state["report"]["actions"] if a["id"] == "budget-plan")
        default_reduction = action["reduction_cents"]
        custom_reduction = max(1, default_reduction // 2)
        self.assertNotEqual(default_reduction, custom_reduction)
        self.post("/api/preview", {"report_id": rid, "reduction_cents": custom_reduction})

        result = self.post("/api/approve", {"report_id": rid, "action_id": "budget-plan"})

        entry = result["history"][-1]
        self.assertEqual(entry["kind"], "default")
        self.assertEqual(entry["applied_cents"], default_reduction)
        self.assertIsNone(entry["preview_id"])
        self.assertIsNone(result["pending_adjustment"])
        self.assertEqual(result["report"]["results"]["cashflow"]["minimum_cents"], action["after_cents"])

    def test_approve_discarded_preview_does_not_fall_back_to_standard(self):
        """Uma aba com prévia descartada não pode aprovar silenciosamente o padrão."""
        state = self.post("/api/consent", {"enabled": True})
        rid = state["report"]["report_id"]
        preview_state = self.post("/api/preview", {"report_id": rid, "reduction_cents": 15000})
        self.post("/api/preview/discard", {})

        with self.assertRaises(HTTPError) as error:
            self.post("/api/approve", {
                "report_id": rid, "action_id": "budget-plan",
                "preview_id": preview_state["preview"]["preview_id"],
            })
        self.assertEqual(error.exception.code, 400)
        error.exception.close()
        with self.client.open(self.base + "/api/state") as response:
            current = json.load(response)
        self.assertEqual(current["report"]["results"]["cashflow"], state["report"]["results"]["cashflow"])
        self.assertFalse(any(h.get("status") == "accepted" for h in current["history"]))

    def test_approve_declined_preview_does_not_fall_back_to_standard(self):
        """A aprovação de uma prévia recusada retorna erro sem aplicar outro valor."""
        state = self.post("/api/consent", {"enabled": True})
        rid = state["report"]["report_id"]
        preview_state = self.post("/api/preview", {"report_id": rid, "reduction_cents": 15000})
        self.post("/api/decline", {"report_id": rid, "action_id": "budget-plan"})

        with self.assertRaises(HTTPError) as error:
            self.post("/api/approve", {
                "report_id": rid, "action_id": "budget-plan",
                "preview_id": preview_state["preview"]["preview_id"],
            })
        self.assertEqual(error.exception.code, 400)
        error.exception.close()
        with self.client.open(self.base + "/api/state") as response:
            current = json.load(response)
        self.assertEqual(current["report"]["results"]["cashflow"], state["report"]["results"]["cashflow"])
        self.assertEqual([h["status"] for h in current["history"]], ["declined"])

    def test_approve_rejects_invalid_preview_ids_without_applying_reduction(self):
        """IDs de prévia devem ser inteiros positivos, sem aceitar booleanos."""
        state = self.post("/api/consent", {"enabled": True})
        rid = state["report"]["report_id"]
        preview_state = self.post("/api/preview", {"report_id": rid, "reduction_cents": 15000})
        for invalid_id in [True, False, 0, -1, 1.5, "1", [], {}]:
            with self.subTest(preview_id=invalid_id):
                with self.assertRaises(HTTPError) as error:
                    self.post("/api/approve", {
                        "report_id": rid, "action_id": "budget-plan", "preview_id": invalid_id,
                    })
                self.assertEqual(error.exception.code, 400)
                error.exception.close()
        with self.client.open(self.base + "/api/state") as response:
            current = json.load(response)
        self.assertEqual(current["pending_adjustment"], preview_state["pending_adjustment"])
        self.assertEqual(current["report"]["results"]["cashflow"], state["report"]["results"]["cashflow"])
        self.assertEqual(current["history"], [])

    def test_monitor_invalidates_preview_and_rejects_it_for_updated_report(self):
        """Dados novos descartam a prévia e impedem reaproveitá-la no relatório novo."""
        state = self.post("/api/consent", {"enabled": True})
        preview_state = self.post("/api/preview", {
            "report_id": state["report"]["report_id"], "reduction_cents": 15000,
        })
        monitored = self.post("/api/monitor", {})
        self.assertIsNone(monitored["pending_adjustment"])

        with self.assertRaises(HTTPError) as error:
            self.post("/api/approve", {
                "report_id": monitored["report"]["report_id"], "action_id": "budget-plan",
                "preview_id": preview_state["preview"]["preview_id"],
            })
        self.assertEqual(error.exception.code, 400)
        error.exception.close()
        with self.client.open(self.base + "/api/state") as response:
            current = json.load(response)
        self.assertEqual(current["report"]["results"]["cashflow"], monitored["report"]["results"]["cashflow"])
        self.assertFalse(any(h.get("status") == "accepted" for h in current["history"]))

    def test_custom_approval_replay_is_idempotent_without_replaying_standard(self):
        """A repetição da mesma prévia é idempotente, sem autorizar outra proposta."""
        state = self.post("/api/consent", {"enabled": True})
        rid = state["report"]["report_id"]
        preview_state = self.post("/api/preview", {"report_id": rid, "reduction_cents": 15000})
        payload = {
            "report_id": rid, "action_id": "budget-plan",
            "preview_id": preview_state["preview"]["preview_id"],
        }
        approved = self.post("/api/approve", payload)
        repeated = self.post("/api/approve", payload)
        self.assertEqual(repeated["history"], approved["history"])
        self.assertEqual(repeated["report"]["results"]["cashflow"], approved["report"]["results"]["cashflow"])
        self.assertEqual(len(repeated["history"]), 1)

        with self.assertRaises(HTTPError) as error:
            self.post("/api/approve", {"report_id": rid, "action_id": "budget-plan"})
        self.assertEqual(error.exception.code, 400)
        error.exception.close()

    # ── T: recusa cancela prévia ──────────────────────────────────────────────
    def test_decline_clears_pending_preview(self):
        """Recusa de budget-plan deve cancelar o ajuste pendente."""
        state = self.post("/api/consent", {"enabled": True})
        rid = state["report"]["report_id"]
        flexible = state["report"]["results"]["cashflow"]["flexible_cents"]
        self.assertGreater(flexible, 0)
        self.post("/api/preview", {"report_id": rid, "reduction_cents": max(1, flexible // 2)})
        result = self.post("/api/decline", {"report_id": rid, "action_id": "budget-plan"})
        self.assertIsNone(result["pending_adjustment"])

    # ── T: histórico distingue kind ───────────────────────────────────────────
    def test_history_kind_default_on_standard_approval(self):
        """Aprovação padrão (sem prévia) registra kind=default no histórico."""
        state = self.post("/api/consent", {"enabled": True})
        rid = state["report"]["report_id"]
        result = self.post("/api/approve", {"report_id": rid, "action_id": "budget-plan"})
        entry = next((h for h in result["history"] if h.get("action") == "budget-plan"), None)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["kind"], "default")
        self.assertIsNotNone(entry["applied_cents"])

    def test_history_kind_declined_on_decline(self):
        """Recusa registra kind=declined e applied_cents=None no histórico."""
        state = self.post("/api/consent", {"enabled": True})
        rid = state["report"]["report_id"]
        result = self.post("/api/decline", {"report_id": rid, "action_id": "budget-plan"})
        entry = next((h for h in result["history"] if h.get("action") == "budget-plan"), None)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["kind"], "declined")
        self.assertIsNone(entry["applied_cents"])


if __name__ == "__main__":
    unittest.main()
