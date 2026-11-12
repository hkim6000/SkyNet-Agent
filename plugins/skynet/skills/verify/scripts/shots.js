const { chromium } = require(require.resolve('playwright', { paths: [process.cwd(), __dirname].concat((process.env.NODE_PATH || '').split(require('path').delimiter).filter(Boolean)) }));
const fs = require('fs');

const base = (process.argv[2] || 'http://localhost:5180/').replace(/\/?$/, '/');
const pageArg = process.argv[3] || 'Home';
const pages = pageArg.split(pageArg.includes('|') ? '|' : ',').map(s => s.trim()).filter(Boolean);
const widths = (process.argv[4] || '1440,820,390').split(',').map(Number);
const out = process.argv[5] || 'shots';
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
  let problems = 0;
  for (const w of widths) {
    const ctx = await browser.newContext(Object.assign({ viewport: { width: w, height: 900 } }, process.env.STATE ? { storageState: process.env.STATE } : {}));
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
        const broken = imgs.filter(i => i.getAttribute('src') && i.complete && i.naturalWidth === 0).map(i => i.getAttribute('src'));
        const overflow = document.documentElement.scrollWidth - window.innerWidth;
        const wide = overflow > 0 ? [...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > window.innerWidth + 1 && getComputedStyle(e).position !== 'fixed').slice(0, 4).map(e => e.tagName.toLowerCase() + '.' + String(e.className).split(' ')[0]) : [];
        const holes = (document.body.innerHTML.match(/\{plhd_[a-z0-9_]*\}/g) || []).slice(0, 4);
        const seen = {};
        document.querySelectorAll('[id]').forEach(e => { seen[e.id] = (seen[e.id] || 0) + 1; });
        const dups = Object.keys(seen).filter(k => seen[k] > 1).slice(0, 4);
        const name = e => e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/)[0] : '');
        const shown = e => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e); return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none'; };
        const scrolls = e => { for (let p = e.parentElement; p && p !== document.body; p = p.parentElement) { const o = getComputedStyle(p).overflowX; if (o === 'auto' || o === 'scroll') return true; } return false; };
        const skip = 'input,select,textarea,svg,canvas,img,video,iframe,option,script,style';
        const clipped = [];
        for (const e of document.querySelectorAll('body *')) {
          if (clipped.length >= 4) break;
          if (e.matches(skip) || e.closest('svg') || !shown(e) || scrolls(e)) continue;
          const cs = getComputedStyle(e);
          if (cs.position === 'fixed' || cs.position === 'absolute') continue;
          if ((cs.overflowX === 'hidden' || cs.overflowX === 'clip') && cs.textOverflow !== 'ellipsis' && e.scrollWidth > e.clientWidth + 2 && e.textContent.trim()) {
            const kids = [...e.querySelectorAll('*')];
            const moving = [e].concat(kids).some(k => getComputedStyle(k).animationName !== 'none');
            const inner = !moving && kids.some(k => k.getBoundingClientRect().right > e.getBoundingClientRect().right + 2 && k.textContent.trim() && !k.matches(skip) && getComputedStyle(k).position !== 'absolute');
            if (inner) { clipped.push(name(e) + ' cuts text'); continue; }
          }
          const p = e.parentElement;
          const own = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
          if (!p || p === document.body || !own) continue;
          const pr = p.getBoundingClientRect(), r = e.getBoundingClientRect();
          const pad = parseFloat(getComputedStyle(p).paddingRight) || 0;
          const end = cs.display !== 'inline' && cs.overflowX === 'visible' && cs.textOverflow !== 'ellipsis' ? Math.max(r.right, r.left + e.scrollWidth) : r.right;
          if (end > pr.right - pad + 3 && end <= window.innerWidth + 1 && (end > r.right + 2 || (getComputedStyle(p).overflowX === 'visible' && p.scrollWidth > p.clientWidth + 2))) clipped.push(name(e) + ' runs out of ' + name(p));
        }
        const rgb = c => { const m = c.match(/[\d.]+/g); return m ? m.map(Number) : [0, 0, 0, 0]; };
        const lum = c => { const v = c.slice(0, 3).map(x => { x /= 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); }); return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]; };
        const unseen = [];
        for (const e of document.querySelectorAll('button, a, [role="button"]')) {
          if (unseen.length >= 4) break;
          if (!shown(e) || !e.textContent.trim()) continue;
          let bg = null;
          for (let p = e; p; p = p.parentElement) {
            const cs = getComputedStyle(p);
            if (cs.backgroundImage !== 'none') break;
            const c = rgb(cs.backgroundColor);
            if ((c.length < 4 || c[3] > 0.5) && cs.backgroundColor !== 'transparent') { bg = c; break; }
          }
          if (!bg) continue;
          const fg = rgb(getComputedStyle(e).color);
          const a1 = lum(fg), a2 = lum(bg);
          if ((Math.max(a1, a2) + 0.05) / (Math.min(a1, a2) + 0.05) < 1.6) unseen.push(name(e) + ' "' + e.textContent.trim().slice(0, 24) + '"');
        }
        return { images: imgs.length, broken, overflow, wide, holes, clipped, dups, unseen, height: document.body.scrollHeight };
      });
      const file = `${out}/${name.replace(/[^A-Za-z0-9_-]+/g, '_')}_${w}.png`;
      await page.screenshot({ path: file, fullPage: true });
      const bad = r.broken.length || r.overflow > 0 || r.holes.length || r.clipped.length || r.dups.length || r.unseen.length;
      if (bad) problems++;
      console.log(`${bad ? 'FAIL' : 'ok  '} ${w} ${name}  images ${r.images}  broken ${r.broken.length} ${r.broken.slice(0, 2).join(' ')}  overflow ${r.overflow} ${r.wide.join(' ')}  placeholders ${r.holes.join(' ')}  clipped ${r.clipped.length} ${r.clipped.slice(0, 2).join(', ')}  duplicate ids ${r.dups.join(' ')}  unreadable ${r.unseen.join(', ')}  height ${r.height}  -> ${file}`);
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
