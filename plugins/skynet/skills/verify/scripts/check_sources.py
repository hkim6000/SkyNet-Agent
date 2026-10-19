import os
import re
import sys

if len(sys.argv) < 2:
    print("usage: python3 check_sources.py <site-folder>")
    sys.exit(1)

ROOT = os.path.abspath(sys.argv[1])
problems = []
warnings = []


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def rel(path):
    return os.path.relpath(path, ROOT)


def files(folder, ext):
    base = os.path.join(ROOT, folder)
    out = []
    for d, _, names in os.walk(base):
        out += [os.path.join(d, n) for n in names if n.endswith(ext)]
    return sorted(out)


for path in files("codes", ".cs") + files("scripts", ".js") + files("styles", ".css"):
    text = read(path)
    for i, line in enumerate(text.split("\n"), 1):
        if re.match(r"^\s*//", line) or "/*" in line:
            problems.append(f"{rel(path)}:{i} comment found")
            break
    if "\r\n" in text:
        problems.append(f"{rel(path)} uses CRLF line endings")

for path in files("codes", ".cs"):
    text = read(path)
    if "Task.CompletedTask" in text:
        problems.append(f"{rel(path)} uses Task.CompletedTask")
    m = re.search(r"public class (\w+)\s*:\s*Web(Page|Base)", text)
    if not m:
        continue
    cls = m.group(1)
    methods = re.findall(r"public async Task<ApiResponse> (\w+)\(\)", text)
    if cls in methods:
        problems.append(f"{rel(path)} method {cls}() has the class name")
    for name in set(methods):
        if methods.count(name) > 1 or re.search(r"(private|internal|protected)[^\n(]*\s" + name + r"\(", text):
            problems.append(f"{rel(path)} method name {name} is used more than once")
    html_path = os.path.join(ROOT, "htmls", cls + ".html")
    if os.path.exists(html_path):
        html = read(html_path)
        for ph in sorted(set(re.findall(r"\{plhd_[a-z0-9_]+\}", html))):
            if ph not in text and ph[:-1] not in text:
                problems.append(f"htmls/{cls}.html placeholder {ph} is never replaced in {rel(path)}")
        site = re.search(r'class="([a-z0-9]+)-site', html)
        if site:
            prefix = site.group(1) + "-"
            if site.group(1) in ("ad", "ads"):
                problems.append(f"htmls/{cls}.html prefix '{prefix}' looks like an advert; ad blockers hide it. Use another prefix")
            for cl in re.findall(r'class="([^"{]+)"', html):
                for c in cl.split():
                    if not c.startswith(prefix):
                        problems.append(f"htmls/{cls}.html class '{c}' does not start with '{prefix}'")
    js_path = os.path.join(ROOT, "scripts", cls + ".js")
    if os.path.exists(js_path):
        keys = set(re.findall(r"key:\s*'([A-Za-z0-9_]+)'", read(js_path)))
        query = set(re.findall(r'QueryValue\("([A-Za-z0-9_]+)"', text))
        for k in sorted(keys & query):
            warnings.append(f"{cls}: request key '{k}' is also a query-string name; rename it if this request is sent from the {cls} page")

pages = {}
types = {}
for path in files("codes", ".cs"):
    text = read(path)
    for m in re.finditer(r"\b(?:class|record|struct|enum|interface)\s+([A-Z]\w*)", text):
        types.setdefault(m.group(1), []).append(rel(path))
    m = re.search(r"public class (\w+)\s*:\s*Web(Page|Base)", text)
    if m:
        pages[m.group(1)] = rel(path)
for name, where in sorted(pages.items()):
    others = [f for f in types.get(name, []) if f != where] + ([where] if types.get(name, []).count(where) > 1 else [])
    if others:
        problems.append(f"page {name} ({where}) shares its name with another type in {', '.join(sorted(set(others)))}; SkyNet finds pages by class name, so /{name} answers 'not found'. Rename the other type")

cfg = os.path.join(ROOT, "appConfig", "application.cfg")
if os.path.exists(cfg):
    for line in read(cfg).splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) == 2 and (parts[0].endswith("password") or parts[0].endswith("encryptkey")):
            if parts[1] not in ("your-password", "your-encrypt-key", ""):
                problems.append(f"appConfig/application.cfg {parts[0]} is not a placeholder")

for w in warnings:
    print("WARN " + w)
for p in problems:
    print("FAIL " + p)
print(f"PROBLEMS {len(problems)}" if problems else "ALL CLEAR")
sys.exit(1 if problems else 0)
