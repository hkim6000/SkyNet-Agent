import os
import sys

from PIL import Image

if len(sys.argv) < 2:
    print('usage: python3 convert.py <manual-folder> [viewport-width=1440] [scale=2]')
    sys.exit(2)

root = os.path.abspath(sys.argv[1])
view = int(sys.argv[2]) if len(sys.argv) > 2 else 1440
scale = int(sys.argv[3]) if len(sys.argv) > 3 else 2
raw = os.path.join(root, 'raw')
out = os.path.join(root, 'jpg')
os.makedirs(out, exist_ok=True)
total = 0
count = 0
for f in sorted(os.listdir(raw)):
    if not f.lower().endswith('.png'):
        continue
    im = Image.open(os.path.join(raw, f)).convert('RGB')
    w = im.width
    if f.startswith('m_'):
        target = 430
    elif w >= view * scale:
        target = 1100
    else:
        target = min(1100, w // scale)
    if w > target:
        im = im.resize((target, round(im.height * target / w)), Image.LANCZOS)
    p = os.path.join(out, f[:-4] + '.jpg')
    im.save(p, quality=84, optimize=True, progressive=True)
    total += os.path.getsize(p)
    count += 1
print('images', count, 'KB', total // 1024)
