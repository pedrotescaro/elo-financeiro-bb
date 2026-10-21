"""Regressões de limites HTTP e concorrência de sessões."""

from concurrent.futures import ThreadPoolExecutor
from http.client import HTTPConnection
import json
from threading import Event, RLock, Thread
from time import monotonic
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from elo.core import apply_saving, build_report, load_scenario
from elo.server import DemoServer, DemoSession, Handler


class SessionLockTests(unittest.TestCase):
    def test_slow_new_session_does_not_block_existing_session(self):
        existing = DemoSession()
        server = SimpleNamespace(sessions={"existing": existing}, sessions_lock=RLock(), planner=None,
                                 clock=monotonic, expire_sessions=lambda now: None)
        started, release = Event(), Event()

        def handler(cookie=""):
            instance = Handler.__new__(Handler)
            instance.server = server
            instance.headers = {"Cookie": cookie}
            return instance

        def slow_constructor(_planner):
            started.set()
            release.wait(3)
            return DemoSession()

        with ThreadPoolExecutor(max_workers=2) as pool:
            with patch("elo.server.DemoSession", side_effect=slow_constructor):
                future = pool.submit(handler().get_session)
                try:
                    self.assertTrue(started.wait(2))
                    response = pool.submit(handler("elo_demo=existing").get_session)
                    self.assertIs(response.result(timeout=1)[0], existing)
                finally:
                    release.set()
                self.assertIsInstance(future.result(timeout=2)[0], DemoSession)

    def test_unhashable_approval_identifiers_are_rejected(self):
        session = DemoSession()
        session.set_consent(True)
        with self.assertRaises(ValueError):
            session.approve({}, [])

    def test_model_cannot_mutate_financial_snapshot(self):
        class MutatingPlanner:
            def plan(self, snapshot):
                snapshot["balance_cents"] = 99999999
                return ["cashflow"]

        snapshot = load_scenario("month")
        report = build_report(snapshot, True, MutatingPlanner())
        self.assertEqual(snapshot["balance_cents"], 150000)
        self.assertEqual(report["results"]["cashflow"]["minimum_cents"], -10000)

    def test_savings_do_not_change_bills_outside_horizon(self):
        snapshot = load_scenario("month")
        snapshot["events"][3]["date"] = "2026-11-01"
        with self.assertRaises(ValueError):
            apply_saving(snapshot, 100)


class InputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = DemoServer(("127.0.0.1", 0))
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.client = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        self.addCleanup(self.client.close)
        self.client.request("GET", "/api/state")
        response = self.client.getresponse()
        cookie = response.getheader("Set-Cookie")
        self.headers = {
            "Cookie": cookie.split(";", 1)[0],
            "X-Demo-CSRF": json.loads(response.read())["csrf"],
            "Content-Type": "application/json",
        }

    def test_invalid_lengths_rejected_with_clear_message(self):
        for length in ("no", "-1", "0", "8193"):
            with self.subTest(length=length):
                self.client.request(
                    "POST", "/api/consent", body=b"{}", headers={**self.headers, "Content-Length": length}
                )
                response = self.client.getresponse()
                self.assertEqual(response.status, 400)
                self.assertIn("error", json.loads(response.read()))

    def test_non_json_content_type_rejected(self):
        self.client.request("POST", "/api/consent", body=b"{}", headers={**self.headers, "Content-Type": "text/plain"})
        response = self.client.getresponse()
        self.assertEqual(response.status, 400)
        self.assertIn("application/json", json.loads(response.read())["error"])

    def test_external_and_null_origins_rejected(self):
        for origin in ("https://example.com", "null"):
            self.client.request("POST", "/api/consent", body=b"{}", headers={**self.headers, "Origin": origin})
            response = self.client.getresponse()
            self.assertEqual(response.status, 403)
            response.read()

    def test_invalid_utf8_rejected(self):
        self.client.request("POST", "/api/consent", body=b"\xff", headers=self.headers)
        response = self.client.getresponse()
        self.assertEqual(response.status, 400)
        self.assertIn("UTF-8", json.loads(response.read())["error"])

    def test_unknown_api_path_is_not_a_file_reader(self):
        self.client.request("GET", "/api/../../data/scenarios.json")
        response = self.client.getresponse()
        self.assertEqual(response.status, 404)
        response.read()
