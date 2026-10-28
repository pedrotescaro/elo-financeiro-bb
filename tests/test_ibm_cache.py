"""Testes de cache IAM e de inferência, relógio controlado, sem chamadas reais à IBM."""
from io import BytesIO
import json
import threading
import unittest
from unittest.mock import patch

from elo.core import load_scenario
from elo.watsonx import (
    _TokenCache, _PLAN_BUDGET,
    WatsonxPlanner,
)

ENV = {
    "IBM_CLOUD_API_KEY": "synthetic-key",
    "WATSONX_PROJECT_ID": "synthetic-project",
    "WATSONX_MODEL_ID": "synthetic-model",
    "WATSONX_URL": "https://us-south.ml.cloud.ibm.com",
}

GOOD_TOKEN = {"access_token": "tok-abc", "expires_in": 3600}
GOOD_PLAN = '{"tools":["cashflow","guidance"]}'


def resp(payload):
    return BytesIO(json.dumps(payload).encode())


def make_planner(fake_clock=None):
    """Cria WatsonxPlanner com token cache isolado e relógio injetado."""
    clock = fake_clock if fake_clock is not None else (lambda: 0.0)
    cache = _TokenCache(clock=clock)
    return WatsonxPlanner(token_cache=cache, clock=clock), cache


class TokenCacheTests(unittest.TestCase):

    def _cache(self, clock):
        return _TokenCache(clock=clock)

    def test_token_reused_within_validity_window(self):
        """Segundo plano usa token cacheado sem nova chamada IAM."""
        t = [0.0]
        def clock():
            return t[0]
        cache = self._cache(clock)
        with patch.dict("os.environ", ENV), \
             patch("elo.watsonx.urlopen", side_effect=[
                 resp(GOOD_TOKEN),
                 resp({"results": [{"generated_text": GOOD_PLAN}]}),
                 # segunda chamada de inferência — sem nova auth
                 resp({"results": [{"generated_text": GOOD_PLAN}]}),
             ]) as opened:
            planner = WatsonxPlanner(token_cache=cache, clock=clock)
            snap = load_scenario("month")
            planner.plan(snap)
            # Avança 10 s (dentro do prazo de validade)
            t[0] = 10.0
            # Invalida cache de inferência para forçar nova chamada ao modelo
            planner.invalidate_cache()
            planner.plan(snap)
        # Apenas 1 chamada IAM + 2 de inferência
        self.assertEqual(opened.call_count, 3)
        urls = [c.args[0].full_url for c in opened.call_args_list]
        iam_calls = [u for u in urls if "iam.cloud.ibm.com" in u]
        self.assertEqual(len(iam_calls), 1)

    def test_token_renewed_after_expiry_margin(self):
        """Token é renovado quando o relógio ultrapassa expires_at - margem."""
        t = [0.0]
        def clock():
            return t[0]
        cache = self._cache(clock)
        with patch.dict("os.environ", ENV), \
             patch("elo.watsonx.urlopen", side_effect=[
                 resp({"access_token": "tok-1", "expires_in": 120}),
                 resp({"results": [{"generated_text": GOOD_PLAN}]}),
                 resp({"access_token": "tok-2", "expires_in": 3600}),
                 resp({"results": [{"generated_text": GOOD_PLAN}]}),
             ]) as opened:
            planner = WatsonxPlanner(token_cache=cache, clock=clock)
            snap = load_scenario("month")
            planner.plan(snap)
            # Avança além do prazo: 120 - margem(60) = 60 s → expira em 61 s
            t[0] = 61.0
            planner.invalidate_cache()
            planner.plan(snap)
        iam_calls = [c for c in opened.call_args_list
                     if "iam.cloud.ibm.com" in c.args[0].full_url]
        self.assertEqual(len(iam_calls), 2)

    def test_token_not_renewed_just_before_margin(self):
        """Token ainda válido a 61 s do vencimento (margem=60) não é renovado."""
        t = [0.0]
        def clock():
            return t[0]
        cache = self._cache(clock)
        with patch.dict("os.environ", ENV), \
             patch("elo.watsonx.urlopen", side_effect=[
                 resp({"access_token": "tok-1", "expires_in": 200}),
                 resp({"results": [{"generated_text": GOOD_PLAN}]}),
                 # sem nova auth; segunda inferência apenas
                 resp({"results": [{"generated_text": GOOD_PLAN}]}),
             ]) as opened:
            planner = WatsonxPlanner(token_cache=cache, clock=clock)
            snap = load_scenario("month")
            planner.plan(snap)
            # Avança para 139 s: expires_at = 200, margem = 60 → válido até 140 s
            t[0] = 139.0
            planner.invalidate_cache()
            planner.plan(snap)
        iam_calls = [c for c in opened.call_args_list
                     if "iam.cloud.ibm.com" in c.args[0].full_url]
        self.assertEqual(len(iam_calls), 1)

    def test_concurrent_auth_single_call(self):
        """Threads concorrentes com token expirado realizam apenas uma chamada IAM."""
        iam_count = [0]
        count_lock = threading.Lock()

        def fake_urlopen(request, timeout, context):
            if "iam.cloud.ibm.com" in request.full_url:
                with count_lock:
                    iam_count[0] += 1
                return resp({"access_token": "tok-shared", "expires_in": 3600})
            return resp({"results": [{"generated_text": GOOD_PLAN}]})

        # Cache compartilhado entre todos os planners (simula threads da mesma sessão).
        cache = _TokenCache()
        errors = []

        def run():
            try:
                with patch.dict("os.environ", ENV), \
                     patch("elo.watsonx.urlopen", side_effect=fake_urlopen):
                    p = WatsonxPlanner(token_cache=cache)
                    p.plan(load_scenario("month"))
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=run) for _ in range(4)]
        for th in threads:
            th.start()
        for th in threads:
            th.join(timeout=10)
        self.assertFalse(errors, errors)
        # O lock garante que apenas 1 thread entra na renovação por vez.
        self.assertEqual(iam_count[0], 1)

    def test_invalid_token_response_not_cached(self):
        """Token inválido levanta exceção e não polui o cache."""
        cache = _TokenCache()
        with patch.dict("os.environ", ENV), \
             patch("elo.watsonx.urlopen", return_value=resp({"access_token": ""})):
            with self.assertRaises(ValueError):
                cache.get("synthetic-key", "")
        self.assertIsNone(cache._token)


