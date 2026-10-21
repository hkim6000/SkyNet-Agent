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


for name in os.listdir(ROOT):
    if name.endswith(".csproj"):
        proj = read(os.path.join(ROOT, name))
        for folder in ("data", "temp"):
            if re.search(r'<Content Include="' + folder + r'\\\*\*"\s*>', proj):
                problems.append(f"{name} includes {folder}\\** without Exclude=\"{folder}\\**\\*.json\" (NETSDK1022 once a .json file appears there)")
        m = re.search(r'Include="TheSkyLite\.SkyNet"\s+Version="([0-9.]+)"', proj)
        starter = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "website", "starter", "Starter.csproj")
        if m and os.path.exists(starter):
            sm = re.search(r'Include="TheSkyLite\.SkyNet"\s+Version="([0-9.]+)"', read(starter))
            if sm and [int(x) for x in m.group(1).split(".")] < [int(x) for x in sm.group(1).split(".")]:
                warnings.append(f"{name} references TheSkyLite.SkyNet {m.group(1)}; the starter uses {sm.group(1)}")

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
            chrome = {prefix + s for s in ("head", "foot", "nav", "site")}
            page_chrome = set()
            for cl in re.findall(r'class="([^"{]+)"', html):
                page_chrome |= chrome & set(cl.split())
            sources = [(f"codes/{cls}.cs", text)]
            if os.path.exists(js_path := os.path.join(ROOT, "scripts", cls + ".js")):
                sources.append((f"scripts/{cls}.js", read(js_path)))
            for name, src in sources:
                for cl in re.findall(r'''(?:class=|className\s*=\s*|classList\.add\()\\?["']([^"'{\\]+)''', src):
                    for c in page_chrome & set(cl.split()):
                        problems.append(f"{name} writes class '{c}' into page content, but htmls/{cls}.html uses it for the page header, footer or frame; its CSS will style the content as the frame. Name the content part '{prefix}c{c[len(prefix):]}'")
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

readme = os.path.join(ROOT, "README.md")
if os.path.exists(readme):
    shots = [s for s in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', read(readme)) if not s.startswith("http")]
    if not shots:
        problems.append("README.md has no screenshots; run readme_shots.js and add docs/screenshot-home.png and docs/screenshot-responsive.png")
    for shot in shots:
        if not shot.startswith("http") and not os.path.exists(os.path.join(ROOT, shot)):
            problems.append(f"README.md shows {shot} but the file is missing")

admin_css = [p for p in files("styles", ".css") if os.path.basename(p).startswith("Admin") and os.path.basename(p) != "AdminLogin.css"]
if len(admin_css) > 1:
    shapes = {}
    for path in admin_css:
        text = read(path)
        px = None
        m = re.search(r"\.([a-z0-9]{2,3})-site\b|\.([a-z0-9]{2,3})-logo\b", text)
        if m:
            px = m.group(1) or m.group(2)
        if not px:
            continue
        phone = re.search(r"@media\s*\(max-width:\s*(680|600|640|700)px\)\s*\{(.*?)\n\}", text, re.S)
        block = phone.group(2) if phone else ""
        hides_brand = re.search(r"\." + px + r"-logo\s+span\s*\{[^}]*display:\s*none", block) is not None
        who_minw = re.search(r"\." + px + r"-who\s*\{[^}]*min-width:\s*0", block) is not None
        shapes[rel(path)] = (hides_brand, who_minw)
    if shapes:
        common = max(set(shapes.values()), key=list(shapes.values()).count)
        for name, shape in shapes.items():
            if shape != common:
                problems.append(f"{name}: the phone header rules differ from the other admin pages (brand text hidden: {shape[0]}, name column min-width 0: {shape[1]}); copy the header block from a page that is right")

for w in warnings:
    print("WARN " + w)
for p in problems:
    print("FAIL " + p)
print(f"PROBLEMS {len(problems)}" if problems else "ALL CLEAR")
sys.exit(1 if problems else 0)
