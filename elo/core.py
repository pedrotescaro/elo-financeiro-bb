"""Ferramentas financeiras determinísticas e coordenador de escopo limitado.

Valores são centavos inteiros. O modelo seleciona ferramentas; não calcula
saldos, aprova ações nem estabelece a validade de uma movimentação bancária.
"""
from copy import deepcopy
from datetime import date
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = json.loads((ROOT / "data/scenarios.json").read_text(encoding="utf-8"))
TOOLS = ("cashflow", "purchase", "safety", "guidance")


def load_scenario(name):
    if name not in CATALOG:
        raise ValueError("Cenário desconhecido.")
    return deepcopy(CATALOG[name])


def amount(value):
    if type(value) is not int or value < 0 or value > 100_000_000:
        raise ValueError("Valor financeiro inválido.")
    return value


def validate(snapshot):
    start = date.fromisoformat(snapshot["as_of"])
    horizon = date.fromisoformat(snapshot["horizon"])
    if horizon < start:
        raise ValueError("Horizonte inválido.")
    for field in ("balance_cents", "buffer_cents"):
        amount(snapshot[field])
    ids = set()
    for event in snapshot["events"]:
        amount(event["amount_cents"])
        if not start <= date.fromisoformat(event["date"]) <= horizon:
            raise ValueError("Evento fora do horizonte.")
        if event["direction"] not in ("in", "out"):
            raise ValueError("Direção inválida.")
        if event["id"] in ids:
            raise ValueError("Evento duplicado.")
        ids.add(event["id"])
    return snapshot


def cashflow(snapshot):
    """Agrupa o fechamento diário. Não estima horários de liquidação."""
    validate(snapshot)
    balance = snapshot["balance_cents"]
    rows = [{"date": snapshot["as_of"], "balance_cents": balance, "events": []}]
    days = sorted({e["date"] for e in snapshot["events"]})
    for day in days:
        events = [e for e in snapshot["events"] if e["date"] == day]
        for event in events:
            balance += event["amount_cents"] * (1 if event["direction"] == "in" else -1)
        rows.append({"date": day, "balance_cents": balance,
                     "events": [e["label"] for e in events]})
    low = min(rows, key=lambda r: r["balance_cents"])
    negative = next((r["date"] for r in rows if r["balance_cents"] < 0), None)
    flexible = sum(e["amount_cents"] for e in snapshot["events"]
                   if e["direction"] == "out" and e.get("flexible", False))
    needed = max(0, snapshot["buffer_cents"] - low["balance_cents"])
    return {"daily": rows, "minimum_cents": low["balance_cents"],
            "minimum_date": low["date"], "first_negative_date": negative,
            "closing_cents": balance, "buffer_cents": snapshot["buffer_cents"],
            "gap_to_buffer_cents": needed, "flexible_cents": flexible,
            "uncertainty": "Estimativa por fechamento diário; recebimentos podem atrasar e novas despesas podem surgir."}


def purchase(snapshot):
    item = snapshot.get("purchase")
    if not item:
        return {"available": False}
    price = amount(item["price_cents"])
    installments = item["installments"]
    if type(installments) is not int or not 1 <= installments <= 60:
        raise ValueError("Número de parcelas inválido.")
    base = cashflow(snapshot)
    # Cenário informado sem juros, inclui valores exatos das parcelas.
    first = price // installments + (1 if price % installments else 0)
    return {"available": True, "label": item["label"], "price_cents": price,
            "cash_minimum_cents": base["minimum_cents"] - price,
            "cash_closing_cents": base["closing_cents"] - price,
            "installments": installments, "first_installment_cents": first,
            "installment_minimum_cents": base["minimum_cents"] - first,
            "assumption": "Primeira parcela hoje; sem juros no exemplo. As demais parcelas não foram projetadas neste horizonte.",
            "recommendation": "Adiar e criar uma meta" if base["minimum_cents"] - price < snapshot["buffer_cents"] else "Comparar antes de decidir"}


def safety(snapshot):
    operation = snapshot.get("pix")
    if not operation:
        return {"available": False}
    amount(operation["amount_cents"])
    reasons = []
    if operation.get("new_recipient"):
        reasons.append("Destinatário novo neste cenário.")
    if operation["amount_cents"] > snapshot["typical_pix_cents"] * 3:
        reasons.append("Valor superior a três vezes o padrão sintético informado.")
    # Sinais da simulação, não classificadores de fraude validados.
    if operation.get("urgency_message"):
        reasons.append("A mensagem do cenário exige urgência.")
    return {"available": True, "signal_level": "atenção reforçada" if len(reasons) >= 2 else "atenção habitual",
            "reasons": reasons, "amount_cents": operation["amount_cents"],
            "recommendation": "Verifique o destinatário por um canal independente antes de decidir.",
            "limitation": "Sinais ilustrativos não provam fraude. Ausência de sinais não garante segurança.",
            "payment_executed": False}


