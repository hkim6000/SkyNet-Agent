const { chromium } = require(require.resolve('playwright', { paths: [process.cwd(), __dirname].concat((process.env.NODE_PATH || '').split(require('path').delimiter).filter(Boolean)) }));
const fs = require('fs');
const path = require('path');

const file = path.resolve(process.argv[2] || '');
const out = process.argv[3] || path.join(path.dirname(file), 'check');
const banned = (process.argv[4] || 'demo,lorem,TODO').split(',').filter(Boolean);
const LAUNCH = process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {};

if (!fs.existsSync(file)) {
  console.log('usage: node check.js <Manual.html> [shots-folder] [banned,words]');
  process.exit(2);
}

(async () => {
  fs.mkdirSync(out, { recursive: true });
  let problems = 0;
  const text = fs.readFileSync(file, 'utf8').replace(/data:image\/[a-z]+;base64,[A-Za-z0-9+/=]+/g, '');
  for (const w of banned) {
    const hits = (text.match(new RegExp('.{0,40}\\b' + w + '\\b.{0,40}', 'gi')) || []).slice(0, 3);
    if (hits.length) { problems++; console.log('FAIL word "' + w + '": ' + hits.join(' | ')); }
  }
  const browser = await chromium.launch(LAUNCH);
  for (const [w, h] of [[1440, 900], [820, 1100], [390, 844]]) {
    const p = await (await browser.newContext({ viewport: { width: w, height: h } })).newPage();
    const errs = [];
    p.on('pageerror', e => errs.push(e.message));
    p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    await p.goto('file://' + file);
    await p.waitForTimeout(500);
    const r = await p.evaluate(async () => {
      const res = { sections: 0, images: 0, broken: 0, diagrams: document.querySelectorAll('.hm-diagram svg').length, links: [], overflow: [], noId: [] };
      const ids = new Set([...document.querySelectorAll('[id]')].map(e => e.id));
      document.querySelectorAll('a[data-target]').forEach(a => {
        const t = a.getAttribute('data-target'), s = a.getAttribute('data-sub');
        if (!ids.has(t) || (s && !ids.has(s))) res.links.push(t + (s ? '#' + s : ''));
      });
      document.querySelectorAll('.hm-section h2:not([id])').forEach(h => res.noId.push(h.textContent.slice(0, 40)));
      const content = document.getElementById('hm-content');
      for (const s of document.querySelectorAll('.hm-section')) {
        res.sections++;
        document.querySelector('.hm-navtop[data-target="' + s.id + '"]').click();
        await new Promise(r => setTimeout(r, 120));
        for (const img of s.querySelectorAll('img')) {
          res.images++;
          img.loading = 'eager';
          if (!img.complete) await new Promise(r => { img.onload = r; img.onerror = r; setTimeout(r, 3000); });
          if (!img.naturalWidth) res.broken++;
        }
        const right = content.getBoundingClientRect().right;
        for (const e of s.querySelectorAll('*')) {
          const b = e.getBoundingClientRect();
          if (b.width && b.right > right + 1 && !e.closest('.hm-tw') && !e.closest('pre')) { res.overflow.push(s.id + ' ' + e.tagName.toLowerCase()); break; }
        }
      }
      return res;
    });
    const bad = r.links.length || r.broken || r.overflow.length || r.noId.length || errs.length;
    if (bad) problems++;
    console.log((bad ? 'FAIL ' : 'ok   ') + w + '  sections ' + r.sections + '  images ' + r.images + '  broken ' + r.broken + '  diagrams ' + r.diagrams + '  bad links ' + r.links.slice(0, 4).join(' ') + '  overflow ' + r.overflow.slice(0, 3).join(', ') + '  h2 without id ' + r.noId.length + '  errors ' + (errs.slice(0, 2).join(' | ') || 0));
    if (w === 1440) {
      const n = await p.locator('.hm-diagram').count();
      for (let i = 0; i < n; i++) {
        const d = p.locator('.hm-diagram').nth(i);
        const sid = await d.evaluate(e => e.closest('.hm-section').id);
        await p.click('.hm-navtop[data-target="' + sid + '"]');
        await p.waitForTimeout(150);
        await d.scrollIntoViewIfNeeded();
        await d.screenshot({ path: path.join(out, 'diagram' + (i + 1) + '.png') });
      }
      await p.fill('#hm-search', 'sign');
      await p.waitForTimeout(200);
      const hits = await p.textContent('#hm-hits');
      await p.fill('#hm-search', '');
      await p.dispatchEvent('#hm-search', 'input');
      const withImg = await p.evaluate(() => { const s = [...document.querySelectorAll('.hm-section')].find(x => x.querySelector('img')); return s ? s.id : ''; });
      let zoom = 'no image';
      if (withImg) {
        await p.click('.hm-navtop[data-target="' + withImg + '"]');
        await p.waitForTimeout(200);
        const first = p.locator('.hm-section.active img').first();
        await first.click();
        await p.waitForTimeout(200);
        zoom = await p.evaluate(() => document.getElementById('hm-zoom').classList.contains('open')) ? 'opens' : 'FAIL';
        await p.keyboard.press('Escape');
      }
      if (zoom === 'FAIL' || !hits) problems++;
      console.log('     search "sign": ' + (hits || 'FAIL no result') + '  zoom ' + zoom + '  diagram shots ' + n + ' -> ' + out);
    }
    if (w === 390) {
      await p.click('#hm-menu');
      await p.waitForTimeout(300);
      await p.screenshot({ path: path.join(out, 'phone_menu.png') });
    }
    await p.close();
  }
  await browser.close();
  console.log(problems ? 'PROBLEMS ' + problems : 'ALL CLEAR');
  process.exit(problems ? 1 : 0);
})();
