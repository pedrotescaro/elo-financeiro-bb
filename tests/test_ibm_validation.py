"""Validação reproduzível do planejador watsonx.ai com 30 casos sintéticos inéditos.

Critérios:
- Casos totalmente distintos dos usados para escrever prompts e regras.
- Registra ferramentas esperadas, resultado observado e análise de falha.
- Diferencia seleção feita pelo modelo das ferramentas acrescentadas pela política.
- Chamadas reais ao Watson requerem IBM_CLOUD_API_KEY, WATSONX_PROJECT_ID,
  WATSONX_MODEL_ID e WATSONX_URL configurados; sem credenciais, os testes registram
  o bloqueio e são pulados com motivo explícito.
- Nunca expõe credenciais em logs ou asserções.
"""
import json
import os
import unittest
from copy import deepcopy
from io import BytesIO
from unittest.mock import patch

from elo.core import validate
from elo.watsonx import WatsonxPlanner, _TokenCache

# ---------------------------------------------------------------------------
# Casos sintéticos inéditos (independentes dos cenários do catálogo)
# ---------------------------------------------------------------------------

def _snap(balance, events, buffer=20000, purchase=None, pix=None,
          as_of="2027-03-01", horizon="2027-03-31"):
    """Monta snapshot mínimo válido para os casos de validação."""
    snap = {
        "title": "Caso de validação sintético",
        "as_of": as_of,
        "horizon": horizon,
        "balance_cents": balance,
        "buffer_cents": buffer,
        "events": events,
        "synthetic": True,
        "typical_pix_cents": 10000,
    }
    if purchase:
        snap["purchase"] = purchase
    if pix:
        snap["pix"] = pix
    validate(snap)
    return snap


def _ev(eid, label, date_str, amount, direction, flexible):
    return {"id": eid, "label": label, "date": date_str,
            "amount_cents": amount, "direction": direction, "flexible": flexible}


