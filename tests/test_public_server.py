"""Controles da demonstração pública exercitados só por conexões locais."""
from http.client import HTTPConnection
from http.cookies import SimpleCookie
import json
import socket
from threading import Event, Thread
import unittest

from elo.server import DemoServer, DemoSession, Handler


PUBLIC_ORIGIN = "https://elo-demo.example"


class FakeClock:
    """Relógio monotônico controlado: expiração sem esperas reais."""

    def __init__(self):
        self.now = 1000

    def __call__(self):
        return self.now


class PublicServerTests(unittest.TestCase):
    def start_server(self, *, public_origin=PUBLIC_ORIGIN, **options):
        self.clock = FakeClock()
        self.server = DemoServer(("127.0.0.1", 0), public_origin=public_origin, clock=self.clock, **options)
        self.host = "elo-demo.example" if public_origin else "127.0.0.1:" + str(self.server.server_port)
        self.thread = Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
        self.thread.start()

        def stop():
            self.server.shutdown()
            self.server.server_close()
            self.thread.join(timeout=2)

        self.addCleanup(stop)

    def request(self, path="/api/state", method="GET", payload=None, *, headers=None, host=None):
        connection = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        request_headers = {"Host": self.host if host is None else host}
        request_headers.update(headers or {})
        body = json.dumps(payload).encode() if payload is not None else None
        if body is not None:
            request_headers.setdefault("Content-Type", "application/json")
        try:
            connection.request(method, path, body=body, headers=request_headers)
            response = connection.getresponse()
            result = response.read()
            return response.status, dict((k.lower(), v) for k, v in response.getheaders()), result
        finally:
            connection.close()

    def bootstrap(self):
        status, headers, body = self.request()
        self.assertEqual(status, 200)
        cookies = SimpleCookie(headers["set-cookie"])
        return json.loads(body), "elo_demo=" + cookies["elo_demo"].value

    def post(self, state, cookie, path, payload, origin=PUBLIC_ORIGIN):
        headers = {"Cookie": cookie, "X-Demo-CSRF": state["csrf"]}
        if origin is not None:
            headers["Origin"] = origin
        return self.request(path, "POST", payload, headers=headers)

    def test_public_cookie_and_security_headers_cover_success_and_error(self):
        self.start_server()
        for path, expected in [("/api/state", 200), ("/missing", 404)]:
            status, headers, _ = self.request(path)
            self.assertEqual(status, expected)
            for name in ("content-security-policy", "referrer-policy", "permissions-policy",
                         "x-frame-options", "x-content-type-options", "strict-transport-security"):
                self.assertIn(name, headers)
            self.assertEqual(headers["cache-control"], "no-store")
            self.assertIn("Origin", headers["vary"])
            self.assertNotIn("access-control-allow-origin", headers)
            if path == "/api/state":
                cookie = SimpleCookie(headers["set-cookie"])["elo_demo"]
                self.assertTrue(cookie["secure"])
                self.assertTrue(cookie["httponly"])
                self.assertEqual(cookie["samesite"], "Strict")

    def test_public_post_requires_exact_configured_origin(self):
        self.start_server()
        state, cookie = self.bootstrap()
        for origin in [None, "null", "http://elo-demo.example", "https://elsewhere.example",
                       PUBLIC_ORIGIN + "/", PUBLIC_ORIGIN + ":443"]:
            with self.subTest(origin=origin):
                status, _, _ = self.post(state, cookie, "/api/consent", {"enabled": True}, origin)
                self.assertEqual(status, 403)
        status, _, body = self.post(state, cookie, "/api/consent", {"enabled": True})
        self.assertEqual(status, 200)
        self.assertTrue(json.loads(body)["consent"])

    def test_host_header_cannot_change_public_cookie_policy_or_origin(self):
        self.start_server()
        for host in ["localhost", "127.0.0.1", "elo-demo.example.evil", "attacker.example"]:
            with self.subTest(host=host):
                status, _, _ = self.request(host=host)
                self.assertEqual(status, 403)
        self.assertEqual(len(self.server.sessions), 0)

    def test_local_mode_checks_host_and_preserves_http_cookie(self):
        self.start_server(public_origin=None)
        status, headers, _ = self.request()
        self.assertEqual(status, 200)
        self.assertFalse(SimpleCookie(headers["set-cookie"])["elo_demo"]["secure"])
        for host in ["attacker.example", "localhost.evil", "127.0.0.1:1"]:
            with self.subTest(host=host):
                self.assertEqual(self.request(host=host)[0], 403)

    def test_rate_limit_returns_retry_after_and_window_reopens(self):
        self.start_server(rate_limit=2, rate_window=60)
        self.assertEqual(self.request()[0], 200)
        self.assertEqual(self.request()[0], 200)
        status, headers, _ = self.request()
        self.assertEqual(status, 429)
        self.assertGreater(int(headers["retry-after"]), 0)
        self.assertLessEqual(int(headers["retry-after"]), 60)
        self.assertEqual(len(self.server.sessions), 2)
        self.clock.now += 60
        self.assertEqual(self.request()[0], 200)

    def test_health_does_not_create_sessions_or_consume_rate_limit(self):
        self.start_server(rate_limit=1)
        for _ in range(4):
            self.assertEqual(self.request("/healthz", host="internal-probe")[0], 200)
        self.assertEqual(self.server.sessions, {})
        self.assertEqual(self.server.ip_windows, {})
        self.assertEqual(self.request()[0], 200)
        self.assertEqual(self.request("/healthz")[0], 200)
        self.assertEqual(self.request()[0], 429)

    def test_idle_expiry_discards_plans_and_changes_csrf(self):
        self.start_server(session_ttl=30)
        state, cookie = self.bootstrap()
        status, _, body = self.post(state, cookie, "/api/consent", {"enabled": True})
        self.assertEqual(status, 200)
        state = json.loads(body)
        status, _, _ = self.post(state, cookie, "/api/approve", {
            "report_id": state["report"]["report_id"], "action_id": "budget-plan",
        })
        self.assertEqual(status, 200)
        self.clock.now += 30
        status, headers, body = self.request(headers={"Cookie": cookie})
        self.assertEqual(status, 200)
        renewed = json.loads(body)
        self.assertNotEqual(renewed["csrf"], state["csrf"])
        self.assertFalse(renewed["consent"])
        self.assertEqual(renewed["history"], [])
        self.assertEqual(renewed["goals"], [])
        self.assertEqual(len(self.server.sessions), 1)
        new_cookie = "elo_demo=" + SimpleCookie(headers["set-cookie"])["elo_demo"].value
        self.assertEqual(self.post(state, new_cookie, "/api/consent", {"enabled": True})[0], 403)

    def test_recent_activity_extends_idle_expiration(self):
        self.start_server(session_ttl=30)
        state, cookie = self.bootstrap()
        for _ in range(2):
            self.clock.now += 29
            status, _, body = self.request(headers={"Cookie": cookie})
            self.assertEqual(status, 200)
            self.assertEqual(json.loads(body)["csrf"], state["csrf"])
        self.clock.now += 30
        self.assertNotEqual(json.loads(self.request(headers={"Cookie": cookie})[2])["csrf"], state["csrf"])

    def test_expired_sessions_release_the_hundred_session_limit(self):
        self.start_server(session_ttl=30)
        for i in range(100):
            session = DemoSession()
            session.last_seen = self.clock()
            self.server.sessions[str(i)] = session
        self.assertEqual(self.request()[0], 503)
        self.assertEqual(len(self.server.sessions), 100)
        self.clock.now += 30
        self.assertEqual(self.request()[0], 200)
        self.assertEqual(len(self.server.sessions), 1)

    def test_duplicate_content_length_is_rejected(self):
        self.start_server()
        state, cookie = self.bootstrap()
        connection = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        self.addCleanup(connection.close)
        connection.putrequest("POST", "/api/monitor", skip_host=True)
        for name, value in [("Host", self.host), ("Origin", PUBLIC_ORIGIN), ("Cookie", cookie),
                            ("X-Demo-CSRF", state["csrf"]), ("Content-Type", "application/json"),
                            ("Content-Length", "2"), ("Content-Length", "2")]:
            connection.putheader(name, value)
        connection.endheaders(b"{}")
        response = connection.getresponse()
        self.assertEqual(response.status, 400)
        response.read()

    def test_non_json_transfer_encoding_and_oversized_body_are_rejected(self):
        self.start_server()
        state, cookie = self.bootstrap()
        headers = {"Cookie": cookie, "X-Demo-CSRF": state["csrf"], "Origin": PUBLIC_ORIGIN}
        for extra in [{"Content-Type": "text/plain"}, {"Transfer-Encoding": "chunked"},
                      {"Content-Length": "8193"}, {"Content-Length": "invalid"}, {"Content-Length": "0"}]:
            with self.subTest(headers=extra):
                status, _, _ = self.request("/api/monitor", "POST", {}, headers={**headers, **extra})
                self.assertEqual(status, 400)

    def test_workers_are_bounded_and_released_after_handler_failure(self):
        self.start_server(max_workers=1)
        entered, release, finished = Event(), Event(), Event()

        def blocking_handler(request, address, server):
            entered.set()
            release.wait(timeout=2)
            raise RuntimeError("synthetic handler failure")

        original = self.server.process_request_thread

        def tracked(*args):
            try:
                original(*args)
            finally:
                finished.set()

        self.server.process_request_thread = tracked
        self.server.RequestHandlerClass = blocking_handler
        self.server.handle_error = lambda *args: None
        client = socket.create_connection(self.server.server_address, timeout=3)
        self.addCleanup(client.close)
        self.addCleanup(release.set)
        self.assertTrue(entered.wait(timeout=2))
        self.assertEqual(self.request("/healthz")[0], 503)
        self.server.RequestHandlerClass = Handler
        release.set()
        self.assertTrue(finished.wait(timeout=2))
        self.assertEqual(self.request("/healthz")[0], 200)


