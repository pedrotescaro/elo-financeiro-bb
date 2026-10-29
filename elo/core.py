"""Ferramentas financeiras determinísticas e coordenador de escopo limitado.

Valores são centavos inteiros. O modelo seleciona ferramentas; não calcula
saldos, aprova ações nem estabelece a validade de uma movimentação bancária.
"""
import calendar
from copy import deepcopy
from datetime import date, timedelta
from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlsplit
from .retrieval import LocalRetriever

ROOT = Path(__file__).resolve().parent.parent
CATALOG: dict = json.loads((ROOT / "data/scenarios.json").read_text(encoding="utf-8"))
KNOWLEDGE: list = json.loads((ROOT / "data/knowledge.json").read_text(encoding="utf-8"))
_RETRIEVER = LocalRetriever(KNOWLEDGE)
TOOLS: frozenset = frozenset(("cashflow", "purchase", "safety", "guidance"))
_TOOL_ORDER = ("cashflow", "purchase", "safety", "guidance")

# URL schemes allowed in curated knowledge documents.
_SAFE_SCHEMES = frozenset(("http", "https"))


def load_scenario(name: str) -> dict:
    """Retorna uma cópia profunda do cenário solicitado ou levanta ValueError."""
    if not isinstance(name, str) or not 1 <= len(name) <= 40:
        raise ValueError("Nome de cenário inválido.")
    if name not in CATALOG:
        raise ValueError("Cenário desconhecido.")
    return deepcopy(CATALOG[name])


def amount(value: object) -> int:
    """Valida e retorna um valor financeiro em centavos inteiros."""
    if type(value) is not int or value < 0 or value > 100_000_000:
        raise ValueError("Valor financeiro inválido.")
    return value


def validate(snapshot: dict) -> dict:
    """Valida estrutura e intervalos do snapshot; levanta ValueError em caso de falha."""
    start = date.fromisoformat(snapshot["as_of"])
    horizon = date.fromisoformat(snapshot["horizon"])
    if horizon < start or (horizon - start).days > 366:
        raise ValueError("Horizonte inválido.")
    for field in ("balance_cents", "buffer_cents"):
        amount(snapshot[field])
    ids: set = set()
    for event in snapshot["events"]:
        amount(event["amount_cents"])
        if date.fromisoformat(event["date"]) < start:
            raise ValueError("Evento anterior ao início da projeção.")
        if event["direction"] not in ("in", "out"):
            raise ValueError("Direção inválida.")
        if type(event.get("flexible")) is not bool:
            raise ValueError("Campo 'flexible' deve ser booleano.")
        if event["id"] in ids:
            raise ValueError("Evento duplicado.")
        ids.add(event["id"])
    return snapshot


def cashflow(snapshot: dict) -> dict:
    """Agrupa o fechamento diário. Não estima horários de liquidação."""
    validate(snapshot)
    balance = snapshot["balance_cents"]
    rows = []
    start = date.fromisoformat(snapshot["as_of"])
    horizon = date.fromisoformat(snapshot["horizon"])
    # Um fechamento por dia, inclusive dias sem eventos e a data inicial.
    for offset in range((horizon - start).days + 1):
        day = (start + timedelta(days=offset)).isoformat()
        events = [e for e in snapshot["events"] if e["date"] == day]
        for event in events:
            balance += event["amount_cents"] * (1 if event["direction"] == "in" else -1)
        rows.append({"date": day, "balance_cents": balance,
                     "events": [e["label"] for e in events]})
    low = min(rows, key=lambda r: r["balance_cents"])
    negative = next((r["date"] for r in rows if r["balance_cents"] < 0), None)
    flexible = sum(e["amount_cents"] for e in snapshot["events"]
                   if e["direction"] == "out" and e["flexible"] and e["date"] <= snapshot["horizon"])
    needed = max(0, snapshot["buffer_cents"] - low["balance_cents"])
    return {"daily": rows, "initial_cents": snapshot["balance_cents"], "minimum_cents": low["balance_cents"],
            "minimum_date": low["date"], "first_negative_date": negative,
            "closing_cents": balance, "buffer_cents": snapshot["buffer_cents"],
            "gap_to_buffer_cents": needed, "flexible_cents": flexible,
            "uncertainty": "Estimativa por fechamento diário; recebimentos podem atrasar e novas despesas podem surgir."}


