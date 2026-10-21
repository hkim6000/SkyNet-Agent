import json
import os
import re
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qsl, urlparse

if len(sys.argv) < 3:
    print("usage: python3 preview_server.py <site-folder> <runner-path> [port] [namespace]")
    sys.exit(1)

ROOT = os.path.abspath(sys.argv[1])
RUNNER = os.path.abspath(sys.argv[2])
PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8190
NS = sys.argv[4] if len(sys.argv) > 4 else os.path.basename(ROOT.rstrip("/"))
PAGES = {os.path.splitext(f)[0] for f in os.listdir(os.path.join(ROOT, "htmls")) if f.endswith(".html")}
ENV = dict(os.environ, SKYNET_ROOT=ROOT, SKYNET_NS=NS)
MOCK = ("<script>window.__log=[];window.__busy=0;window.__vars={};"
        "function $GetVarData(n){return window.__vars[n];}function $WaitOn(){}"
        "function $ApiRequest(r,d){window.__busy++;window.__log.push(r);"
        "fetch('/api',{method:'POST',body:JSON.stringify({r:r,d:JSON.parse(d)})}).then(function(x){return x.json()}).then(function(o){"
        "o.forEach(function(x){if(x.op==='set'){var e=document.getElementById(x.k);if(e){if(/^(INPUT|TEXTAREA|SELECT)$/.test(e.tagName))e.value=x.v;else e.innerHTML=x.v;}}"
        "else if(x.op==='var'){window.__vars[x.k]=JSON.parse(x.v);}else{eval(x.v);}});window.__busy--;})"
        ".catch(function(e){window.__busy--;window.__err=String(e);});}</script>")
TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp", ".svg": "image/svg+xml", ".gif": "image/gif",
         ".js": "application/javascript", ".css": "text/css", ".woff2": "font/woff2", ".json": "application/json", ".ico": "image/x-icon", ".mp4": "video/mp4", ".webm": "video/webm"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body, ctype):
        b = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urlparse(self.path)
        path = u.path.lstrip("/") or "Home"
        if path in PAGES:
            args = [RUNNER, "get", path]
            for k, v in parse_qsl(u.query, keep_blank_values=True):
                args += [k, v]
            r = subprocess.run(args, capture_output=True, text=True, env=ENV)
            if r.returncode != 0:
                return self.send(500, r.stderr, "text/plain")
            body = r.stdout.split("\n", 1)[1] if r.stdout.startswith("<!--TITLE") else r.stdout
            title = r.stdout.split("\n", 1)[0][10:-3] if r.stdout.startswith("<!--TITLE") else path
            html = ("<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width, initial-scale=1'>"
                    f"<title>{title}</title><link rel=stylesheet href='styles/{path}.css'>{MOCK}<script src='scripts/{path}.js'></script></head>"
                    f"<body>\n{body}\n</body></html>")
            return self.send(200, html, "text/html; charset=utf-8")
        full = os.path.join(ROOT, path)
        if os.path.isfile(full):
            data = open(full, "rb").read()
            if path.endswith(".css"):
                data = re.sub(rb"@import url\([^)]*fonts\.googleapis[^)]*\);?", b"", data)
            return self.send(200, data, TYPES.get(os.path.splitext(path)[1], "application/octet-stream"))
        self.send(404, "not found", "text/plain")

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        j = json.loads(self.rfile.read(n))
        page, method = j["r"].split("/")
        args = [RUNNER, method, page]
        for x in j["d"]:
            args += [x["key"], str(x["vlu"])]
        r = subprocess.run(args, capture_output=True, text=True, env=ENV)
        if r.returncode != 0:
            return self.send(500, json.dumps([{"op": "js", "k": "", "v": "console.error(" + json.dumps(r.stderr[:500]) + ")"}]), "application/json")
        self.send(200, r.stdout, "application/json")


print(f"preview of {ROOT} on http://127.0.0.1:{PORT}/  pages: {', '.join(sorted(PAGES))}")
ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