class PublicConfigurationTests(unittest.TestCase):
    def test_public_mode_refuses_external_planner(self):
        with self.assertRaises(ValueError):
            DemoServer(("127.0.0.1", 0), planner=object(), public_origin=PUBLIC_ORIGIN)

    def test_public_origin_must_be_an_https_origin(self):
        for origin in ["http://elo-demo.example", "https://", "https://user@elo-demo.example",
                       "https://elo-demo.example/path", PUBLIC_ORIGIN + "?query=x", PUBLIC_ORIGIN + "#fragment"]:
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                DemoServer(("127.0.0.1", 0), public_origin=origin)

    def test_rate_limit_storage_is_bounded_and_recovers_after_expiry(self):
        clock = FakeClock()
        server = DemoServer(("127.0.0.1", 0), clock=clock)
        self.addCleanup(server.server_close)
        for i in range(1024):
            self.assertTrue(server.check_rate(f"2001:db8::{i:x}"))
        self.assertFalse(server.check_rate("198.51.100.1"))
        self.assertLessEqual(len(server.ip_windows), 1024)
        clock.now += 60
        self.assertTrue(server.check_rate("198.51.100.1"))
        self.assertLessEqual(len(server.ip_windows), 1024)

    def test_accepted_connections_have_a_bounded_read_timeout(self):
        server = DemoServer(("127.0.0.1", 0))
        self.addCleanup(server.server_close)
        client = socket.create_connection(server.server_address, timeout=3)
        self.addCleanup(client.close)
        accepted, _ = server.get_request()
        self.addCleanup(accepted.close)
        self.assertIsNotNone(accepted.gettimeout())
        self.assertGreater(accepted.gettimeout(), 0)
        self.assertLessEqual(accepted.gettimeout(), 30)


if __name__ == "__main__":
    unittest.main()