def _installment_dates(start: date, n: int) -> list[date]:
    """Retorna n datas mensais a partir de start, preservando o dia sempre que possível.

    Quando o dia não existir no mês destino, usa o último dia daquele mês.
    """
    ref_day = start.day
    dates = [start]
    for i in range(1, n):
        year = start.year + (start.month - 1 + i) // 12
        month = (start.month - 1 + i) % 12 + 1
        last = calendar.monthrange(year, month)[1]
        dates.append(date(year, month, min(ref_day, last)))
    return dates


def _split_installments(price: int, n: int) -> list[int]:
    """Distribui price em n parcelas inteiras; os centavos restantes vão para as primeiras."""
    base, remainder = divmod(price, n)
    return [base + (1 if i < remainder else 0) for i in range(n)]


def purchase(snapshot: dict) -> dict:
    """Compara impacto à vista e parcelas projetadas. Não executa nenhuma compra."""
    item = snapshot.get("purchase")
    if not item:
        return {"available": False}
    price = amount(item["price_cents"])
    installments = item["installments"]
    if type(installments) is not int or not 1 <= installments <= 60:
        raise ValueError("Número de parcelas inválido.")
    base = cashflow(snapshot)
    as_of = date.fromisoformat(snapshot["as_of"])
    horizon = date.fromisoformat(snapshot["horizon"])

    # Calcula datas e valores de todas as parcelas.
    dates = _installment_dates(as_of, installments)
    values = _split_installments(price, installments)

    # Separa parcelas dentro e fora do horizonte.
    schedule = [
        {"date": d.isoformat(), "amount_cents": v, "number": i + 1}
        for i, (d, v) in enumerate(zip(dates, values))
        if d <= horizon
    ]
    out_of_horizon = installments - len(schedule)

    # Projeta o menor saldo com todas as parcelas incluídas no horizonte.
    projected_snapshot = deepcopy(snapshot)
    for entry in schedule:
        projected_snapshot["events"].append({
            "id": f"__installment_{entry['number']}",
            "date": entry["date"],
            "label": f"Parcela {entry['number']}/{installments} – {item['label']}",
            "amount_cents": entry["amount_cents"],
            "direction": "out",
            "flexible": False,
        })
    projected = cashflow(projected_snapshot)

    first_value = values[0]
    return {
        "available": True,
        "label": item["label"],
        "price_cents": price,
        "cash_minimum_cents": base["minimum_cents"] - price,
        "cash_closing_cents": base["closing_cents"] - price,
        "installments": installments,
        "first_installment_cents": first_value,
        "installment_minimum_cents": base["minimum_cents"] - first_value,
        "installment_projected_minimum_cents": projected["minimum_cents"],
        "installment_projected_closing_cents": projected["closing_cents"],
        "schedule": schedule,
        "out_of_horizon": out_of_horizon,
        "assumption": (
            "Primeira parcela em " + as_of.isoformat() + "; sem juros no exemplo. "
            + ("Todas as parcelas estão dentro do horizonte analisado."
               if out_of_horizon == 0
               else f"{out_of_horizon} parcela(s) fora do horizonte não foram incluídas no cálculo do menor saldo.")
        ),
        "recommendation": (
            "Adiar e criar uma meta"
            if projected["minimum_cents"] < snapshot["buffer_cents"]
            else "Comparar antes de decidir"
        ),
    }


def safety(snapshot: dict) -> dict:
    """Exibe sinais sintéticos de atenção para uma intenção de PIX. Nunca executa pagamento."""
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


def _safe_url(url: object) -> str | None:
    """Retorna a URL somente se o esquema for HTTP(S); caso contrário retorna None."""
    if not isinstance(url, str):
        return None
    try:
        parsed = urlsplit(url)
        return url if (parsed.scheme.lower() in _SAFE_SCHEMES and parsed.hostname
                       and not parsed.username and not parsed.password) else None
    except ValueError:
        return None


def guidance(snapshot: dict) -> dict:
    """Recupera trechos curados por conceitos locais, com fallback por tópico."""
    topic = "pix" if snapshot.get("pix") else "purchase" if snapshot.get("purchase") else "cashflow"
    context = [snapshot["title"], *(event["label"] for event in snapshot["events"])]
    if snapshot.get("purchase"):
        context.extend([snapshot["purchase"]["label"], "compra parcelamento"])
    if snapshot.get("pix"):
        context.append("PIX destinatário verificação")
    result = _RETRIEVER.retrieve(" ".join(context), topic)
    result["documents"] = [{**doc, "url": _safe_url(doc.get("url"))} for doc in result["documents"]]
    return result


