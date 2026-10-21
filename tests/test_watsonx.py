"""Contrato HTTP do adaptador IBM, simulado sem credenciais ou chamadas reais."""
from io import BytesIO
import json
import ssl
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from elo.core import build_report, load_scenario
from elo.watsonx import WatsonxPlanner, _SSL_CTX


ENV = {
    "IBM_CLOUD_API_KEY": "synthetic-key",
    "WATSONX_PROJECT_ID": "synthetic-project",
    "WATSONX_MODEL_ID": "synthetic-model",
    "WATSONX_URL": "https://us-south.ml.cloud.ibm.com",
}


def response(payload: object) -> BytesIO:
    """Cria uma resposta JSON com a mesma interface de leitura de urlopen."""
    return BytesIO(json.dumps(payload).encode())


class WatsonxTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict("os.environ", ENV, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.planner = WatsonxPlanner()

    def report_with_generation(self, generated):
        with patch("elo.watsonx.urlopen", side_effect=[
            response({"access_token": "synthetic-token"}),
            response({"results": [{"generated_text": generated}]}),
        ]):
            return build_report(load_scenario("month"), True, self.planner)

    def test_valid_generation_uses_verified_tls_and_constrained_prompt(self):
        with patch("elo.watsonx.urlopen", side_effect=[
            response({"access_token": "synthetic-token"}),
            response({"results": [{"generated_text": '{"tools":["cashflow","guidance"]}'}]}),
        ]) as opened:
            self.assertEqual(self.planner.plan(load_scenario("month")), ["cashflow", "guidance"])
        self.assertTrue(_SSL_CTX.check_hostname)
        self.assertEqual(_SSL_CTX.verify_mode, ssl.CERT_REQUIRED)
        self.assertEqual(opened.call_count, 2)
        for call in opened.call_args_list:
            self.assertIs(call.kwargs["context"], _SSL_CTX)
            self.assertGreater(call.kwargs["timeout"], 0)
        generation = opened.call_args_list[1].args[0]
        payload = json.loads(generation.data)
        self.assertIn("CONTEXTO_INICIO", payload["input"])
        self.assertTrue(payload["input"].endswith("Retorne somente o JSON de seleção de ferramentas permitidas."))
        self.assertIn("version=2024-05-31", generation.full_url)

    def test_malformed_generation_falls_back_without_exposing_remote_data(self):
        malformed = [
            "not-json", "{}", "[]", "null", '{"tools":null}',
            '{"tools":[]}', '{"tools":["send_pix"]}',
            '{"tools":["cashflow", "guidance", "safety", "purchase", "cashflow"]}',
            '{"tools":[1]}', '{"tools":"cashflow"}', None,
        ]
        for generated in malformed:
            with self.subTest(generated=generated):
                report = self.report_with_generation(generated)
                self.assertEqual(report["mode"], "demo_fallback")
                self.assertIn("cashflow", report["results"])
                self.assertIn("regras", report["warning"])
                self.assertNotIn("synthetic-key", report["warning"])

    def test_malformed_http_envelopes_fall_back(self):
        for envelope in [None, {}, {"results": []}, {"results": [None]}, {"results": [{}]}]:
            with self.subTest(envelope=envelope), patch("elo.watsonx.urlopen", side_effect=[
                response({"access_token": "synthetic-token"}), response(envelope),
            ]):
                report = build_report(load_scenario("month"), True, self.planner)
                self.assertEqual(report["mode"], "demo_fallback")

    def test_bad_iam_response_never_attempts_generation(self):
        for auth in [None, {}, {"access_token": ""}, {"access_token": 1}, {"access_token": "a\r\nb"}]:
            with self.subTest(auth=auth), patch("elo.watsonx.urlopen", return_value=response(auth)) as opened:
                report = build_report(load_scenario("month"), True, self.planner)
                self.assertEqual(report["mode"], "demo_fallback")
                self.assertEqual(opened.call_count, 1)

    def test_network_and_http_errors_fall_back(self):
        errors = [TimeoutError("timeout"), URLError("network"),
                  HTTPError(ENV["WATSONX_URL"], 503, "Unavailable", {}, None)]
        for error in errors:
            for during_generation in (False, True):
                with self.subTest(error=type(error).__name__, generation=during_generation):
                    effects = [response({"access_token": "synthetic-token"}), error] if during_generation else [error]
                    with patch("elo.watsonx.urlopen", side_effect=effects):
                        report = build_report(load_scenario("month"), True, self.planner)
                    self.assertEqual(report["mode"], "demo_fallback")
                    self.assertEqual(report["results"]["cashflow"]["minimum_cents"], -10000)

    def test_non_synthetic_snapshot_never_leaves_process(self):
        snapshot = load_scenario("month")
        snapshot["synthetic"] = False
        with patch("elo.watsonx.urlopen") as opened:
            with self.assertRaises(ValueError):
                self.planner.plan(snapshot)
            opened.assert_not_called()

    def test_endpoint_rejects_unsafe_or_nonregional_urls(self):
        invalid = [
            "http://us-south.ml.cloud.ibm.com", "https://ml.cloud.ibm.com",
            "https://us-south.ml.cloud.ibm.com.evil.example",
            "https://evil.example", "https://user@us-south.ml.cloud.ibm.com",
            "https://us-south.ml.cloud.ibm.com:8443", "https://us-south.ml.cloud.ibm.com:bad",
            "https://us-south.ml.cloud.ibm.com/path", "https://us-south.ml.cloud.ibm.com?query=x",
            "https://us-south.ml.cloud.ibm.com#fragment", "https://us-south.ml.cloud.ibm.com?",
            " https://us-south.ml.cloud.ibm.com", "https://[broken",
        ]
        for endpoint in invalid:
            with self.subTest(endpoint=endpoint), patch.dict("os.environ", {"WATSONX_URL": endpoint}):
                with patch("elo.watsonx.urlopen") as opened:
                    with self.assertRaises(ValueError):
                        WatsonxPlanner().plan(load_scenario("month"))
                    opened.assert_not_called()

    def test_endpoint_accepts_https_default_port_and_root(self):
        for endpoint in [ENV["WATSONX_URL"], ENV["WATSONX_URL"] + "/", ENV["WATSONX_URL"] + ":443"]:
            with self.subTest(endpoint=endpoint), patch.dict("os.environ", {"WATSONX_URL": endpoint}):
                with patch("elo.watsonx.urlopen", side_effect=[
                    response({"access_token": "synthetic-token"}),
                    response({"results": [{"generated_text": '{"tools":["cashflow"]}'}]}),
                ]):
                    planner = WatsonxPlanner()
                    self.assertEqual(planner.plan(load_scenario("month")), ["cashflow"])
                    self.assertEqual(planner.endpoint, endpoint.rstrip("/"))

    def test_missing_configuration_allows_startup_and_falls_back_without_network(self):
        for field in ("IBM_CLOUD_API_KEY", "WATSONX_PROJECT_ID", "WATSONX_MODEL_ID"):
            with self.subTest(field=field), patch.dict("os.environ", {field: ""}):
                with patch("elo.watsonx.urlopen") as opened:
                    planner = WatsonxPlanner()
                    report = build_report(load_scenario("month"), True, planner)
                    self.assertEqual(report["mode"], "demo_fallback")
                    opened.assert_not_called()


if __name__ == "__main__":
    unittest.main()
