"""Evidência de chamada real ao watsonx.ai, verificada com respostas simuladas."""
from datetime import datetime, timedelta, timezone
from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from elo import prova_watsonx
from elo.watsonx import WatsonxPlanner, _TokenCache


ENV = {
    "IBM_CLOUD_API_KEY": "chave-secreta-sintetica",
    "WATSONX_PROJECT_ID": "projeto-secreto-sintetico",
    "WATSONX_MODEL_ID": "ibm/granite-sintetico",
    "WATSONX_URL": "https://us-south.ml.cloud.ibm.com",
}
FIXED_NOW = datetime(2026, 11, 11, 14, 30, 0, tzinfo=timezone(timedelta(hours=-3)))


def response(payload: object) -> BytesIO:
    return BytesIO(json.dumps(payload).encode())


def generation(tools: list[str]) -> BytesIO:
    return response({
        "model_id": "ibm/granite-sintetico",
        "model_version": "1.0.0",
        "created_at": "2026-11-11T17:30:00.000Z",
        "results": [{"generated_text": json.dumps({"tools": tools}), "generated_token_count": 12,
                     "input_token_count": 300, "stop_reason": "eos_token"}],
    })


class ProvaWatsonxTests(unittest.TestCase):
    def setUp(self):
        env = patch.dict("os.environ", ENV, clear=True)
        env.start()
        self.addCleanup(env.stop)

    def planner(self):
        return WatsonxPlanner(token_cache=_TokenCache())

    def test_missing_variables_lists_names_only(self):
        self.assertEqual(prova_watsonx.missing_variables({"WATSONX_URL": "x"}),
                         ["IBM_CLOUD_API_KEY", "WATSONX_PROJECT_ID", "WATSONX_MODEL_ID"])
        self.assertEqual(prova_watsonx.missing_variables(ENV), [])

    def test_main_without_credentials_writes_nothing_and_returns_2(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict("os.environ", {}, clear=True):
            with patch("builtins.print"):
                code = prova_watsonx.main(["--saida", folder])
            self.assertEqual(code, 2)
            self.assertEqual(list(Path(folder).iterdir()), [])

    def test_real_response_metadata_is_recorded_without_secrets(self):
        with patch("elo.watsonx.urlopen", side_effect=[
            response({"access_token": "token-secreto", "expires_in": 3600}),
            generation(["cashflow", "guidance"]),
        ]):
            evidence = prova_watsonx.run(self.planner, ["month"], now=lambda: FIXED_NOW)
        case = evidence["casos"][0]
        self.assertTrue(evidence["chamada_real_comprovada"])
        self.assertEqual(case["modo_do_relatorio"], "watsonx")
        self.assertEqual(case["resposta_api"]["model_id"], "ibm/granite-sintetico")
        self.assertEqual(case["resposta_api"]["generated_token_count"], 12)
        self.assertEqual(evidence["regiao"], "us-south")
        text = json.dumps(evidence)
        for secret in ("chave-secreta-sintetica", "projeto-secreto-sintetico", "token-secreto"):
            self.assertNotIn(secret, text)

    def test_each_scenario_forces_a_new_call(self):
        with patch("elo.watsonx.urlopen", side_effect=[
            response({"access_token": "t", "expires_in": 3600}),
            generation(["cashflow", "guidance"]),
            generation(["cashflow", "purchase", "guidance"]),
            generation(["cashflow", "safety", "guidance"]),
        ]) as opened:
            evidence = prova_watsonx.run(self.planner, ["month", "purchase", "pix"], now=lambda: FIXED_NOW)
        self.assertEqual(opened.call_count, 4)  # 1 token IAM reaproveitado + 3 gerações
        self.assertTrue(all(case["chamada_real"] for case in evidence["casos"]))

    def test_failed_call_is_recorded_as_fallback_not_as_proof(self):
        with patch("elo.watsonx.urlopen", side_effect=[
            response({"access_token": "t", "expires_in": 3600}),
            response({"results": [{"generated_text": "não é JSON"}]}),
        ]):
            evidence = prova_watsonx.run(self.planner, ["month"], now=lambda: FIXED_NOW)
        case = evidence["casos"][0]
        self.assertFalse(evidence["chamada_real_comprovada"])
        self.assertEqual(case["modo_do_relatorio"], "demo_fallback")
        self.assertFalse(case["chamada_real"])
        self.assertIsNotNone(case["aviso"])

    def test_save_uses_timestamp_name(self):
        evidence = {"gerado_em": FIXED_NOW.isoformat(timespec="seconds"), "casos": []}
        with tempfile.TemporaryDirectory() as folder:
            path = prova_watsonx.save(evidence, Path(folder))
            self.assertEqual(path.name, "2026-11-11_143000.json")
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["casos"], [])


if __name__ == "__main__":
    unittest.main()
