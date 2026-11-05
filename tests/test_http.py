import http.cookiejar
import json
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import Request, build_opener, HTTPCookieProcessor
from elo.server import DemoServer


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = DemoServer(("127.0.0.1", 0))
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
        with self.assertRaises(HTTPError) as error:
            self.client.open(self.base + "/../data/scenarios.json")
        self.assertEqual(error.exception.code, 404)

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
        self.post("/api/preview", {"report_id": rid, "reduction_cents": custom_reduction})
        # Aprova a redução personalizada.
        result = self.post("/api/approve", {"report_id": rid, "action_id": "budget-plan"})
        # O saldo deve refletir a redução personalizada.
        new_min = result["report"]["results"]["cashflow"]["minimum_cents"]
        original_min = state["report"]["results"]["cashflow"]["minimum_cents"]
        self.assertGreater(new_min, original_min)
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


if __name__ == "__main__":
    unittest.main()
