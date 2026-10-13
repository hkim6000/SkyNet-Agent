const { chromium } = require(require.resolve('playwright', { paths: [process.cwd(), __dirname].concat((process.env.NODE_PATH || '').split(require('path').delimiter).filter(Boolean)) }));
const fs = require('fs');

const base = (process.argv[2] || 'http://localhost:5180/').replace(/\/?$/, '/');
const pages = (process.argv[3] || 'Home').split(',');
const widths = (process.argv[4] || '1440,820,390').split(',').map(Number);
const out = process.argv[5] || 'shots';
const launch = process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {};

(async () => {
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch(launch);
  let problems = 0;
  for (const w of widths) {
    const ctx = await browser.newContext({ viewport: { width: w, height: 900 } });
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('console', m => { if (m.type() === 'error' && !m.text().startsWith('Failed to load resource')) errors.push(m.text()); });
    page.on('response', r => { if (r.status() >= 400 && !r.url().endsWith('favicon.ico')) errors.push(r.status() + ' ' + r.url()); });
    for (const name of pages) {
      await page.goto(base + name, { waitUntil: 'networkidle' });
      await page.evaluate(async () => {
        for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 40)); }
        window.scrollTo(0, 0);
      });
      await page.waitForTimeout(400);
      const r = await page.evaluate(() => {
        const imgs = [...document.images];
        const broken = imgs.filter(i => i.complete && i.naturalWidth === 0).map(i => i.getAttribute('src'));
        const overflow = document.documentElement.scrollWidth - window.innerWidth;
        const wide = overflow > 0 ? [...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > window.innerWidth + 1 && getComputedStyle(e).position !== 'fixed').slice(0, 4).map(e => e.tagName.toLowerCase() + '.' + String(e.className).split(' ')[0]) : [];
        const holes = (document.body.innerHTML.match(/\{plhd_[a-z0-9_]*\}/g) || []).slice(0, 4);
        return { images: imgs.length, broken, overflow, wide, holes, height: document.body.scrollHeight };
      });
      const file = `${out}/${name.replace(/[^A-Za-z0-9_-]+/g, '_')}_${w}.png`;
      await page.screenshot({ path: file, fullPage: true });
      const bad = r.broken.length || r.overflow > 0 || r.holes.length;
      if (bad) problems++;
      console.log(`${bad ? 'FAIL' : 'ok  '} ${w} ${name}  images ${r.images}  broken ${r.broken.length} ${r.broken.slice(0, 2).join(' ')}  overflow ${r.overflow} ${r.wide.join(' ')}  placeholders ${r.holes.join(' ')}  height ${r.height}  -> ${file}`);
    }
    if (errors.length) {
      problems++;
      console.log(`FAIL ${w} errors: ${[...new Set(errors)].slice(0, 6).join(' | ')}`);
    }
    await ctx.close();
  }
  await browser.close();
  console.log(problems ? `PROBLEMS ${problems}` : 'ALL CLEAR');
  process.exit(problems ? 1 : 0);
})();
