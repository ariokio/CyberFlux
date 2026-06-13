#!/usr/bin/env python3
"""
CyberFlux RSS Proxy — v2.0
Proxy local CORS pour CyberFlux-v2.html
Utilise requests pour contourner les anti-bots
Lance avec : python3 cyberflux_proxy.py
Écoute sur  : http://localhost:8765
"""

import http.server
import urllib.parse
import json
import sys
import os
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

PORT = 8765
TIMEOUT = 15

# Couleurs terminal
R = "\033[91m"; G = "\033[92m"; Y = "\033[93m"
C = "\033[96m"; W = "\033[97m"; X = "\033[0m"

def log(color, tag, msg):
    ts = time.strftime("%H:%M:%S")
    print(f"{color}[{ts}] [{tag}]{X} {msg}")

# Session requests réutilisable avec retry automatique
def make_session():
    s = requests.Session()
    retry = Retry(total=2, backoff_factor=0.3,
                  status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s

SESSION = make_session()

HEADERS_BASE = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) "
        "Gecko/20100101 Firefox/125.0"
    ),
    "Accept": (
        "application/rss+xml, application/atom+xml, "
        "application/xml, text/xml, */*;q=0.8"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-GPC": "1",
}

def build_headers(url):
    """Ajoute un Referer basé sur le domaine cible."""
    h = dict(HEADERS_BASE)
    try:
        p = urllib.parse.urlparse(url)
        h["Referer"] = f"{p.scheme}://{p.netloc}/"
        h["Host"] = p.netloc
    except Exception:
        pass
    return h


class RSSProxyHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass  # Silence le logger HTTP par défaut

    def send_cors(self, status=200, ctype="application/xml; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_cors(status, "application/json; charset=utf-8")
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_cors()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        # /ping
        if parsed.path == "/ping":
            self.send_json({"status": "ok", "port": PORT})
            return

        # /fetch?url=...
        if parsed.path == "/fetch":
            params = urllib.parse.parse_qs(parsed.query)
            target = params.get("url", [None])[0]
            if not target:
                self.send_json({"error": "Paramètre url manquant"}, 400)
                return
            if not target.startswith(("http://", "https://")):
                self.send_json({"error": "URL invalide"}, 400)
                return
            self._proxy_feed(target)
            return

        # / ou /CyberFlux-v2.html → sert le HTML
        if parsed.path in ("/", "/index.html", "/CyberFlux-v2.html"):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            html_path = os.path.join(script_dir, "CyberFlux-v2.html")
            if os.path.exists(html_path):
                with open(html_path, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", len(data))
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_cors(404, "text/plain")
                self.wfile.write(b"CyberFlux-v2.html introuvable dans le meme dossier")
            return

        self.send_cors(404, "text/plain")
        self.wfile.write(b"Endpoint inconnu")

    def _proxy_feed(self, url):
        short = url[:65] + "..." if len(url) > 65 else url
        try:
            r = SESSION.get(
                url,
                headers=build_headers(url),
                timeout=TIMEOUT,
                verify=False,          # SSL permissif (certs auto-signés)
                allow_redirects=True
            )

            # Certains feeds retournent 200 mais avec du HTML (anti-bot)
            ct = r.headers.get("Content-Type", "")
            if r.status_code == 200 and "text/html" in ct and "<rss" not in r.text[:500] and "<feed" not in r.text[:500]:
                log(Y, "BLK", f"Réponse HTML (anti-bot) — {short}")
                self.send_json({"error": "anti-bot: réponse HTML", "url": url}, 403)
                return

            if r.status_code >= 400:
                log(R, "ERR", f"HTTP {r.status_code} — {short}")
                self.send_json({"error": f"HTTP {r.status_code}", "url": url}, r.status_code)
                return

            # Détection charset : priorité à la déclaration XML <?xml encoding="...">
            raw = r.content
            detected = None
            try:
                head = raw[:200].decode("ascii", errors="ignore")
                if 'encoding="' in head:
                    detected = head.split('encoding="')[1].split('"')[0].strip()
                elif "encoding='" in head:
                    detected = head.split("encoding='")[1].split("'")[0].strip()
            except Exception:
                pass

            charset = detected or r.encoding or "utf-8"

            # Décode dans le charset source puis réencode en UTF-8
            try:
                text = raw.decode(charset, errors="replace")
            except (LookupError, UnicodeDecodeError):
                text = raw.decode("utf-8", errors="replace")

            # Remplace la déclaration d'encodage dans le XML
            if detected and detected.lower() not in ("utf-8", "utf8"):
                text = text.replace(f'encoding="{detected}"', 'encoding="UTF-8"')
                text = text.replace(f"encoding='{detected}'", "encoding='UTF-8'")

            encoded = text.encode("utf-8")
            self.send_cors(200, "application/xml; charset=utf-8")
            self.wfile.write(encoded)
            log(G, "OK ", f"HTTP {r.status_code} — {short}")

        except requests.exceptions.Timeout:
            log(Y, "TIM", f"Timeout ({TIMEOUT}s) — {short}")
            self.send_json({"error": "timeout", "url": url}, 504)

        except requests.exceptions.SSLError as e:
            log(Y, "SSL", f"{e} — {short}")
            self.send_json({"error": f"SSL: {e}", "url": url}, 502)

        except requests.exceptions.ConnectionError as e:
            log(R, "CON", f"{e} — {short}")
            self.send_json({"error": f"Connection: {e}", "url": url}, 502)

        except Exception as e:
            log(R, "EXC", f"{type(e).__name__}: {e} — {short}")
            self.send_json({"error": str(e), "url": url}, 500)


def print_banner():
    print(f"""
{C}╔══════════════════════════════════════════════════════╗
║        CYBERFLUX RSS PROXY  v2.0                     ║
║        Proxy local CORS — moteur requests            ║
╚══════════════════════════════════════════════════════╝{X}

{W}Interface  :{X}  {G}http://localhost:{PORT}/{X}
{W}Endpoint   :{X}  http://localhost:{PORT}/fetch?url=<rss_url>
{W}Ping       :{X}  http://localhost:{PORT}/ping

{Y}Placer CyberFlux-v2.html dans le même dossier
que ce script, puis ouvrir http://localhost:{PORT}/{X}

{C}Ctrl+C pour arrêter{X}
{"─" * 56}
""")

# Supprime les warnings SSL de urllib3
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    print_banner()

    if sys.version_info < (3, 7):
        print(f"{R}[ERR] Python 3.7+ requis{X}")
        sys.exit(1)

    try:
        import requests  # noqa
    except ImportError:
        print(f"{R}[ERR] Module 'requests' manquant{X}")
        print(f"{Y}Lance : pip install requests --break-system-packages{X}")
        sys.exit(1)

    server = http.server.ThreadingHTTPServer(("localhost", PORT), RSSProxyHandler)
    server.daemon_threads = True

    log(G, "SRV", f"Proxy démarré — http://localhost:{PORT}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n{Y}[SRV] Arrêt...{X}")
        server.shutdown()
        log(G, "SRV", "Proxy arrêté proprement")


if __name__ == "__main__":
    main()