class InferenceCacheTests(unittest.TestCase):

    def test_cache_hit_skips_network_calls(self):
        """Segundo plan() com snapshot idêntico não faz nenhuma chamada HTTP."""
        t = [0.0]
        def clock():
            return t[0]
        cache = _TokenCache(clock=clock)
        with patch.dict("os.environ", ENV), \
             patch("elo.watsonx.urlopen", side_effect=[
                 resp(GOOD_TOKEN),
                 resp({"results": [{"generated_text": GOOD_PLAN}]}),
             ]) as opened:
            planner = WatsonxPlanner(token_cache=cache, clock=clock)
            snap = load_scenario("month")
            r1 = planner.plan(snap)
            r2 = planner.plan(snap)   # cache hit — sem HTTP
        self.assertEqual(opened.call_count, 2)  # 1 auth + 1 infer
        self.assertEqual(r1, r2)

    def test_cache_invalidated_on_snapshot_change(self):
        """Snapshot diferente invalida o cache e dispara nova inferência."""
        t = [0.0]
        def clock():
            return t[0]
        cache = _TokenCache(clock=clock)
        with patch.dict("os.environ", ENV), \
             patch("elo.watsonx.urlopen", side_effect=[
                 resp(GOOD_TOKEN),
                 resp({"results": [{"generated_text": GOOD_PLAN}]}),
                 resp({"results": [{"generated_text": '{"tools":["cashflow"]}'}]}),
             ]) as opened:
            planner = WatsonxPlanner(token_cache=cache, clock=clock)
            snap1 = load_scenario("month")
            snap2 = load_scenario("month")
            snap2["balance_cents"] += 1  # muda digest
            planner.plan(snap1)
            planner.plan(snap2)
        # 1 auth + 2 inferências
        self.assertEqual(opened.call_count, 3)

    def test_failure_not_cached(self):
        """Falha de inferência não polui o cache; próxima chamada tenta novamente."""
        t = [0.0]
        def clock():
            return t[0]
        cache = _TokenCache(clock=clock)
        with patch.dict("os.environ", ENV), \
             patch("elo.watsonx.urlopen", side_effect=[
                 resp(GOOD_TOKEN),
                 resp({"results": [{"generated_text": "invalid-json"}]}),
                 resp({"results": [{"generated_text": GOOD_PLAN}]}),
             ]) as opened:
            planner = WatsonxPlanner(token_cache=cache, clock=clock)
            snap = load_scenario("month")
            with self.assertRaises((ValueError, Exception)):
                planner.plan(snap)
            result = planner.plan(snap)
        self.assertIn("cashflow", result)
        # 1 auth + 2 inferências (falha não foi cacheada)
        infer_calls = [c for c in opened.call_args_list
                       if "ml.cloud.ibm.com" in c.args[0].full_url
                       and "iam" not in c.args[0].full_url]
        self.assertEqual(len(infer_calls), 2)

    def test_cache_invalidated_by_explicit_call(self):
        """invalidate_cache() força nova inferência na próxima chamada."""
        t = [0.0]
        def clock():
            return t[0]
        cache = _TokenCache(clock=clock)
        with patch.dict("os.environ", ENV), \
             patch("elo.watsonx.urlopen", side_effect=[
                 resp(GOOD_TOKEN),
                 resp({"results": [{"generated_text": GOOD_PLAN}]}),
                 resp({"results": [{"generated_text": GOOD_PLAN}]}),
             ]) as opened:
            planner = WatsonxPlanner(token_cache=cache, clock=clock)
            snap = load_scenario("month")
            planner.plan(snap)
            planner.invalidate_cache()
            planner.plan(snap)
        infer_calls = [c for c in opened.call_args_list
                       if "ml.cloud.ibm.com" in c.args[0].full_url
                       and "iam" not in c.args[0].full_url]
        self.assertEqual(len(infer_calls), 2)

    def test_session_isolation(self):
        """Dois planners com caches separados não compartilham plano."""
        t = [0.0]
        def clock():
            return t[0]
        cache_a = _TokenCache(clock=clock)
        cache_b = _TokenCache(clock=clock)
        snap = load_scenario("month")
        with patch.dict("os.environ", ENV), \
             patch("elo.watsonx.urlopen", side_effect=[
                 resp(GOOD_TOKEN),
                 resp({"results": [{"generated_text": GOOD_PLAN}]}),
                 resp(GOOD_TOKEN),
                 resp({"results": [{"generated_text": '{"tools":["cashflow"]}'}]}),
             ]):
            pa = WatsonxPlanner(token_cache=cache_a, clock=clock)
            pb = WatsonxPlanner(token_cache=cache_b, clock=clock)
            ra = pa.plan(snap)
            rb = pb.plan(snap)
        self.assertIn("guidance", ra)
        self.assertNotIn("guidance", rb)


