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
        self.client = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
        with self.client.open(self.base + "/api/state") as response:
            self.state = json.load(response)

    def post(self, path, payload, token=None):
        request = Request(self.base + path, data=json.dumps(payload).encode(),
                          headers={"Content-Type":"application/json", "X-Demo-CSRF": token or self.state["csrf"]})
        with self.client.open(request) as response: return json.load(response)

    def test_complete_consent_approval_monitoring_flow(self):
        state = self.post("/api/consent", {"enabled":True})
        state = self.post("/api/approve", {"report_id":state["report"]["report_id"], "action_id":"budget-plan"})
        self.assertEqual(state["report"]["results"]["cashflow"]["minimum_cents"], 20000)
        state = self.post("/api/monitor", {})
        self.assertEqual(state["report"]["results"]["cashflow"]["minimum_cents"], 5000)

    def test_invalid_csrf_rejected(self):
        with self.assertRaises(HTTPError) as error:
            self.post("/api/consent", {"enabled":True}, "wrong")
        self.assertEqual(error.exception.code, 403)

    def test_invalid_body_rejected(self):
        with self.assertRaises(HTTPError) as error:
            self.post("/api/consent", {"enabled":"yes"})
        self.assertEqual(error.exception.code, 400)

    def test_static_path_traversal_rejected(self):
        with self.assertRaises(HTTPError) as error: self.client.open(self.base + "/../data/scenarios.json")
        self.assertEqual(error.exception.code, 404)


if __name__ == "__main__": unittest.main()
