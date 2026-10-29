"""Demonstração sintética limitada; modo público requer proxy HTTPS configurado."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from math import ceil
import os
import secrets
from threading import BoundedSemaphore, RLock
from time import monotonic
from typing import Callable
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
        self.audit: list = []
        self.audit_sequence = 0
        self.last_seen = monotonic()
        self.record("session_started", "Sessão demonstrativa iniciada, sem leitura autorizada.")

    def record(self, event: str, label: str) -> None:
        """Mantém até 200 eventos observáveis, sem prompts, tokens ou valores privados."""
        self.audit_sequence += 1
        self.audit.append({"sequence": self.audit_sequence,
                           "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                           "event": event, "label": label})
        del self.audit[:-200]

    def refresh(self) -> None:
        """Reconstrói o relatório com base no snapshot e no consentimento atuais."""
        self.report = build_report(self.snapshot, self.consent, self.planner)
        if self.consent:
            tools = ", ".join(t["tool"] for t in self.report["trace"])
            self.record("tools_consulted", "Consultas realizadas com leitura autorizada: " + tools + ".")
        if self.goals:
            self.report["actions"] = [a for a in self.report["actions"] if a["id"] != "purchase-goal"]

    def public_state(self) -> dict:
        """Retorna o estado serializável para o navegador."""
        return {"scenario": self.name, "scenario_title": self.snapshot["title"],
                "scenarios": [{"id": k, "title": v["title"]} for k, v in CATALOG.items()],
                "consent": self.consent, "csrf": self.csrf, "report": deepcopy(self.report),
                "history": deepcopy(self.history), "goals": deepcopy(self.goals), "audit": deepcopy(self.audit),
                "synthetic": True, "monitoring": "Simulado por evento acionado na interface",
                "monitor_done": any(e["id"] == "new-spend" for e in self.snapshot["events"])}

    def set_consent(self, enabled: bool) -> None:
        """Ativa ou revoga o consentimento demonstrativo."""
        if type(enabled) is not bool:
            raise ValueError("Consentimento inválido.")
        self.consent = enabled
        self.record("consent_granted" if enabled else "consent_revoked",
                    "Leitura dos dados fictícios autorizada." if enabled else
                    "Leitura revogada; planos e metas desta sessão foram limpos.")
        if not enabled:
            self.history.clear()
            self.goals.clear()
            self.approved.clear()
            self.snapshot = load_scenario(self.name)
            if hasattr(self.planner, "invalidate_cache"):
                self.planner.invalidate_cache()
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
        if hasattr(self.planner, "invalidate_cache"):
            self.planner.invalidate_cache()
        self.record("scenario_selected", "Cenário selecionado: " + self.snapshot["title"] + ".")
        self.refresh()

    def approve(self, report_id: str, action_id: str) -> dict:
        """Executa a ação aprovada vinculada ao relatório vigente."""
        if not self.consent:
            raise PermissionError("Autorize a leitura antes de aprovar um plano.")
        if not isinstance(report_id, str) or not 1 <= len(report_id) <= 64:
            raise ValueError("Identificador do relatório inválido.")
        if not isinstance(action_id, str) or not 1 <= len(action_id) <= 40:
            raise ValueError("Identificador da ação inválido.")
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
        self.record("action_approved", "Ação autorizada: " + action["label"] + ".")
        self.refresh()
        return record

    def decline(self, report_id: str, action_id: str) -> dict:
        """Registra a recusa explícita de uma ação sem alterar o snapshot."""
        if not self.consent:
            raise PermissionError("Autorize a leitura antes de recusar um plano.")
        if not isinstance(report_id, str) or not 1 <= len(report_id) <= 64:
            raise ValueError("Identificador do relatório inválido.")
        if not isinstance(action_id, str) or not 1 <= len(action_id) <= 40:
            raise ValueError("Identificador da ação inválido.")
        if report_id != self.report.get("report_id"):
            raise ValueError("Os dados mudaram. Revise a nova recomendação antes de recusar.")
        action = next((a for a in self.report["actions"] if a["id"] == action_id), None)
        if not action:
            raise ValueError("Ação não encontrada.")
        record = {"action": action_id, "report_id": report_id, "label": action["label"],
                  "status": "declined", "effect": "Proposta recusada; nenhuma alteração foi feita."}
        self.history.append(record)
        self.record("action_declined", "Proposta recusada pelo usuário: " + action["label"] + ".")
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
        self.record("event_observed", "Nova despesa fictícia informada; projeção reavaliada.")
        self.refresh()


class DemoServer(ThreadingHTTPServer):
    """Servidor ThreadingHTTP com mapa de sessões protegido por lock."""

    def __init__(self, address: tuple, planner: object = None, *, public_origin: str | None = None,
                 session_ttl: int = 1800, rate_limit: int = 120, rate_window: int = 60,
                 max_workers: int = 16, clock: Callable[[], float] = monotonic) -> None:
        if public_origin:
            origin = urlsplit(public_origin)
            if (origin.scheme != "https" or not origin.hostname or origin.username or origin.password
                    or origin.path or origin.query or origin.fragment or origin.port not in (None, 443)
                    or public_origin != "https://" + origin.netloc):
                raise ValueError("ELO_PUBLIC_ORIGIN deve ser uma origem HTTPS sem caminho ou barra final.")
            if planner is not None:
                raise ValueError("A demonstração pública permite somente o modo por regras, sem chamadas IBM.")
        if any(type(n) is not int or n <= 0 for n in (session_ttl, rate_limit, rate_window, max_workers)):
            raise ValueError("Os limites da demonstração devem ser inteiros positivos.")
        self.sessions: dict = {}
        self.sessions_lock = RLock()
        self.planner = planner
        self.public_origin = public_origin
        self.session_ttl = session_ttl
        self.rate_limit, self.rate_window = rate_limit, rate_window
        self.clock = clock
        self.ip_windows: dict = {}
        self.rate_lock = RLock()
        self.workers = BoundedSemaphore(max_workers)
        super().__init__(address, Handler)

    def expire_sessions(self, now: float) -> None:
        """Remove sessões inativas sob o lock do mapa, liberando sua memória."""
        expired = [key for key, session in self.sessions.items() if now - session.last_seen >= self.session_ttl]
        for key in expired:
            del self.sessions[key]

    def check_rate(self, ip: str) -> bool:
        """Aplica janela fixa por IP da conexão, com memória limitada a 1024 IPs."""
        now = self.clock()
        with self.rate_lock:
            expired = [key for key, (start, _) in self.ip_windows.items() if now - start >= self.rate_window]
            for key in expired:
                del self.ip_windows[key]
            if ip not in self.ip_windows:
                if len(self.ip_windows) >= 1024:
                    return False
                self.ip_windows[ip] = (now, 0)
            start, count = self.ip_windows[ip]
            if count >= self.rate_limit:
                return False
            self.ip_windows[ip] = (start, count + 1)
            return True

    def get_request(self) -> tuple:
        """Limita a espera de cabeçalhos e corpo em cada conexão."""
        connection, address = super().get_request()
        connection.settimeout(10)
        return connection, address

    def process_request(self, request: object, client_address: tuple) -> None:
        """Rejeita excesso de conexões antes de criar uma thread."""
        if not self.workers.acquire(blocking=False):
            try:
                request.settimeout(1)
                request.sendall(b"HTTP/1.0 503 Service Unavailable\r\nContent-Length: 0\r\n"
                                b"Connection: close\r\nRetry-After: 1\r\nCache-Control: no-store\r\n"
                                b"X-Content-Type-Options: nosniff\r\nX-Frame-Options: DENY\r\n"
                                b"Referrer-Policy: no-referrer\r\nPermissions-Policy: camera=(), microphone=(), geolocation=(), payment=()\r\n"
                                b"Content-Security-Policy: default-src 'none'; frame-ancestors 'none'\r\n\r\n")
            except OSError:
                pass
            finally:
                self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except Exception:
            self.workers.release()
            raise

    def process_request_thread(self, request: object, client_address: tuple) -> None:
        """Libera o slot inclusive quando a conexão falha."""
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.workers.release()


class Handler(BaseHTTPRequestHandler):
    """Lida com requisições individuais da demonstração."""

    def log_message(self, fmt: str, *args: object) -> None:
        # Não grava dados financeiros, tokens ou conteúdo de requisições.
        pass

    def parse_request(self) -> bool:
        """Verifica Host e limite antes do roteamento, sem confiar em proxies do cliente."""
        if not super().parse_request():
            return False
        try:
            path = urlsplit(self.path).path
        except ValueError:
            self.send_json(400, {"error": "Caminho inválido."})
            return False
        if self.command == "GET" and path == "/healthz":
            return True
        hosts = self.headers.get_all("Host", [])
        port = self.server.server_port
        expected = (urlsplit(self.server.public_origin).netloc,) if self.server.public_origin else (
            f"127.0.0.1:{port}", f"localhost:{port}")
        if len(hosts) != 1 or hosts[0] not in expected:
            self.send_json(403, {"error": "Host não permitido para esta demonstração."})
            return False
        if not self.server.check_rate(self.client_address[0]):
            self.send_json(429, {"error": "Muitas requisições. Aguarde um minuto e tente novamente."})
            return False
        return True

    def send_error(self, code: int, message: str | None = None, explain: str | None = None) -> None:
        """Mantém erros de protocolo sem conteúdo refletido da requisição."""
        self.close_connection = True
        self.send_json(code, {"error": "Requisição HTTP não permitida ou inválida."})

    def get_session(self) -> tuple[DemoSession, str | None]:
        """Consulta sob lock; constrói fora dele e reinsere com limite atômico."""
        cookies = SimpleCookie()
        try:
            cookies.load(self.headers.get("Cookie", ""))
        except Exception:
            cookies = SimpleCookie()
        item = cookies.get("elo_demo")
        key = item.value if item else None

        with self.server.sessions_lock:
            now = self.server.clock()
            self.server.expire_sessions(now)
            session = self.server.sessions.get(key)
            if session is not None:
                session.last_seen = now
                return session, None
            if len(self.server.sessions) >= 100:
                raise RuntimeError("Limite de sessões da demonstração atingido.")
        new_session = DemoSession(self.server.planner)
        new_key = secrets.token_urlsafe(24)
        with self.server.sessions_lock:
            now = self.server.clock()
            self.server.expire_sessions(now)
            if len(self.server.sessions) >= 100:
                raise RuntimeError("Limite de sessões da demonstração atingido.")
            new_session.last_seen = now
            self.server.sessions[new_key] = new_session
        return new_session, new_key

    def send_bytes(self, status: int, content: bytes, content_type: str,
                   new_cookie: "str | None" = None) -> None:
        """Envia uma resposta com cabeçalhos de segurança padrão."""
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Vary", "Origin")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()")
        if self.server.public_origin:
            self.send_header("Strict-Transport-Security", "max-age=31536000")
        if status == 429:
            self.send_header("Retry-After", str(ceil(self.server.rate_window)))
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
            "frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
        )
        if new_cookie:
            # A origem configurada determina Secure; cabeçalhos do visitante não alteram a política.
            secure_flag = "; Secure" if self.server.public_origin else ""
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
        if path == "/healthz":
            self.send_json(200, {"status": "ok", "synthetic": True})
            return
        if path == "/api/state":
            try:
                session, new_cookie = self.get_session()
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
            origin = self.headers.get("Origin")
            expected_origin = self.server.public_origin or "http://" + self.headers.get("Host", "")
            origins = self.headers.get_all("Origin", [])
            if len(origins) > 1 or (origin and origin != expected_origin) or (self.server.public_origin and not origin):
                raise PermissionError("Origem não permitida.")
            session, new_cookie = self.get_session()
            token = self.headers.get("X-Demo-CSRF", "")
            if not secrets.compare_digest(token, session.csrf):
                raise PermissionError("Sessão inválida. Atualize a página.")
            if self.headers.get_content_type() != "application/json":
                raise ValueError("Envie conteúdo application/json.")
            if self.headers.get("Transfer-Encoding"):
                raise ValueError("Transfer-Encoding não é aceito.")
            lengths = self.headers.get_all("Content-Length", [])
            if len(lengths) != 1 or not lengths[0].isascii() or not lengths[0].isdecimal():
                raise ValueError("Cabeçalho Content-Length inválido.")
            raw_len = lengths[0]
            try:
                size = int(raw_len)
            except (ValueError, TypeError):
                raise ValueError("Cabeçalho Content-Length inválido.")
            if not 0 < size <= 8192:
                raise ValueError("Tamanho inválido.")
            body = self.rfile.read(size)
            if len(body) != size:
                raise ValueError("Corpo da requisição incompleto.")
            payload = json.loads(body)
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
                elif path == "/api/decline":
                    rid, aid = payload.get("report_id"), payload.get("action_id")
                    if not isinstance(rid, str) or not isinstance(aid, str):
                        raise ValueError("Identificador inválido.")
                    session.decline(rid, aid)
                elif path == "/api/monitor":
                    session.monitor()
                else:
                    self.send_json(404, {"error": "Ação não encontrada."})
                    return
                self.send_json(200, session.public_state(), new_cookie=new_cookie)
        except PermissionError as exc:
            self.send_json(403, {"error": str(exc)})
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_json(400, {"error": "Envie um objeto JSON válido em UTF-8."})
        except ValueError as exc:
            self.send_json(400, {"error": str(exc)})
        except (KeyError, TypeError):
            self.send_json(400, {"error": "Requisição inválida. Confira os campos enviados."})
        except TimeoutError:
            self.send_json(408, {"error": "Tempo de leitura esgotado. Tente novamente."})
        except RuntimeError:
            self.send_json(503, {"error": "A demonstração está ocupada."})

    def do_OPTIONS(self) -> None:
        """A API é da própria origem; não há autorização CORS para terceiros."""
        self.send_json(403, {"error": "A API aceita apenas requisições da própria origem."})


def main() -> None:
    """Ponto de entrada para `python -m elo.server`."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")))
    args = parser.parse_args()
    planner = None
    if os.environ.get("ELO_PLANNER") == "watsonx":
        if args.host not in ("127.0.0.1", "localhost"):
            parser.error("O planejador IBM só pode ser ativado na demonstração local.")
        from .watsonx import WatsonxPlanner
        planner = WatsonxPlanner()
    print(f"Elo Financeiro: http://{args.host}:{args.port} | dados sintéticos")
    DemoServer((args.host, args.port), planner, public_origin=os.environ.get("ELO_PUBLIC_ORIGIN") or None).serve_forever()


if __name__ == "__main__":
    main()