def guidance(snapshot):
    knowledge = json.loads((ROOT / "data/knowledge.json").read_text(encoding="utf-8"))
    topic = "pix" if snapshot.get("pix") else "cashflow"
    return {"topic": topic, "documents": [d for d in knowledge if topic in d["topics"]],
            "retrieval_mode": "Busca local por tópico em conteúdo curado; RAG semântico ainda não implementado."}


def apply_saving(snapshot, reduction):
    """Ajusta apenas previsões flexíveis, sem alterar transações realizadas."""
    changed = deepcopy(snapshot)
    remaining = amount(reduction)
    for event in sorted(changed["events"], key=lambda e: e["date"]):
        if event["direction"] == "out" and event.get("flexible", False):
            part = min(event["amount_cents"], remaining)
            event["amount_cents"] -= part
            remaining -= part
    if remaining:
        raise ValueError("Redução superior às despesas flexíveis.")
    return changed


def build_report(snapshot, consent, planner=None):
    if consent is not True:
        return {"status": "consent_required", "title": "Você controla o acesso",
                "message": "Autorize a leitura dos dados sintéticos para iniciar a demonstração.",
                "trace": [], "actions": []}
    validate(snapshot)
    digest = sha256(json.dumps(snapshot, sort_keys=True).encode()).hexdigest()[:20]
    mode, warning = "demo_rules", None
    selected = ["cashflow", "purchase" if snapshot.get("purchase") else "safety" if snapshot.get("pix") else "guidance"]
    if planner:
        try:
            selected = planner.plan(snapshot)
            mode = "watsonx"
        except Exception:
            # Não retorna prompts, chaves ou respostas HTTP ao navegador.
            warning = "O planejador IBM não respondeu com um plano válido. Demonstração por regras ativada."
            mode = "demo_fallback"
    selected = [name for name in dict.fromkeys(selected) if name in TOOLS]
    # Política exige análise de caixa e segurança quando há uma operação.
    if "cashflow" not in selected:
        selected.insert(0, "cashflow")
    if snapshot.get("pix") and "safety" not in selected:
        selected.append("safety")
    if snapshot.get("purchase") and "purchase" not in selected:
        selected.append("purchase")
    trace, result = [], {}
    for name in selected:
        result[name] = globals()[name](snapshot)
        trace.append({"role": {"cashflow": "Agente de Caixa", "purchase": "Agente de Planejamento",
                               "safety": "Agente de Segurança", "guidance": "Consulta de orientações"}[name],
                      "tool": name, "status": "completed"})
    flow = result["cashflow"]
    saving = min(flow["gap_to_buffer_cents"], flow["flexible_cents"])
    actions = []
    if saving:
        projected = cashflow(apply_saving(snapshot, saving))
        actions.append({"id": "budget-plan", "label": "Ativar plano de gastos",
                        "reduction_cents": saving, "before_cents": flow["minimum_cents"],
                        "after_cents": projected["minimum_cents"],
                        "meets_buffer": projected["minimum_cents"] >= flow["buffer_cents"],
                        "effect": "Registra um plano e ajusta a previsão de despesas flexíveis; não bloqueia compras nem movimenta dinheiro."})
    if snapshot.get("purchase"):
        actions.append({"id": "purchase-goal", "label": "Criar meta de compra",
                        "target_cents": snapshot["purchase"]["price_cents"],
                        "effect": "Registra uma meta demonstrativa; não transfere nem reserva dinheiro."})
    if snapshot.get("pix"):
        title = "Uma pausa para verificar pode proteger sua decisão"
    elif flow["first_negative_date"]:
        title = "Seu saldo pode ficar negativo antes do próximo recebimento"
    elif flow["minimum_cents"] < flow["buffer_cents"]:
        title = "Sua margem de segurança pode ficar pequena"
    else:
        title = "Acompanhe sua margem antes de decidir"
    return {"status": "ready", "report_id": digest, "mode": mode, "warning": warning,
            "title": title, "as_of": snapshot["as_of"], "horizon": snapshot["horizon"],
            "results": result, "actions": actions, "trace": trace,
            "estimated": True, "policy_version": "demo-1"}
