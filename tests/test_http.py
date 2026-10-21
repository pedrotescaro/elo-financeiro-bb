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


if __name__ == "__main__":
    unittest.main()
