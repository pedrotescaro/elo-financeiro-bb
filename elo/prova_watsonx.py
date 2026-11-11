"""Gera evidência verificável de chamadas reais ao IBM watsonx.ai.

Uso (com as variáveis IBM configuradas apenas no terminal):

    python -m elo.prova_watsonx

Para cada cenário sintético de data/scenarios.json, o script monta o relatório
com o WatsonxPlanner e grava em docs/evidencias/watsonx/ um JSON com o que a
própria API informou (model_id, model_version, created_at, contagem de tokens),
a latência medida e as ferramentas finais. Chave de API, token IAM e ID do
projeto nunca são gravados; o projeto aparece apenas como digest curto.

Uma execução só é marcada como "chamada_real_comprovada" quando todos os
cenários terminam em modo "watsonx", sem cache e com model_id devolvido pela
API. Qualquer falha fica registrada como contingência, sem esconder o motivo.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from time import monotonic
from urllib.parse import urlsplit

from .core import CATALOG, ROOT, build_report, load_scenario

REQUIRED = ("IBM_CLOUD_API_KEY", "WATSONX_PROJECT_ID", "WATSONX_MODEL_ID", "WATSONX_URL")
DEFAULT_OUTPUT = ROOT / "docs" / "evidencias" / "watsonx"
_BRT = timezone(timedelta(hours=-3), "BRT")


def missing_variables(environ: dict | None = None) -> list[str]:
    """Lista as variáveis obrigatórias ausentes, sem ler seus valores."""
    env = os.environ if environ is None else environ
    return [name for name in REQUIRED if not env.get(name, "").strip()]


def _region(url: str) -> str:
    host = urlsplit(url).hostname or ""
    return host.split(".", 1)[0] if host.endswith(".ml.cloud.ibm.com") else "desconhecida"


def run(planner_factory, scenarios: list[str] | None = None, *, clock=monotonic,
        now=None, environ: dict | None = None) -> dict:
    """Executa um relatório por cenário e devolve o registro de evidência."""
    env = os.environ if environ is None else environ
    started = (now or (lambda: datetime.now(_BRT)))()
    planner = planner_factory()
    cases = []
    for name in scenarios or list(CATALOG):
        if hasattr(planner, "invalidate_cache"):
            planner.invalidate_cache()  # força chamada nova para cada cenário
        t0 = clock()
        report = build_report(load_scenario(name), True, planner)
        latency = clock() - t0
        call = getattr(planner, "last_call", None) or {}
        real = (report.get("mode") == "watsonx" and call.get("cache_hit") is False
                and bool(call.get("model_id")))
        cases.append({
            "cenario": name,
            "modo_do_relatorio": report.get("mode"),
            "chamada_real": real,
            "latencia_s": round(latency, 3),
            "ferramentas_finais": [step["tool"] for step in report.get("trace", [])],
            "aviso": report.get("warning"),
            "resposta_api": {key: call.get(key) for key in (
                "model_id", "model_version", "created_at", "input_token_count",
                "generated_token_count", "stop_reason", "generated_text") if key in call},
        })
    project = env.get("WATSONX_PROJECT_ID", "")
    return {
        "gerado_em": started.isoformat(timespec="seconds"),
        "produto": "IBM watsonx.ai (text generation REST API, version=2024-05-31)",
        "modelo_solicitado": env.get("WATSONX_MODEL_ID"),
        "regiao": _region(env.get("WATSONX_URL", "")),
        "projeto_digest": sha256(project.encode()).hexdigest()[:8] if project else None,
        "casos": cases,
        "chamada_real_comprovada": bool(cases) and all(case["chamada_real"] for case in cases),
        "observacao": ("Dados sintéticos. Chave, token IAM e ID do projeto não são gravados. "
                       "Modo 'demo_fallback' indica que a chamada falhou e a contingência por regras foi usada."),
    }


def save(evidence: dict, output: Path) -> Path:
    """Grava o JSON com nome derivado do horário da execução."""
    output.mkdir(parents=True, exist_ok=True)
    stamp = evidence["gerado_em"][:19].replace(":", "").replace("T", "_")
    path = output / f"{stamp}.json"
    path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Comprova chamadas reais ao IBM watsonx.ai.")
    parser.add_argument("--saida", type=Path, default=DEFAULT_OUTPUT,
                        help="pasta onde o JSON de evidência será gravado")
    parser.add_argument("--cenario", action="append", choices=sorted(CATALOG),
                        help="limita a execução a um cenário (pode repetir)")
    args = parser.parse_args(argv)

    missing = missing_variables()
    if missing:
        print("Sem credenciais IBM: nenhuma chamada foi feita e nenhuma evidência foi gravada.")
        print("Variáveis ausentes: " + ", ".join(missing))
        return 2

    from .watsonx import WatsonxPlanner
    evidence = run(WatsonxPlanner, args.cenario)
    path = save(evidence, args.saida)
    for case in evidence["casos"]:
        api = case["resposta_api"]
        print(f"[{case['cenario']}] modo={case['modo_do_relatorio']} real={case['chamada_real']} "
              f"latência={case['latencia_s']}s modelo={api.get('model_id')} "
              f"ferramentas={','.join(case['ferramentas_finais'])}")
    verdict = "COMPROVADA" if evidence["chamada_real_comprovada"] else "NÃO COMPROVADA (ver avisos no JSON)"
    print(f"Chamada real ao watsonx.ai: {verdict}")
    print(f"Evidência gravada em: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
    return 0 if evidence["chamada_real_comprovada"] else 1


if __name__ == "__main__":
    sys.exit(main())