class BudgetTests(unittest.TestCase):

    def test_budget_consumed_by_auth_raises_timeout(self):
        """Se a autenticação consome todo o orçamento, TimeoutError é levantado."""
        # Simula relógio que avança 26 s durante a auth (> PLAN_BUDGET=25)
        calls = [0]
        def slow_clock():
            # 0 no início, 26 na primeira leitura após auth
            v = [0.0, 0.0, 26.0, 26.0]
            idx = min(calls[0], len(v) - 1)
            calls[0] += 1
            return v[idx]

        cache = _TokenCache(clock=slow_clock)
        with patch.dict("os.environ", ENV), \
             patch("elo.watsonx.urlopen", return_value=resp(GOOD_TOKEN)):
            planner = WatsonxPlanner(token_cache=cache, clock=slow_clock)
            with self.assertRaises(TimeoutError):
                planner.plan(load_scenario("month"))

    def test_generation_timeout_uses_remaining_budget(self):
        """O timeout da geração é calculado como orçamento menos tempo de auth."""
        t = [0.0]
        def clock():
            return t[0]
        cache = _TokenCache(clock=clock)
        captured = {}

        def capture_urlopen(request, timeout, context):
            if "ml.cloud.ibm.com" in request.full_url and "iam" not in request.full_url:
                captured["gen_timeout"] = timeout
            return resp(GOOD_TOKEN) if "iam" in request.full_url \
                else resp({"results": [{"generated_text": GOOD_PLAN}]})

        with patch.dict("os.environ", ENV), \
             patch("elo.watsonx.urlopen", side_effect=capture_urlopen):
            planner = WatsonxPlanner(token_cache=cache, clock=clock)
            planner.plan(load_scenario("month"))
        # Com clock estático=0, auth "levou" 0 s → remaining ≈ PLAN_BUDGET
        self.assertAlmostEqual(captured["gen_timeout"], _PLAN_BUDGET, delta=1.0)


class ServerCacheInvalidationTests(unittest.TestCase):
    """Verifica que DemoSession chama invalidate_cache ao revogar/trocar cenário."""

    def setUp(self):
        self.environment = patch.dict("os.environ", ENV, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def _make_session_with_spy(self):
        from elo.server import DemoSession
        planner = WatsonxPlanner(token_cache=_TokenCache())
        invalidated = []
        original = planner.invalidate_cache
        planner.invalidate_cache = lambda: (invalidated.append(1), original())
        session = DemoSession(planner=planner)
        session.set_consent(True)
        return session, invalidated

    def test_revoke_consent_invalidates_cache(self):
        session, invalidated = self._make_session_with_spy()
        before = len(invalidated)
        session.set_consent(False)
        self.assertGreater(len(invalidated), before)

    def test_set_scenario_invalidates_cache(self):
        session, invalidated = self._make_session_with_spy()
        before = len(invalidated)
        session.set_scenario("month")
        self.assertGreater(len(invalidated), before)


if __name__ == "__main__":
    unittest.main()
