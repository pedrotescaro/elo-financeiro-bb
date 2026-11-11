"""Carteira sintética de uma agência e análise em lote para o analista de negócios.

A carteira representa o tipo de dado corporativo que um analista do banco
consulta: muitos clientes, cada um com saldo, compromissos futuros e
consentimento de compartilhamento. Todos os registros são fictícios e gerados
de forma determinística (`python -m elo.carteira --gerar`). Cada cliente usa o
mesmo formato de snapshot dos cenários, então o cálculo é o de `core.cashflow`.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import unicodedata
from copy import deepcopy
from datetime import date, timedelta
from time import perf_counter

from .core import ROOT, apply_saving, cashflow

PATH = ROOT / "data" / "carteira.json"
AS_OF = date(2026, 10, 7)
HORIZON_DAYS = 14
SEED = 17
SIZE = 40

SEGMENTOS = {
    "assalariado": "Assalariado com salário mensal",
    "renda-variavel": "Autônomo com renda variável",
    "aposentado": "Aposentado ou pensionista",
    "estudante": "Estudante com renda parcial",
    "mei": "Microempreendedor individual (conta PF)",
}
_FIXED_OUT = [("Moradia", 60000, 140000), ("Energia e água", 15000, 40000), ("Fatura já comprometida", 25000, 120000),
              ("Escola ou curso", 30000, 90000), ("Plano de saúde", 20000, 70000), ("Parcela de financiamento", 30000, 110000)]
_FLEX_OUT = [("Lazer previsto", 10000, 60000), ("Compras não essenciais", 8000, 45000),
             ("Restaurantes e delivery", 8000, 40000), ("Assinaturas", 3000, 12000)]
_INCOME = {"assalariado": (220000, 520000), "renda-variavel": (150000, 600000), "aposentado": (180000, 380000),
           "estudante": (80000, 160000), "mei": (200000, 650000)}


def _cents(rng: random.Random, low: int, high: int) -> int:
    """Valores múltiplos de R$ 10 para facilitar a leitura na demonstração."""
    return rng.randrange(low // 1000, high // 1000 + 1) * 1000


def gerar(seed: int = SEED, size: int = SIZE) -> dict:
    """Gera a carteira sintética; mesma semente, mesmo resultado."""
    rng = random.Random(seed)
    horizon = AS_OF + timedelta(days=HORIZON_DAYS)
    clientes = []
    segment_ids = list(SEGMENTOS)
    for n in range(1, size + 1):
        segmento = segment_ids[(n - 1) % len(segment_ids)] if n <= len(segment_ids) else rng.choice(segment_ids)
        low, high = _INCOME[segmento]
        income = _cents(rng, low, high)
        income_day = AS_OF + timedelta(days=rng.randrange(5, HORIZON_DAYS + 1))
        events = []
        for i, (label, lo, hi) in enumerate(rng.sample(_FIXED_OUT, rng.randrange(2, 5))):
            events.append({"id": f"f{i}", "date": (AS_OF + timedelta(days=rng.randrange(1, HORIZON_DAYS))).isoformat(),
                           "label": label, "amount_cents": _cents(rng, lo, hi), "direction": "out", "flexible": False})
        for i, (label, lo, hi) in enumerate(rng.sample(_FLEX_OUT, rng.randrange(1, 4))):
            events.append({"id": f"x{i}", "date": (AS_OF + timedelta(days=rng.randrange(1, HORIZON_DAYS))).isoformat(),
                           "label": label, "amount_cents": _cents(rng, lo, hi), "direction": "out", "flexible": True})
        events.append({"id": "income", "date": income_day.isoformat(), "label": "Recebimento esperado",
                       "amount_cents": income, "direction": "in", "flexible": False})
        events.sort(key=lambda e: (e["date"], e["id"]))
        outflow_before_income = sum(e["amount_cents"] for e in events
                                    if e["direction"] == "out" and e["date"] < income_day.isoformat())
        # Saldos variados: parte da carteira fica apertada antes do recebimento, parte não.
        balance = max(5000, outflow_before_income + _cents(rng, -40000, 170000))
        clientes.append({
            "id": f"C{n:02d}",
            "nome": f"Cliente {n:02d}",
            "segmento": segmento,
            "consentimento_open_finance": rng.random() > 0.12,
            "snapshot": {
                "title": f"Atendimento do Cliente {n:02d}",
                "synthetic": True,
                "as_of": AS_OF.isoformat(),
                "horizon": horizon.isoformat(),
                "balance_cents": balance,
                "buffer_cents": _cents(rng, 10000, 40000),
                "typical_pix_cents": 10000,
                "events": events,
            },
        })
    return {
        "agencia": "Agência fictícia 0001",
        "descricao": "Carteira sintética para demonstração. Nenhum registro corresponde a pessoa ou cliente real.",
        "synthetic": True,
        "seed": seed,
        "gerada_para": AS_OF.isoformat(),
        "clientes": clientes,
    }


def carregar() -> dict:
    """Lê a carteira publicada em data/carteira.json."""
    data = json.loads(PATH.read_text(encoding="utf-8"))
    if data.get("synthetic") is not True:
        raise ValueError("A demonstração aceita somente carteiras sintéticas.")
    return data


CARTEIRA: dict = carregar() if PATH.exists() else gerar()
_BY_ID = {c["id"]: c for c in CARTEIRA["clientes"]}


def cliente_snapshot(client_id: str) -> dict:
    """Snapshot de um cliente para abrir no fluxo de atendimento (somente com consentimento)."""
    client = _BY_ID.get(client_id)
    if client is None:
        raise ValueError("Cliente desconhecido.")
    if not client["consentimento_open_finance"]:
        raise ValueError("Cliente sem consentimento de compartilhamento; a análise não está disponível.")
    return deepcopy(client["snapshot"])


def analisar_cliente(client: dict) -> dict:
    """Classifica um cliente com o mesmo cálculo da tela de atendimento."""
    snap = client["snapshot"]
    flow = cashflow(snap)
    as_of = date.fromisoformat(snap["as_of"])
    negative = flow["first_negative_date"]
    if negative:
        risco = "negativo"
    elif flow["minimum_cents"] < flow["buffer_cents"]:
        risco = "abaixo_da_margem"
    else:
        risco = "ok"
    gap = flow["gap_to_buffer_cents"]
    # Mesmo cálculo da proposta na tela de atendimento: reduz gastos flexíveis previstos
    # e recalcula. Gasto flexível que cai depois do pior dia não ajuda.
    reducao = min(gap, flow["flexible_cents"])
    depois = cashflow(apply_saving(snap, reducao))["minimum_cents"] if reducao else flow["minimum_cents"]
    resolve = risco != "ok" and depois >= flow["buffer_cents"]
    if risco == "ok":
        acao = "Sem contato necessário neste horizonte."
    elif resolve:
        acao = "Contato proativo: propor ajuste nos gastos flexíveis previstos, com aprovação do cliente."
    else:
        acao = "Contato proativo: gastos flexíveis não cobrem a falta; revisar o calendário com o cliente."
    return {
        "id": client["id"], "nome": client["nome"], "segmento": client["segmento"],
        "segmento_rotulo": SEGMENTOS[client["segmento"]],
        "risco": risco,
        "menor_saldo_cents": flow["minimum_cents"], "data_menor_saldo": flow["minimum_date"],
        "primeiro_negativo": negative,
        "dias_ate_risco": (date.fromisoformat(negative) - as_of).days if negative else None,
        "falta_para_margem_cents": gap, "flexivel_cents": flow["flexible_cents"],
        "margem_cents": flow["buffer_cents"], "resolve_com_flexivel": resolve,
        "reducao_sugerida_cents": reducao if risco != "ok" else 0, "menor_saldo_apos_ajuste_cents": depois,
        "acao_sugerida": acao,
    }


_RISK_ORDER = {"negativo": 0, "abaixo_da_margem": 1, "ok": 2}


def analisar_carteira(carteira: dict | None = None) -> dict:
    """Analisa todos os clientes com consentimento e mede o tempo da análise."""
    data = carteira or CARTEIRA
    started = perf_counter()
    consented = [c for c in data["clientes"] if c["consentimento_open_finance"]]
    rows = [analisar_cliente(c) for c in consented]
    rows.sort(key=lambda r: (_RISK_ORDER[r["risco"]], r["menor_saldo_cents"], r["id"]))
    elapsed_ms = (perf_counter() - started) * 1000
    em_risco = [r for r in rows if r["risco"] != "ok"]
    return {
        "agencia": data["agencia"], "data_base": data["gerada_para"],
        "total_clientes": len(data["clientes"]), "analisados": len(rows),
        "sem_consentimento": len(data["clientes"]) - len(rows),
        "negativos": sum(r["risco"] == "negativo" for r in rows),
        "abaixo_da_margem": sum(r["risco"] == "abaixo_da_margem" for r in rows),
        "resolvem_com_flexivel": sum(r["resolve_com_flexivel"] for r in rows),
        "falta_total_cents": sum(r["falta_para_margem_cents"] for r in em_risco),
        "tempo_analise_ms": round(elapsed_ms, 2),
        "clientes": rows,
    }


# ---------------------------------------------------------------------------
# Perguntas do analista
# ---------------------------------------------------------------------------

INTENCOES = ("resumo", "negativos", "abaixo_da_margem", "em_risco", "resolvem", "nao_resolvem", "cliente")
_LIMITE_PADRAO = 10


def _plain(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text.lower()) if not unicodedata.combining(c))


def interpretar_por_regras(pergunta: str) -> dict:
    """Traduz a pergunta em consulta estruturada usando palavras-chave revisadas."""
    q = _plain(pergunta)
    consulta: dict = {"intencao": "em_risco", "segmento": None, "dias": None, "limite": _LIMITE_PADRAO, "cliente": None}
    m = re.search(r"\bc\s?(\d{1,2})\b|cliente\s+(\d{1,2})\b", q)
    if m:
        consulta.update(intencao="cliente", cliente=f"C{int(m.group(1) or m.group(2)):02d}")
        return consulta
    for seg in SEGMENTOS:
        tokens = {"renda-variavel": ("variavel", "autonom"), "mei": ("mei", "microempreend"),
                  "aposentado": ("aposentad", "pensionist"), "estudante": ("estudant",),
                  "assalariado": ("assalariad", "salario fixo", "clt")}[seg]
        if any(t in q for t in tokens):
            consulta["segmento"] = seg
    d = re.search(r"(\d{1,2})\s*dias?", q)
    if d:
        consulta["dias"] = max(1, min(HORIZON_DAYS, int(d.group(1))))
    top = re.search(r"\b(?:top|primeiros|maiores|principais)\s+(\d{1,2})\b", q)
    if top:
        consulta["limite"] = max(1, min(40, int(top.group(1))))
    if any(w in q for w in ("resumo", "visao geral", "panorama", "quantos clientes", "como esta a carteira")):
        consulta["intencao"] = "resumo"
    elif any(w in q for w in ("nao resolve", "nao cobre", "nao basta", "insuficiente")):
        consulta["intencao"] = "nao_resolvem"
    elif any(w in q for w in ("resolve", "cobre", "ajuste", "reduzir", "flexive")):
        consulta["intencao"] = "resolvem"
    elif any(w in q for w in ("negativ", "vermelho", "zerar", "zera", "estour", "falta de dinheiro")):
        consulta["intencao"] = "negativos"
    elif any(w in q for w in ("margem", "reserva", "folga")):
        consulta["intencao"] = "abaixo_da_margem"
    return consulta


def validar_consulta(raw: object) -> dict:
    """Aceita somente consultas no contrato; usado para a saída do modelo."""
    if not isinstance(raw, dict) or raw.get("intencao") not in INTENCOES:
        raise ValueError("Consulta fora do contrato.")
    seg, dias, limite, cliente = raw.get("segmento"), raw.get("dias"), raw.get("limite", _LIMITE_PADRAO), raw.get("cliente")
    if seg is not None and seg not in SEGMENTOS:
        raise ValueError("Segmento desconhecido.")
    if dias is not None and (type(dias) is not int or not 1 <= dias <= HORIZON_DAYS):
        raise ValueError("Prazo inválido.")
    if type(limite) is not int or not 1 <= limite <= 40:
        raise ValueError("Limite inválido.")
    if raw["intencao"] == "cliente" and not (isinstance(cliente, str) and re.fullmatch(r"C\d{2}", cliente)):
        raise ValueError("Cliente inválido.")
    return {"intencao": raw["intencao"], "segmento": seg, "dias": dias, "limite": limite,
            "cliente": cliente if raw["intencao"] == "cliente" else None}


def _brl(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    reais, cent = divmod(abs(cents), 100)
    return f"{sign}R$ {reais:,}".replace(",", ".") + f",{cent:02d}"


def _dia(iso: str) -> str:
    return iso[8:10] + "/" + iso[5:7]


def _n(qtd: int) -> str:
    return f"{qtd} cliente" if qtd == 1 else f"{qtd} clientes"


def executar(consulta: dict, analise: dict) -> dict:
    """Aplica a consulta sobre a análise já calculada e redige a resposta com números do código."""
    rows = analise["clientes"]
    if consulta["intencao"] == "cliente":
        row = next((r for r in rows if r["id"] == consulta["cliente"]), None)
        if row is None:
            fora = consulta["cliente"] in _BY_ID
            texto = (f"{consulta['cliente']} não tem consentimento de compartilhamento ativo; não analisamos esse cliente."
                     if fora else f"Não existe {consulta['cliente']} nesta carteira.")
            return {"resposta": texto, "clientes": []}
        quando = f"fica negativo em {_dia(row['primeiro_negativo'])}" if row["primeiro_negativo"] else "não fica negativo"
        texto = (f"{row['nome']} ({row['segmento_rotulo']}) {quando}; menor saldo previsto {_brl(row['menor_saldo_cents'])} "
                 f"em {_dia(row['data_menor_saldo'])}. Faltam {_brl(row['falta_para_margem_cents'])} para a margem e há "
                 f"{_brl(row['flexivel_cents'])} em gastos flexíveis previstos. {row['acao_sugerida']}")
        return {"resposta": texto, "clientes": [row]}
    if consulta["intencao"] == "resumo":
        texto = (f"{analise['agencia']}: {_n(analise['analisados'])} analisados "
                 f"({analise['sem_consentimento']} sem consentimento ficaram de fora). {_n(analise['negativos'])} com saldo "
                 f"negativo nos próximos 14 dias e {_n(analise['abaixo_da_margem'])} abaixo da margem. "
                 f"{analise['resolvem_com_flexivel']} desses casos se resolvem com ajuste de gastos flexíveis. "
                 f"Falta total para a margem: {_brl(analise['falta_total_cents'])}.")
        return {"resposta": texto, "clientes": [r for r in rows if r["risco"] != "ok"][:consulta["limite"]]}
    filtros = {
        "negativos": lambda r: r["risco"] == "negativo",
        "abaixo_da_margem": lambda r: r["risco"] == "abaixo_da_margem",
        "em_risco": lambda r: r["risco"] != "ok",
        "resolvem": lambda r: r["resolve_com_flexivel"],
        "nao_resolvem": lambda r: r["risco"] != "ok" and not r["resolve_com_flexivel"],
    }
    found = [r for r in rows if filtros[consulta["intencao"]](r)]
    if consulta["segmento"]:
        found = [r for r in found if r["segmento"] == consulta["segmento"]]
    if consulta["dias"] is not None:
        found = [r for r in found if r["dias_ate_risco"] is not None and r["dias_ate_risco"] <= consulta["dias"]]
    descricao = {
        "negativos": "saldo negativo nos próximos 14 dias",
        "abaixo_da_margem": "saldo abaixo da margem de segurança, sem ficar negativo",
        "em_risco": "saldo negativo ou abaixo da margem",
        "resolvem": "risco que se resolve com ajuste de gastos flexíveis",
        "nao_resolvem": "risco que não se resolve só com gastos flexíveis",
    }[consulta["intencao"]]
    recorte = []
    if consulta["segmento"]:
        recorte.append("segmento " + SEGMENTOS[consulta["segmento"]].lower())
    if consulta["dias"] is not None and consulta["intencao"] == "negativos":
        descricao = f"saldo negativo nos próximos {consulta['dias']} dias"
    elif consulta["dias"] is not None:
        recorte.append(f"saldo negativo em até {consulta['dias']} dias")
    sufixo = f" ({'; '.join(recorte)})" if recorte else ""
    if not found:
        return {"resposta": f"Nenhum cliente com {descricao}{sufixo}.", "clientes": []}
    shown = found[:consulta["limite"]]
    falta = sum(r["falta_para_margem_cents"] for r in found)
    texto = (f"{_n(len(found))} com {descricao}{sufixo}. Falta somada para a margem: {_brl(falta)}. "
             f"Mostrando {len(shown)}, do menor saldo previsto para o maior.")
    return {"resposta": texto, "clientes": shown}


def responder(pergunta: object, interpreter: object = None, analise: dict | None = None) -> dict:
    """Responde a uma pergunta do analista. O modelo, se houver, só interpreta a pergunta."""
    if not isinstance(pergunta, str) or not pergunta.strip():
        raise ValueError("Escreva uma pergunta sobre a carteira.")
    pergunta = pergunta.strip()[:300]
    started = perf_counter()
    analise = analise or analisar_carteira()
    interpretado_por, aviso = "regras", None
    consulta = interpretar_por_regras(pergunta)
    if interpreter is not None and hasattr(interpreter, "interpret"):
        try:
            consulta = validar_consulta(interpreter.interpret(pergunta))
            interpretado_por = "watsonx"
        except Exception:
            aviso = "O IBM watsonx.ai não devolveu uma consulta válida. A pergunta foi interpretada por regras."
            interpretado_por = "regras_contingencia"
    resultado = executar(consulta, analise)
    return {
        "pergunta": pergunta, "consulta": consulta, "interpretado_por": interpretado_por, "aviso": aviso,
        "resposta": resultado["resposta"], "clientes": resultado["clientes"],
        "analisados": analise["analisados"], "sem_consentimento": analise["sem_consentimento"],
        "tempo_resposta_ms": round((perf_counter() - started) * 1000, 2),
        "limites": "Dados sintéticos. Projeção por fechamento diário com eventos conhecidos; não avalia crédito nem confirma fraude.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Carteira sintética da agência.")
    parser.add_argument("--gerar", action="store_true", help="regrava data/carteira.json a partir da semente")
    args = parser.parse_args(argv)
    if args.gerar:
        PATH.write_text(json.dumps(gerar(), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"Carteira gravada em {PATH.relative_to(ROOT)}")
    resumo = analisar_carteira(carregar() if PATH.exists() else gerar())
    print({k: v for k, v in resumo.items() if k != "clientes"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