def apply_saving(snapshot: dict, reduction: int) -> dict:
    """Ajusta apenas previsões flexíveis, sem alterar transações realizadas."""
    validate(snapshot)
    changed = deepcopy(snapshot)
    remaining = amount(reduction)
    for event in sorted(changed["events"], key=lambda e: e["date"]):
        if event["direction"] == "out" and event["flexible"] and event["date"] <= snapshot["horizon"]:
            part = min(event["amount_cents"], remaining)
            event["amount_cents"] -= part
            remaining -= part
    if remaining:
        raise ValueError("Redução superior às despesas flexíveis.")
    return changed


def _explanations(snapshot: dict, results: dict, actions: list[dict]) -> dict:
    """Expõe dados e limites verificáveis de cada decisão, sem raciocínio de LLM."""
    flow = results["cashflow"]
    events = [event for event in snapshot["events"] if event["date"] <= snapshot["horizon"]]
    income = sum(event["amount_cents"] for event in events if event["direction"] == "in")
    expenses = sum(event["amount_cents"] for event in events if event["direction"] == "out")
    if flow["first_negative_date"]:
        summary = "As saídas conhecidas deixam o menor saldo abaixo de zero no horizonte analisado."
    elif flow["gap_to_buffer_cents"]:
        summary = "O menor saldo previsto fica abaixo da margem escolhida para este cenário."
    else:
        summary = "O calendário conhecido preserva a margem escolhida; novas despesas podem mudar o resultado."
    explanations = {
        "cashflow": {
            "title": "Por que acompanhar esta margem",
            "summary": summary,
            "numbers": [{"label": label, "value_cents": value} for label, value in (
                ("Saldo inicial", snapshot["balance_cents"]), ("Recebimentos no horizonte", income),
                ("Despesas no horizonte", expenses), ("Menor saldo previsto", flow["minimum_cents"]),
                ("Margem escolhida", flow["buffer_cents"]), ("Falta para a margem", flow["gap_to_buffer_cents"]),
            )],
            "assumptions": [
                f"Fechamentos diários de {snapshot['as_of']} a {snapshot['horizon']}; eventos do mesmo dia são somados.",
                f"O menor fechamento ocorre em {flow['minimum_date']}.",
                "Recebimentos e compromissos usam as datas e os valores sintéticos informados; não são garantidos.",
            ],
            "not_considered": [
                "Horários de liquidação dentro de um mesmo dia.",
                "Novas despesas, juros, tarifas e alterações de renda não registrados no cenário.",
                "Eventos depois do horizonte, inclusive recebimentos atrasados para além dele.",
            ],
        },
    }
    for action in actions:
        if action["id"] == "budget-plan":
            explanations["budget-plan"] = {
                "title": "Por que sugerir este ajuste",
                "summary": "A redução flexível preserva a margem desejada." if action["meets_buffer"] else
                    "A redução flexível melhora a projeção, mas ainda não recompõe toda a margem desejada.",
                "numbers": [{"label": label, "value_cents": value} for label, value in (
                    ("Gastos flexíveis disponíveis", flow["flexible_cents"]),
                    ("Redução proposta", action["reduction_cents"]), ("Menor saldo antes", action["before_cents"]),
                    ("Menor saldo após o ajuste", action["after_cents"]), ("Margem escolhida", flow["buffer_cents"]),
                )],
                "assumptions": ["Reduz somente previsões flexíveis deste horizonte, em ordem de data.",
                                "O ajuste depende da sua aprovação; despesas essenciais permanecem iguais."],
                "not_considered": ["Compras já realizadas, bloqueio de gastos e movimentação de dinheiro.",
                                   "Mudanças futuras no orçamento que não foram informadas."],
            }
        elif action["id"] == "purchase-goal":
            explanations["purchase-goal"] = {
                "title": "Por que oferecer uma meta",
                "summary": "A meta registra o preço para planejar a compra antes de assumir um compromisso.",
                "numbers": [{"label": "Valor da meta", "value_cents": action["target_cents"]},
                            {"label": "Margem escolhida", "value_cents": flow["buffer_cents"]}],
                "assumptions": ["A meta é demonstrativa e só é registrada após sua aprovação."],
                "not_considered": ["Reserva automática, rendimento, transferência e prazo para alcançar a meta."],
            }
    comparison = results.get("purchase", {})
    if comparison.get("available"):
        scheduled_count = len(comparison.get("schedule", []))
        out = comparison.get("out_of_horizon", 0)
        not_considered = ["Juros, tarifas e outras ofertas de crédito.",
                          "Contratação de compra, crédito ou recomendação financeira personalizada."]
        if out:
            not_considered.insert(0, f"{out} parcela(s) fora do horizonte não foram incluídas no cálculo do menor saldo.")
        numbers = [{"label": label, "value_cents": comparison[key]} for label, key in (
            ("Preço à vista", "price_cents"), ("Menor saldo à vista", "cash_minimum_cents"),
            ("Primeira parcela", "first_installment_cents"),
            ("Menor saldo com a primeira parcela (só 1ª parcela)", "installment_minimum_cents"),
        )]
        if scheduled_count > 1:
            numbers.append({"label": f"Menor saldo com {scheduled_count} parcela(s) projetada(s)", "value_cents": comparison["installment_projected_minimum_cents"]})
        numbers.append({"label": "Margem escolhida", "value_cents": flow["buffer_cents"]})
        explanations["purchase"] = {
            "title": "Por que comparar antes de comprar",
            "summary": comparison["recommendation"] + ": o preço é comparado ao calendário e à margem desejada.",
            "numbers": numbers,
            "assumptions": [comparison["assumption"]],
            "not_considered": not_considered,
        }
    signals = results.get("safety", {})
    if signals.get("available"):
        explanations["safety"] = {
            "title": "Por que conferir este PIX",
            "summary": f"Há {len(signals['reasons'])} sinais ilustrativos neste cenário. " + signals["recommendation"],
            "numbers": [{"label": label, "value_cents": value} for label, value in (
                ("Valor do PIX", signals["amount_cents"]), ("Padrão sintético", snapshot["typical_pix_cents"]),
                ("Referência de três vezes o padrão", snapshot["typical_pix_cents"] * 3),
            )],
            "assumptions": signals["reasons"] + ["São regras sobre sinais fornecidos pelo cenário, não um detector validado."],
            "not_considered": ["Identidade real do destinatário, histórico bancário e bases externas de fraude.",
                               signals["limitation"]],
        }
    retrieved = results.get("guidance")
    if retrieved:
        explanations["guidance"] = {
            "title": "Por que estas orientações aparecem",
            "summary": "Trechos curados relacionados ao cenário, recuperados por conceitos locais." if
                retrieved["retrieval_mode"] == "local_concepts" else
                "Sem correspondência de termos suficiente; são exibidas as orientações do tópico do cenário.",
            "numbers": [],
            "assumptions": ["Consulta à base local carregada na inicialização; o texto não é gerado por um modelo."],
            "not_considered": [retrieved["limitation"], "Condições bancárias atuais e aconselhamento individual."],
        }
    return explanations