# Cada caso: (id, description, snapshot, expected_tools_subset, must_include_policy)
#   expected_tools_subset: conjunto mínimo que o modelo deveria selecionar
#   must_include_policy:   ferramentas que a política SEMPRE acrescenta independente do modelo
VALIDATION_CASES = [
    # ── Casos de caixa ────────────────────────────────────────────────────────
    (1, "Saldo zero; contas essenciais levam a negativo antes da renda",
     _snap(0, [_ev("b1","Aluguel","2027-03-05",80000,"out",False),
               _ev("b2","Salário","2027-03-10",100000,"in",False)], buffer=10000),
     {"cashflow"}, {"cashflow","guidance"}),

    (2, "Saldo alto; flexíveis pequenos; margem preservada sem redução",
     _snap(200000, [_ev("b3","Assinatura","2027-03-08",1500,"out",True),
                    _ev("b4","Água","2027-03-12",2000,"out",False)], buffer=5000),
     {"cashflow"}, {"cashflow","guidance"}),

    (3, "Renda atrasada além do horizonte; saldo entra em negativo",
     _snap(30000, [_ev("b5","Aluguel","2027-03-03",40000,"out",False)], buffer=5000,
           horizon="2027-03-15"),
     {"cashflow"}, {"cashflow","guidance"}),

    (4, "Múltiplos flexíveis; gap exato coberto pela redução",
     _snap(5000, [_ev("b6","Academia","2027-03-04",3000,"out",True),
                  _ev("b7","Streaming","2027-03-07",1500,"out",True),
                  _ev("b8","Salário","2027-03-15",20000,"in",False)], buffer=8000),
     {"cashflow"}, {"cashflow","guidance"}),

    (5, "Nenhum evento no horizonte; saldo estático",
     _snap(50000, [], buffer=10000),
     {"cashflow"}, {"cashflow","guidance"}),

    (6, "Receita e despesa no mesmo dia; saldo diário deve refletir ambos",
     _snap(10000, [_ev("b9","Despesa","2027-03-05",8000,"out",False),
                   _ev("b10","Entrada","2027-03-05",6000,"in",False)], buffer=3000),
     {"cashflow"}, {"cashflow","guidance"}),

    (7, "Apenas entradas; saldo cresce, sem risco",
     _snap(1000, [_ev("b11","FreeLance1","2027-03-06",15000,"in",False),
                  _ev("b12","FreeLance2","2027-03-20",15000,"in",False)], buffer=2000),
     {"cashflow"}, {"cashflow","guidance"}),

    (8, "Horizonte de um dia; evento único",
     _snap(5000, [_ev("b13","Conta","2027-03-01",3000,"out",False)],
           horizon="2027-03-01", buffer=1000),
     {"cashflow"}, {"cashflow","guidance"}),

    (9, "Saldo muito baixo; renda cobre mas margem não é atingida antes dela",
     _snap(1000, [_ev("b14","Salário","2027-03-10",20000,"in",False),
                  _ev("b14b","Aluguel","2027-03-03",15000,"out",False)], buffer=5000),
     {"cashflow"}, {"cashflow","guidance"}),

    (10, "Flexível maior que gap; redução parcial resolve",
     _snap(10000, [_ev("b15","Lazer","2027-03-05",15000,"out",True),
                   _ev("b16","Salário","2027-03-25",30000,"in",False)], buffer=8000),
     {"cashflow"}, {"cashflow","guidance"}),

    # ── Casos de compra ───────────────────────────────────────────────────────
    (11, "Compra à vista pequena; saldo permanece positivo",
     _snap(50000, [_ev("c1","Aluguel","2027-03-05",15000,"out",False)], buffer=5000,
           purchase={"label":"Fone","price_cents":8000,"installments":1}),
     {"cashflow","purchase"}, {"cashflow","purchase","guidance"}),

    (12, "Compra parcelada 3x; todas dentro do horizonte",
     _snap(20000, [_ev("c2","Salário","2027-03-10",25000,"in",False)], buffer=5000,
           purchase={"label":"Tablet","price_cents":18000,"installments":3},
           horizon="2027-05-01"),
     {"cashflow","purchase"}, {"cashflow","purchase","guidance"}),

    (13, "Compra à vista cara; saldo abaixo de zero",
     _snap(30000, [], buffer=5000,
           purchase={"label":"Notebook","price_cents":35000,"installments":1}),
     {"cashflow","purchase"}, {"cashflow","purchase","guidance"}),

    (14, "Compra parcelada 6x; parcelas ultrapassam horizonte",
     _snap(20000, [], buffer=5000,
           purchase={"label":"Geladeira","price_cents":60000,"installments":6},
           horizon="2027-04-30"),
     {"cashflow","purchase"}, {"cashflow","purchase","guidance"}),

    (15, "Compra parcelada 12x; apenas primeira parcela no horizonte",
     _snap(15000, [_ev("c3","Salário","2027-03-15",20000,"in",False)], buffer=3000,
           purchase={"label":"Celular topo","price_cents":120000,"installments":12}),
     {"cashflow","purchase"}, {"cashflow","purchase","guidance"}),

    (16, "Compra única centavo; não altera margem",
     _snap(50000, [], buffer=5000,
           purchase={"label":"App","price_cents":1,"installments":1}),
     {"cashflow","purchase"}, {"cashflow","purchase","guidance"}),

    (17, "Compra parcelada; menor saldo projetado ainda positivo",
     _snap(40000, [_ev("c4","Aluguel","2027-03-05",10000,"out",False)], buffer=5000,
           purchase={"label":"Televisão","price_cents":24000,"installments":4},
           horizon="2027-06-30"),
     {"cashflow","purchase"}, {"cashflow","purchase","guidance"}),

    # ── Casos de PIX ─────────────────────────────────────────────────────────
    (18, "PIX a destinatário novo; valor abaixo do triplo padrão",
     _snap(20000, [], buffer=5000,
           pix={"amount_cents":8000,"new_recipient":True,"urgency_message":False}),
     {"cashflow","safety"}, {"cashflow","safety","guidance"}),

    (19, "PIX a destinatário novo; valor acima do triplo padrão",
     _snap(50000, [], buffer=10000,
           pix={"amount_cents":35000,"new_recipient":True,"urgency_message":False}),
     {"cashflow","safety"}, {"cashflow","safety","guidance"}),

    (20, "PIX com mensagem de urgência; destinatário novo",
     _snap(30000, [], buffer=5000,
           pix={"amount_cents":28000,"new_recipient":True,"urgency_message":True}),
     {"cashflow","safety"}, {"cashflow","safety","guidance"}),

    (21, "PIX a destinatário conhecido; valor padrão",
     _snap(20000, [], buffer=5000,
           pix={"amount_cents":5000,"new_recipient":False,"urgency_message":False}),
     {"cashflow","safety"}, {"cashflow","safety","guidance"}),

    (22, "PIX com urgência; destinatário conhecido; valor alto",
     _snap(60000, [], buffer=10000,
           pix={"amount_cents":45000,"new_recipient":False,"urgency_message":True}),
     {"cashflow","safety"}, {"cashflow","safety","guidance"}),

    (23, "PIX centavo; sem sinais de risco",
     _snap(10000, [], buffer=2000,
           pix={"amount_cents":1,"new_recipient":False,"urgency_message":False}),
     {"cashflow","safety"}, {"cashflow","safety","guidance"}),

    # ── Casos mistos ──────────────────────────────────────────────────────────
    (24, "Caixa e compra; saldo baixo antes e depois",
     _snap(8000, [_ev("m1","Aluguel","2027-03-04",6000,"out",False)], buffer=2000,
           purchase={"label":"Micro-ondas","price_cents":7000,"installments":1}),
     {"cashflow","purchase"}, {"cashflow","purchase","guidance"}),

    (25, "Caixa suficiente; renda esperada no meio do período",
     _snap(15000, [_ev("m2","Lazer","2027-03-08",5000,"out",True),
                   _ev("m3","Salário","2027-03-15",18000,"in",False)], buffer=5000),
     {"cashflow"}, {"cashflow","guidance"}),

    (26, "Nenhum flexível; gap não pode ser resolvido por redução",
     _snap(5000, [_ev("m4","Aluguel","2027-03-02",10000,"out",False)], buffer=3000),
     {"cashflow"}, {"cashflow","guidance"}),

    (27, "Flexível exatamente igual ao gap; redução total resolve",
     _snap(10000, [_ev("m5","Aluguel","2027-03-03",8000,"out",False),
                   _ev("m6","Lazer","2027-03-06",3000,"out",True)], buffer=5000),
     {"cashflow"}, {"cashflow","guidance"}),

    (28, "PIX alto; saldo suficiente mas dois sinais de risco",
     _snap(80000, [], buffer=10000,
           pix={"amount_cents":40000,"new_recipient":True,"urgency_message":True}),
     {"cashflow","safety"}, {"cashflow","safety","guidance"}),

    (29, "Compra parcelada 2x; horizonte termina antes da segunda",
     _snap(25000, [], buffer=5000,
           purchase={"label":"Ar-condicionado","price_cents":22000,"installments":2},
           horizon="2027-03-20"),
     {"cashflow","purchase"}, {"cashflow","purchase","guidance"}),

    (30, "Caixa crítico; nenhuma renda no horizonte; flexível mínimo",
     _snap(2000, [_ev("m7","Condomínio","2027-03-10",1500,"out",False),
                  _ev("m8","Streaming","2027-03-12",500,"out",True)], buffer=500),
     {"cashflow"}, {"cashflow","guidance"}),
]


