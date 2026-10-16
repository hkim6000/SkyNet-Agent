import base64
import os
import re
import sys

if len(sys.argv) < 3:
    print('usage: python3 build.py <manual-folder> "<Site name>" [output-name]')
    sys.exit(2)

root = os.path.abspath(sys.argv[1])
site = sys.argv[2]
name = sys.argv[3] if len(sys.argv) > 3 else re.sub(r'[^A-Za-z0-9]+', '_', site).strip('_') + '_User_Manual.html'
assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
src = os.path.join(root, 'src')
jpg = os.path.join(root, 'jpg')

css_file = os.path.join(src, 'manual.css') if os.path.exists(os.path.join(src, 'manual.css')) else os.path.join(assets, 'manual.css')
css = open(css_file, encoding='utf-8').read()
js = open(os.path.join(assets, 'manual.js'), encoding='utf-8').read()
parts = sorted(f for f in os.listdir(src) if re.match(r'body\d+\.html$', f))
if not parts:
    print('no src/body1.html ...')
    sys.exit(2)
body = ''.join(open(os.path.join(src, f), encoding='utf-8').read() for f in parts)

title = site.replace('&', '&amp;') + ' &mdash; User Manual'
page = ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8"/>\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1"/>\n'
        '<title>' + title + '</title>\n<style>\n' + css + '\n</style>\n</head>\n<body>\n'
        + body + '<script>\n' + js + '\n</script>\n</body>\n</html>\n')

used = set()
missing = set()


def embed(m):
    n = m.group(1)
    used.add(n)
    p = os.path.join(jpg, n + '.jpg')
    if not os.path.exists(p):
        missing.add(n)
        return ''
    return 'data:image/jpeg;base64,' + base64.b64encode(open(p, 'rb').read()).decode()


out = re.sub(r'\{\{img:([a-z0-9_]+)\}\}', embed, page)
open(os.path.join(root, name), 'w', encoding='utf-8').write(out)
have = {f[:-4] for f in os.listdir(jpg) if f.endswith('.jpg')} if os.path.isdir(jpg) else set()
print('output', os.path.join(root, name))
print('sections', len(re.findall(r'class="hm-section"', page)), 'images', len(used), 'KB', len(out.encode()) // 1024)
print('missing', sorted(missing) or 'none')
print('unused', sorted(have - used) or 'none')
sys.exit(1 if missing else 0)
