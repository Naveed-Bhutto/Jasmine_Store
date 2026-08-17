#!/usr/bin/env python3
"""
server.py — Jasmine Store dynamic admin server
================================================
A ZERO-DEPENDENCY web server (Python standard library only — no pip installs)
that makes index.html dynamically updatable in two ways:

  METHOD 1 — Password-protected Admin Panel  →  http://<host>/admin
             Add / edit / delete products in a form. Every save instantly
             rewrites the PRODUCTS array inside index.html.

  METHOD 2 — Upload / edit products.json
             • Upload a products.json file from the /admin panel, or
             • Edit products.json on disk and call POST /api/reload
             Either way index.html is re-injected immediately.

Both methods share the same validation + injection engine
(tools/update_products.py), so index.html can never be corrupted.

Run:
    ADMIN_PASSWORD="your-secret" python3 server.py           # port 8000
    ADMIN_PASSWORD="your-secret" PORT=5000 python3 server.py

Security features:
    • Session cookies (HttpOnly, random 256-bit tokens, 8h expiry)
    • Constant-time password comparison (hmac.compare_digest)
    • Login rate-limiting: 5 failed attempts → 5 minute lockout per IP
    • Automatic .bak backup of index.html before every write
"""

import hmac
import importlib.util
import json
import os
import secrets
import sys
import time
import urllib.parse
from http import cookies as http_cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------
ROOT           = Path(__file__).parent
INDEX_FILE     = ROOT / "index.html"
PRODUCTS_FILE  = ROOT / "products.json"
PANEL_FILE     = ROOT / "templates" / "admin_panel.html"
LOGIN_FILE     = ROOT / "templates" / "admin_login.html"

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "jasmine123")   # ← CHANGE ME (env var)
PORT           = int(os.environ.get("PORT", 8000))
SESSION_TTL    = 8 * 3600          # 8 hours
MAX_ATTEMPTS   = 5                 # failed logins before lockout
LOCKOUT_SECS   = 300               # 5 minutes

SESSIONS: dict[str, float] = {}    # token -> expiry timestamp
FAILED:   dict[str, list]  = {}    # ip -> [timestamps of failures]

# --------------------------------------------------------------------------
# Reuse the validation + injection engine from tools/update_products.py
# --------------------------------------------------------------------------
_spec = importlib.util.spec_from_file_location("upd", ROOT / "tools" / "update_products.py")
upd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(upd)      # gives us: upd.validate, upd.to_js, upd.inject


def publish(products: list) -> tuple[bool, str]:
    """Validate → save products.json → inject into index.html (with backup).
    Returns (ok, message)."""
    if not isinstance(products, list):
        return False, "Products payload must be a JSON array."

    errors = upd.validate(products)
    if errors:
        return False, "Validation failed: " + " | ".join(errors)

    # Save master JSON
    PRODUCTS_FILE.write_text(json.dumps(products, indent=2, ensure_ascii=False), encoding="utf-8")

    # Backup then rewrite index.html
    html = INDEX_FILE.read_text(encoding="utf-8")
    (ROOT / "index.html.bak").write_text(html, encoding="utf-8")
    try:
        INDEX_FILE.write_text(upd.inject(html, upd.to_js(products)), encoding="utf-8")
    except SystemExit:
        return False, "PRODUCTS_START/END markers missing in index.html — restore from index.html.bak"

    return True, f"✅ Published {len(products)} products → index.html updated live."