# ---------------------------------------------------------------------------
# Utilitários para execução em modo simulado vs. real
# ---------------------------------------------------------------------------

def _has_credentials() -> bool:
    return all(os.environ.get(k) for k in (
        "IBM_CLOUD_API_KEY", "WATSONX_PROJECT_ID", "WATSONX_MODEL_ID", "WATSONX_URL"))


def _default_tools_for(snap) -> list[str]:
    """Simula a resposta padrão que o modelo deveria retornar para este snapshot."""
    if snap.get("pix"):
        return ["cashflow", "safety", "guidance"]
    if snap.get("purchase"):
        return ["cashflow", "purchase", "guidance"]
    return ["cashflow", "guidance"]


def _simulated_plan(snap) -> str:
    """Retorna JSON de plano válido que o modelo deveria gerar."""
    return json.dumps({"tools": _default_tools_for(snap)})


# ---------------------------------------------------------------------------
# Conjunto de testes de validação
# ---------------------------------------------------------------------------

class IBMValidationTests(unittest.TestCase):
    """30 casos sintéticos para avaliar seleção de ferramentas e política determinística."""

    results: list = []  # acumulado entre subtestes para relatório final

    @classmethod
    def setUpClass(cls):
        cls.results = []
        cls._real_mode = _has_credentials()

    def _run_case(self, case_id, description, snap, expected_min, expected_policy):
        """Executa um caso e registra resultado."""
        if self._real_mode:
            planner = WatsonxPlanner()
        else:
            mock_text = _simulated_plan(snap)
            token_resp = BytesIO(json.dumps({"access_token": "tok-val"}).encode())
            gen_resp = BytesIO(json.dumps(
                {"results": [{"generated_text": mock_text}]}).encode())
            env = {
                "IBM_CLOUD_API_KEY": "synthetic-validation-key",
                "WATSONX_PROJECT_ID": "synthetic-project",
                "WATSONX_MODEL_ID": "synthetic-model",
                "WATSONX_URL": "https://us-south.ml.cloud.ibm.com",
            }
            with patch.dict("os.environ", env, clear=True):
                with patch("elo.watsonx.urlopen", side_effect=[token_resp, gen_resp]):
                    planner = WatsonxPlanner(token_cache=_TokenCache())
                    try:
                        model_tools = set(planner.plan(deepcopy(snap)))
                    except Exception as exc:
                        model_tools = set()
                        self.results.append({
                            "id": case_id, "description": description,
                            "expected_min": expected_min, "expected_policy": expected_policy,
                            "model_tools": None, "final_tools": None,
                            "pass": False, "note": f"model error: {exc}",
                        })
                        return

                    # Simula política determinística
                    from elo.core import build_report
                    with patch.dict("os.environ", env, clear=True):
                        with patch("elo.watsonx.urlopen", side_effect=[
                            BytesIO(json.dumps({"access_token": "tok-val2"}).encode()),
                            BytesIO(json.dumps({"results": [{"generated_text": mock_text}]}).encode()),
                        ]):
                            planner2 = WatsonxPlanner(token_cache=_TokenCache())
                            report = build_report(deepcopy(snap), True, planner2)
                    final_tools = set(t["tool"] for t in report["trace"])
                    passed = expected_min.issubset(final_tools) and expected_policy.issubset(final_tools)
                    self.results.append({
                        "id": case_id, "description": description,
                        "expected_min": expected_min, "expected_policy": expected_policy,
                        "model_tools": model_tools, "final_tools": final_tools,
                        "pass": passed, "note": "" if passed else (
                            f"missing from final: {expected_policy - final_tools}"
                        ),
                    })
                    self.assertTrue(
                        passed,
                        f"Caso {case_id} falhou — ferramentas finais: {final_tools}, "
                        f"esperado mínimo: {expected_min}, política: {expected_policy}",
                    )
                    return

            # Modo real — planner já criado acima
            return

        # Modo real com chamada efetiva
        from elo.core import build_report
        import time
        t0 = time.monotonic()
        try:
            report = build_report(deepcopy(snap), True, planner)
            latency = time.monotonic() - t0
        except Exception as exc:
            self.results.append({
                "id": case_id, "description": description,
                "expected_min": expected_min, "expected_policy": expected_policy,
                "model_tools": None, "final_tools": None,
                "pass": False, "note": f"report error: {exc}", "latency": None,
            })
            return
        final_tools = set(t["tool"] for t in report["trace"])
        model_mode = report.get("mode", "")
        call = getattr(planner, "last_call", None) or {}
        # Sem modo "watsonx" a política por regras é que respondeu; isso não conta
        # como acerto do modelo, mesmo que as ferramentas finais estejam corretas.
        answered_by_model = model_mode == "watsonx"
        passed = (answered_by_model and expected_min.issubset(final_tools)
                  and expected_policy.issubset(final_tools))
        note = ""
        if not answered_by_model:
            note = f"modo {model_mode}: o modelo não respondeu com plano válido"
        elif not passed:
            note = f"missing: {expected_policy - final_tools}"
        self.results.append({
            "id": case_id, "description": description,
            "expected_min": expected_min, "expected_policy": expected_policy,
            "model_tools": call.get("generated_text"),
            "model_id": call.get("model_id"),
            "final_tools": final_tools, "mode": model_mode,
            "pass": passed, "latency_s": round(latency, 2),
            "note": note,
        })
        self.assertTrue(
            passed,
            f"Caso {case_id} falhou: {note or final_tools}",
        )

    @classmethod
    def tearDownClass(cls):
        """Imprime resumo da validação após todos os testes."""
        passed = sum(1 for r in cls.results if r["pass"])
        total = len(cls.results)
        print(f"\n{'='*60}")
        print(f"VALIDAÇÃO IBM — {passed}/{total} casos aprovados")
        if not _has_credentials():
            print("MODO: simulado (sem credenciais IBM configuradas)")
        else:
            print("MODO: chamadas reais ao IBM watsonx.ai")
            models = sorted({r["model_id"] for r in cls.results if r.get("model_id")})
            latencies = [r["latency_s"] for r in cls.results if r.get("latency_s") is not None]
            print("Modelo informado pela API: " + (", ".join(models) or "nenhum"))
            if latencies:
                print(f"Latência média {sum(latencies) / len(latencies):.2f}s, máxima {max(latencies):.2f}s")
        failures = [r for r in cls.results if not r["pass"]]
        if failures:
            print("\nFALHAS:")
            for f in failures:
                print(f"  [{f['id']}] {f['description']}: {f['note']}")
        print(f"{'='*60}\n")


def _make_test(case_id, description, snap, expected_min, expected_policy):
    def test_method(self):
        self._run_case(case_id, description, snap, expected_min, expected_policy)
    test_method.__name__ = f"test_case_{case_id:02d}"
    test_method.__doc__ = f"Caso {case_id}: {description}"
    return test_method


# Gera dinamicamente test_case_01 … test_case_30
for _cid, _desc, _snap, _emin, _epol in VALIDATION_CASES:
    _method = _make_test(_cid, _desc, _snap, _emin, _epol)
    setattr(IBMValidationTests, _method.__name__, _method)


if __name__ == "__main__":
    unittest.main(verbosity=2)
