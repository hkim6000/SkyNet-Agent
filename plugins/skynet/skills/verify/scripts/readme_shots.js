const { chromium } = require(require.resolve('playwright', { paths: [process.cwd(), __dirname].concat((process.env.NODE_PATH || '').split(require('path').delimiter).filter(Boolean)) }));
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const base = (process.argv[2] || 'http://localhost:5180/').replace(/\/?$/, '/');
const site = process.argv[3] || '.';
const page = process.argv[4] || 'Home';
const out = path.join(site, 'docs');
const launch = (() => {
  if (process.env.CHROMIUM_PATH) { return { executablePath: process.env.CHROMIUM_PATH }; }
  try { if (fs.existsSync(chromium.executablePath())) { return {}; } } catch (e) { }
  for (const c of ['/opt/pw-browsers/chromium', '/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/google-chrome']) {
    if (fs.existsSync(c)) { return { executablePath: c }; }
  }
  return {};
})();

(async () => {
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch(launch);
  const raw = [];
  for (const [w, h, mobile] of [[1440, 900, false], [820, 1180, false], [390, 844, true]]) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2, isMobile: mobile, hasTouch: mobile });
    const p = await ctx.newPage();
    await p.goto(base + page);
    await p.waitForLoadState('networkidle');
    await p.waitForTimeout(1200);
    await p.evaluate(() => { document.querySelectorAll('video').forEach(v => { try { v.pause(); } catch (e) { } }); });
    const file = path.join(out, `raw-${w}.png`);
    await p.screenshot({ path: file });
    raw.push([w, file]);
    await ctx.close();
  }
  await browser.close();
  const py = `
import sys
from PIL import Image, ImageDraw, ImageFilter
out, d, t, m = sys.argv[1:5]
desk = Image.open(d).convert('RGB')
desk.resize((1440, 900), Image.LANCZOS).save(out + '/screenshot-home.png')
H = 620
ims = [Image.open(f).convert('RGB') for f in (d, t, m)]
ims = [i.resize((round(i.width * H / i.height), H), Image.LANCZOS) for i in ims]
pad, gap = 36, 32
W = sum(i.width for i in ims) + gap * 2 + pad * 2
px = desk.getpixel((desk.width // 2, 12))
bg = tuple(min(255, int(c * 0.08 + 236 * 0.92)) for c in px)
sheet = Image.new('RGB', (W, H + pad * 2), bg)
x = pad
for i in ims:
    sh = Image.new('RGBA', (i.width + 24, i.height + 24), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((12, 14, i.width + 12, i.height + 14), 14, fill=(0, 0, 0, 60))
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    sheet.paste(sh, (x - 12, pad - 12), sh)
    mask = Image.new('L', i.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, i.width, i.height), 12, fill=255)
    sheet.paste(i, (x, pad), mask)
    x += i.width + gap
sheet.save(out + '/screenshot-responsive.png')
print('wrote', out + '/screenshot-home.png', 'and', out + '/screenshot-responsive.png', sheet.size)
`;
  execFileSync('python3', ['-c', py, out, raw[0][1], raw[1][1], raw[2][1]], { stdio: 'inherit' });
  for (const [, f] of raw) { fs.unlinkSync(f); }
})();