def build_report(snapshot: dict, consent: object, planner: object = None) -> dict:
    """Coordena a seleção de ferramentas e constrói o relatório da sessão."""
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
            raw = planner.plan(deepcopy(snapshot))
            # Valida o plano antes de aceitar o modo watsonx.
            if (not isinstance(raw, list)
                    or not 1 <= len(raw) <= 4
                    or any(type(x) is not str or x not in TOOLS for x in raw)):
                raise ValueError("Plano inválido retornado pelo planejador.")
            selected = raw
            mode = "watsonx"
        except Exception:
            # Não retorna prompts, chaves ou respostas HTTP ao navegador.
            warning = "O planejador IBM não respondeu com um plano válido. Demonstração por regras ativada."
            mode = "demo_fallback"
    selected = [name for name in dict.fromkeys(selected) if name in TOOLS]
    # Política exige análise de caixa e segurança quando há uma operação.
    if "cashflow" not in selected:
        selected.insert(0, "cashflow")
    if "guidance" not in selected:
        selected.append("guidance")
    if snapshot.get("pix") and "safety" not in selected:
        selected.append("safety")
    if snapshot.get("purchase") and "purchase" not in selected:
        selected.append("purchase")
    # Preserva ordem canônica legível para o trace.
    selected = [t for t in _TOOL_ORDER if t in selected]
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
            "explanations": _explanations(snapshot, result, actions),
            "estimated": True, "policy_version": "demo-1"}
