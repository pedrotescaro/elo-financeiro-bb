"""Servidor local de demonstração. Sem autenticação bancária ou uso em produção."""
import argparse
from copy import deepcopy
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import secrets
from threading import RLock
from urllib.parse import urlsplit
from .core import CATALOG, ROOT, apply_saving, build_report, load_scenario


class DemoSession:
    def __init__(self, planner=None):
        self.lock = RLock()
        self.csrf = secrets.token_urlsafe(24)
        self.consent = False
        self.name = "month"
        self.snapshot = load_scenario(self.name)
        self.planner = planner
        self.report = build_report(self.snapshot, False)
        self.approved = {}
        self.history = []
        self.goals = []

    def refresh(self):
        self.report = build_report(self.snapshot, self.consent, self.planner)

    def public_state(self):
        return {"scenario": self.name, "scenario_title": self.snapshot["title"],
                "scenarios": [{"id": k, "title": v["title"]} for k, v in CATALOG.items()],
                "consent": self.consent, "csrf": self.csrf, "report": deepcopy(self.report),
                "history": deepcopy(self.history), "goals": deepcopy(self.goals),
                "synthetic": True, "monitoring": "Simulado por evento acionado na interface"}

    def set_consent(self, enabled):
        if type(enabled) is not bool:
            raise ValueError("Consentimento inválido.")
        self.consent = enabled
        if not enabled:
            self.history.clear()
            self.goals.clear()
            self.approved.clear()
            self.snapshot = load_scenario(self.name)
        self.refresh()

    def set_scenario(self, name):
        self.snapshot = load_scenario(name)
        self.name = name
        self.approved.clear()
        self.history.clear()
        self.goals.clear()
        self.refresh()

    def approve(self, report_id, action_id):
        if not self.consent:
            raise PermissionError("Autorize a leitura antes de aprovar um plano.")
        key = (report_id, action_id)
        if key in self.approved:
            return self.approved[key]
        if report_id != self.report.get("report_id"):
            raise ValueError("Os dados mudaram. Revise a nova recomendação antes de aprovar.")
        action = next((a for a in self.report["actions"] if a["id"] == action_id), None)
        if not action:
            raise ValueError("Ação não permitida.")
        # Valores vêm do plano no servidor, nunca de parâmetros do navegador.
        if action_id == "budget-plan":
            self.snapshot = apply_saving(self.snapshot, action["reduction_cents"])
        elif action_id == "purchase-goal":
            self.goals.append({"label": self.snapshot["purchase"]["label"], "target_cents": action["target_cents"]})
        else:
            raise ValueError("Ação não permitida.")
        record = {"action": action_id, "report_id": report_id, "label": action["label"],
                  "status": "accepted", "effect": action["effect"]}
        self.history.append(record)
        self.approved[key] = record
        self.refresh()
        # Uma meta é suficiente para a demonstração da mesma compra.
        if self.goals:
            self.report["actions"] = [a for a in self.report["actions"] if a["id"] != "purchase-goal"]
        return record

    def monitor(self):
        if not self.consent:
            raise PermissionError("A leitura está desativada.")
        if any(e["id"] == "new-spend" for e in self.snapshot["events"]):
            raise ValueError("Este evento já foi simulado. Reinicie o cenário para repetir.")
        self.snapshot["events"].append({"id": "new-spend", "date": "2026-10-14",
            "label": "Despesa imprevista simulada", "amount_cents": 15000,
            "direction": "out", "flexible": False})
        self.history.append({"label": "Nova despesa simulada: R$ 150,00", "status": "observed"})
        self.refresh()


class DemoServer(ThreadingHTTPServer):
    def __init__(self, address, planner=None):
        self.sessions = {}
        self.sessions_lock = RLock()
        self.planner = planner
        super().__init__(address, Handler)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Não grava dados financeiros, tokens ou conteúdo de requisições.
        pass

    def get_session(self):
        cookies = SimpleCookie()
        try:
            cookies.load(self.headers.get("Cookie", ""))
        except Exception:
            cookies = SimpleCookie()
        item = cookies.get("elo_demo")
        key = item.value if item else None
        with self.server.sessions_lock:
            if key not in self.server.sessions:
                if len(self.server.sessions) >= 100:
                    raise RuntimeError("Limite de sessões da demonstração atingido.")
                key = secrets.token_urlsafe(24)
                self.server.sessions[key] = DemoSession(self.server.planner)
                self.new_cookie = key
            return self.server.sessions[key]

    def send_bytes(self, status, content, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'")
        if getattr(self, "new_cookie", None):
            self.send_header("Set-Cookie", f"elo_demo={self.new_cookie}; HttpOnly; SameSite=Strict; Path=/")
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, status, payload):
        self.send_bytes(status, json.dumps(payload, ensure_ascii=False).encode(), "application/json; charset=utf-8")

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/state":
            try:
                session = self.get_session()
                with session.lock:
                    self.send_json(200, session.public_state())
            except RuntimeError:
                self.send_json(503, {"error": "A demonstração está ocupada."})
            return
        routes = {"/": ("index.html", "text/html"), "/app.js": ("app.js", "text/javascript"),
                  "/style.css": ("style.css", "text/css")}
        if path not in routes:
            self.send_json(404, {"error": "Recurso não encontrado."})
            return
        name, mime = routes[path]
        self.send_bytes(200, (ROOT / "web" / name).read_bytes(), mime + "; charset=utf-8")

    def do_POST(self):
        try:
            session = self.get_session()
            token = self.headers.get("X-Demo-CSRF", "")
            if not secrets.compare_digest(token, session.csrf):
                raise PermissionError("Sessão inválida. Atualize a página.")
            origin = self.headers.get("Origin")
            if origin and urlsplit(origin).netloc != self.headers.get("Host"):
                raise PermissionError("Origem não permitida.")
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 8192:
                raise ValueError("Tamanho inválido.")
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict):
                raise ValueError("Envie um objeto JSON.")
            path = urlsplit(self.path).path
            with session.lock:
                if path == "/api/consent":
                    session.set_consent(payload.get("enabled"))
                elif path == "/api/scenario":
                    session.set_scenario(payload.get("name"))
                elif path == "/api/approve":
                    rid, aid = payload.get("report_id"), payload.get("action_id")
                    if not isinstance(rid, str) or not isinstance(aid, str):
                        raise ValueError("Identificador inválido.")
                    session.approve(rid, aid)
                elif path == "/api/monitor":
                    session.monitor()
                else:
                    self.send_json(404, {"error": "Ação não encontrada."})
                    return
                self.send_json(200, session.public_state())
        except PermissionError as exc:
            self.send_json(403, {"error": str(exc)})
        except (ValueError, KeyError, TypeError):
            self.send_json(400, {"error": "Requisição inválida ou recomendação desatualizada. Revise a página."})
        except RuntimeError:
            self.send_json(503, {"error": "A demonstração está ocupada."})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    planner = None
    if os.environ.get("ELO_PLANNER") == "watsonx":
        from .watsonx import WatsonxPlanner
        planner = WatsonxPlanner()
    print(f"Elo Financeiro: http://{args.host}:{args.port} | dados sintéticos")
    DemoServer((args.host, args.port), planner).serve_forever()


if __name__ == "__main__":
    main()