def load_products() -> list:
    try:
        return json.loads(PRODUCTS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


# --------------------------------------------------------------------------
# HTTP handler
# --------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    server_version = "JasmineStore/1.0"

    # ---------------- helpers ----------------
    def _client_ip(self):
        return self.headers.get("X-Forwarded-For", self.client_address[0]).split(",")[0].strip()

    def _send(self, code=200, body=b"", ctype="text/html; charset=utf-8", extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200, extra=None):
        self._send(code, json.dumps(obj).encode(), "application/json; charset=utf-8", extra)

    def _redirect(self, path, extra=None):
        self.send_response(303)
        self.send_header("Location", path)
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _file(self, path: Path, ctype):
        if not path.exists():
            self._send(404, b"Not found", "text/plain")
            return
        self._send(200, path.read_bytes(), ctype)

    # ---------------- auth ----------------
    def _session_token(self):
        raw = self.headers.get("Cookie", "")
        jar = http_cookies.SimpleCookie(raw)
        return jar["session"].value if "session" in jar else None

    def _authed(self):
        tok = self._session_token()
        if tok and SESSIONS.get(tok, 0) > time.time():
            return True
        if tok in SESSIONS:                      # expired — clean up
            SESSIONS.pop(tok, None)
        return False

    def _locked_out(self, ip):
        now = time.time()
        FAILED[ip] = [t for t in FAILED.get(ip, []) if now - t < LOCKOUT_SECS]
        return len(FAILED[ip]) >= MAX_ATTEMPTS

    # ---------------- request body ----------------
    def _body(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        return self.rfile.read(length) if length else b""

    # ================= GET =================
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path

        if path in ("/", "/index.html"):
            return self._file(INDEX_FILE, "text/html; charset=utf-8")

        if path == "/products.json":
            return self._file(PRODUCTS_FILE, "application/json; charset=utf-8")

        if path == "/admin":
            page = PANEL_FILE if self._authed() else LOGIN_FILE
            return self._file(page, "text/html; charset=utf-8")

        if path == "/admin/logout":
            tok = self._session_token()
            SESSIONS.pop(tok, None)
            return self._redirect("/admin", {"Set-Cookie": "session=; Max-Age=0; Path=/; HttpOnly"})

        if path == "/api/products":
            if not self._authed():
                return self._json({"error": "unauthorized"}, 401)
            return self._json(load_products())

        # Legacy offline tool remains available
        if path == "/admin.html":
            return self._file(ROOT / "admin.html", "text/html; charset=utf-8")

        self._send(404, b"Not found", "text/plain")

    # ================= POST =================
    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        ip = self._client_ip()

        # ---- login ----
        if path == "/admin/login":
            if self._locked_out(ip):
                return self._send(429, "<h3>Too many attempts. Try again in 5 minutes.</h3>".encode())
            form = urllib.parse.parse_qs(self._body().decode())
            password = form.get("password", [""])[0]
            if hmac.compare_digest(password, ADMIN_PASSWORD):
                FAILED.pop(ip, None)
                tok = secrets.token_hex(32)
                SESSIONS[tok] = time.time() + SESSION_TTL
                cookie = f"session={tok}; Path=/; HttpOnly; Max-Age={SESSION_TTL}; SameSite=Lax"
                return self._redirect("/admin", {"Set-Cookie": cookie})
            FAILED.setdefault(ip, []).append(time.time())
            return self._redirect("/admin?error=1")

        # ---- everything below requires auth ----
        if not self._authed():
            return self._json({"error": "unauthorized"}, 401)

        # METHOD 1: add or update ONE product from the admin form
        if path == "/api/products":
            try:
                p = json.loads(self._body().decode())
            except json.JSONDecodeError:
                return self._json({"ok": False, "message": "Invalid JSON body."}, 400)
            products = load_products()
            if p.get("id") and any(x["id"] == p["id"] for x in products):
                products = [p if x["id"] == p["id"] else x for x in products]     # update
            else:
                p["id"] = max((x["id"] for x in products), default=0) + 1         # add
                products.append(p)
            ok, msg = publish(products)
            return self._json({"ok": ok, "message": msg, "id": p.get("id")}, 200 if ok else 400)

        # METHOD 1: delete a product
        if path == "/api/products/delete":
            try:
                pid = json.loads(self._body().decode()).get("id")
            except json.JSONDecodeError:
                return self._json({"ok": False, "message": "Invalid JSON body."}, 400)
            products = [x for x in load_products() if x["id"] != pid]
            ok, msg = publish(products)
            return self._json({"ok": ok, "message": msg}, 200 if ok else 400)

        # METHOD 2a: replace the ENTIRE catalog (products.json upload from panel)
        if path == "/api/replace":
            try:
                products = json.loads(self._body().decode())
            except json.JSONDecodeError:
                return self._json({"ok": False, "message": "That file is not valid JSON."}, 400)
            ok, msg = publish(products)
            return self._json({"ok": ok, "message": msg}, 200 if ok else 400)

        # METHOD 2b: products.json was edited on disk → re-inject it
        if path == "/api/reload":
            ok, msg = publish(load_products())
            return self._json({"ok": ok, "message": msg}, 200 if ok else 400)

        self._json({"error": "not found"}, 404)

    def log_message(self, fmt, *args):   # tidy console output
        sys.stderr.write(f"[{self._client_ip()}] {fmt % args}\n")


# --------------------------------------------------------------------------
if __name__ == "__main__":
    if ADMIN_PASSWORD == "jasmine123":
        print("⚠️  Using DEFAULT password 'jasmine123'. Set a real one:")
        print("    ADMIN_PASSWORD='my-secret' python3 server.py\n")
    print(f"🌸 Jasmine Store server → http://0.0.0.0:{PORT}")
    print(f"   Site:  /        Admin: /admin")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
