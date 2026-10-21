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

_MAX_SESSION_NAME_LEN = 40


class DemoSession:
    """Estado isolado de uma sessão de demonstração. Thread-safe via lock próprio."""

    def __init__(self, planner: object = None) -> None:
        self.lock = RLock()
        self.csrf = secrets.token_urlsafe(24)
        self.consent = False
        self.name = "month"
        self.snapshot = load_scenario(self.name)
        self.planner = planner
        self.report = build_report(self.snapshot, False)
        self.approved: dict = {}
        self.history: list = []
        self.goals: list = []

    def refresh(self) -> None:
        """Reconstrói o relatório com base no snapshot e no consentimento atuais."""
        self.report = build_report(self.snapshot, self.consent, self.planner)

    def public_state(self) -> dict:
        """Retorna o estado serializável para o navegador."""
        return {"scenario": self.name, "scenario_title": self.snapshot["title"],
                "scenarios": [{"id": k, "title": v["title"]} for k, v in CATALOG.items()],
                "consent": self.consent, "csrf": self.csrf, "report": deepcopy(self.report),
                "history": deepcopy(self.history), "goals": deepcopy(self.goals),
                "synthetic": True, "monitoring": "Simulado por evento acionado na interface"}

    def set_consent(self, enabled: bool) -> None:
        """Ativa ou revoga o consentimento demonstrativo."""
        if type(enabled) is not bool:
            raise ValueError("Consentimento inválido.")
        self.consent = enabled
        if not enabled:
            self.history.clear()
            self.goals.clear()
            self.approved.clear()
            self.snapshot = load_scenario(self.name)
        self.refresh()

    def set_scenario(self, name: str) -> None:
        """Troca o cenário ativo e reinicia o estado da sessão."""
        if not isinstance(name, str) or not name or len(name) > _MAX_SESSION_NAME_LEN:
            raise ValueError("Nome de cenário inválido.")
        self.snapshot = load_scenario(name)  # levanta ValueError se desconhecido
        self.name = name
        self.approved.clear()
        self.history.clear()
        self.goals.clear()
        self.refresh()

    def approve(self, report_id: str, action_id: str) -> dict:
        """Executa a ação aprovada vinculada ao relatório vigente."""
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

    def monitor(self) -> None:
        """Simula uma nova despesa e reavalia a projeção."""
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
    """Servidor ThreadingHTTP com mapa de sessões protegido por lock."""

    def __init__(self, address: tuple, planner: object = None) -> None:
        self.sessions: dict = {}
        self.sessions_lock = RLock()
        self.planner = planner
        super().__init__(address, Handler)


class Handler(BaseHTTPRequestHandler):
    """Lida com requisições individuais da demonstração."""

    def log_message(self, fmt: str, *args: object) -> None:
        # Não grava dados financeiros, tokens ou conteúdo de requisições.
        pass

    def get_session(self) -> "DemoSession":
        """Retorna a sessão existente ou cria uma nova sob o lock global."""
        cookies = SimpleCookie()
        try:
            cookies.load(self.headers.get("Cookie", ""))
        except Exception:
            cookies = SimpleCookie()
        item = cookies.get("elo_demo")
        key = item.value if item else None

        with self.server.sessions_lock:
            session = self.server.sessions.get(key)
            if session is not None:
                return session
            if len(self.server.sessions) >= 100:
                raise RuntimeError("Limite de sessões da demonstração atingido.")
            new_key = secrets.token_urlsafe(24)
            new_session = DemoSession(self.server.planner)
            self.server.sessions[new_key] = new_session

        self._new_cookie = new_key
        return new_session

    def send_bytes(self, status: int, content: bytes, content_type: str,
                   new_cookie: "str | None" = None) -> None:
        """Envia uma resposta com cabeçalhos de segurança padrão."""
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'",
        )
        if new_cookie:
            # Adiciona Secure apenas quando servido via HTTPS (produção).
            # Em HTTP local o flag Secure impede que o cookie seja enviado de volta.
            host = self.headers.get("Host", "")
            secure_flag = "" if host.startswith("127.0.0.1") or host.startswith("localhost") else "; Secure"
            self.send_header(
                "Set-Cookie",
                f"elo_demo={new_cookie}; HttpOnly; SameSite=Strict{secure_flag}; Path=/",
            )
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, status: int, payload: object,
                  new_cookie: "str | None" = None) -> None:
        """Serializa payload como JSON e envia via send_bytes."""
        self.send_bytes(
            status,
            json.dumps(payload, ensure_ascii=False).encode(),
            "application/json; charset=utf-8",
            new_cookie=new_cookie,
        )

    def do_GET(self) -> None:
        new_cookie = None
        path = urlsplit(self.path).path
        if path == "/api/state":
            try:
                self._new_cookie = None
                session = self.get_session()
                new_cookie = getattr(self, "_new_cookie", None)
                with session.lock:
                    self.send_json(200, session.public_state(), new_cookie=new_cookie)
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

    def do_POST(self) -> None:
        new_cookie = None
        try:
            self._new_cookie = None
            session = self.get_session()
            new_cookie = getattr(self, "_new_cookie", None)
            token = self.headers.get("X-Demo-CSRF", "")
            if not secrets.compare_digest(token, session.csrf):
                raise PermissionError("Sessão inválida. Atualize a página.")
            origin = self.headers.get("Origin")
            if origin and urlsplit(origin).netloc != self.headers.get("Host"):
                raise PermissionError("Origem não permitida.")
            raw_len = self.headers.get("Content-Length", "")
            try:
                size = int(raw_len)
            except (ValueError, TypeError):
                raise ValueError("Cabeçalho Content-Length inválido.")
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
                self.send_json(200, session.public_state(), new_cookie=new_cookie)
        except PermissionError as exc:
            self.send_json(403, {"error": str(exc)})
        except (ValueError, KeyError, TypeError):
            self.send_json(400, {"error": "Requisição inválida ou recomendação desatualizada. Revise a página."})
        except RuntimeError:
            self.send_json(503, {"error": "A demonstração está ocupada."})


def main() -> None:
    """Ponto de entrada para `python -m elo.server`."""
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
