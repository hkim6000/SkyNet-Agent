const { chromium } = require(require.resolve('playwright', { paths: [process.cwd(), __dirname].concat((process.env.NODE_PATH || '').split(require('path').delimiter).filter(Boolean)) }));
const fs = require('fs');

const BASE = (process.argv[2] || 'http://localhost:5180/').replace(/\/?$/, '/');
const OUT = (process.argv[3] || 'manual/raw').replace(/\/?$/, '/');
const ONLY = process.argv[4] ? process.argv[4].split(',') : null;
const USER = process.env.MANUAL_USER || 'admin';
const PASS = process.env.MANUAL_PASS || '';
const LAUNCH = (() => {
  if (process.env.CHROMIUM_PATH) { return { executablePath: process.env.CHROMIUM_PATH }; }
  try { if (fs.existsSync(chromium.executablePath())) { return {}; } } catch (e) { }
  for (const c of ['/opt/pw-browsers/chromium', '/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/google-chrome']) {
    if (fs.existsSync(c)) { return { executablePath: c }; }
  }
  return {};
})();
const SCRUB_WORDS = [];

const SCRUB = words => {
  const res = words.map(w => new RegExp(w[0], w[1]));
  const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = walk.nextNode())) {
    let v = n.nodeValue;
    for (const r of res) v = v.replace(r, '');
    if (v !== n.nodeValue) n.nodeValue = v;
  }
};
const WORDS = SCRUB_WORDS.map(r => [r.source, r.flags]);

async function idle(p) {
  await p.waitForLoadState('networkidle');
  await p.waitForFunction(() => window.__busy === undefined || window.__busy === 0, null, { timeout: 30000 });
  await p.waitForTimeout(450);
}
async function go(p, url) { await p.goto(BASE + url); await idle(p); }
async function shot(p, name) { await p.evaluate(SCRUB, WORDS); await p.screenshot({ path: OUT + name + '.png' }); console.log('shot', name); }
async function part(p, sel, name) {
  const v = p.viewportSize();
  await p.setViewportSize({ width: v.width, height: 2600 });
  await p.waitForTimeout(400);
  await p.evaluate(SCRUB, WORDS);
  await p.locator(sel).first().screenshot({ path: OUT + name + '.png' });
  await p.setViewportSize(v);
  await p.waitForTimeout(250);
  console.log('part', name);
}
async function askOpen(p, px) { await p.locator('.' + px + '-ask.' + px + '-open .' + px + '-askbox').waitFor(); await p.waitForTimeout(250); }
async function askOk(p, px) { await askOpen(p, px); await p.locator('.' + px + '-ask.' + px + '-open .' + px + '-askacts button').last().click(); await idle(p); }
async function askNo(p, px) { await askOpen(p, px); await p.locator('.' + px + '-ask.' + px + '-open .' + px + '-askacts button').first().click(); await p.waitForTimeout(300); }
async function signIn(p, user, pass) {
  await go(p, 'AdminLogin');
  await p.fill('#lg-user', user);
  await p.fill('#lg-pass', pass);
  await p.click('button[type=submit]');
  await p.waitForURL(/\/Admin$/);
  await idle(p);
}
let failed = 0;
async function step(name, f) {
  if (ONLY && !ONLY.includes(name)) return;
  try { await f(); } catch (e) { failed++; console.log('FAIL', name, e.message.split('\n')[0]); }
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch(LAUNCH);
  const desk = await (await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 })).newPage();
  const errors = [];
  desk.on('pageerror', e => errors.push(e.message));

  await step('signin', async () => {
    await go(desk, 'AdminLogin');
    await shot(desk, 'login');
    await signIn(desk, USER, PASS);
    await shot(desk, 'dashboard');
    await desk.evaluate(() => window.scrollTo(0, 620));
    await desk.waitForTimeout(300);
    await shot(desk, 'dashboard2');
  });

  await step('area', async () => {
    await go(desk, 'AdminRooms');
    await shot(desk, 'rooms');
    await desk.locator('#rm-main button', { hasText: 'Edit' }).first().click();
    await idle(desk);
    await part(desk, '.rm-mbox', 'room_edit');
    await desk.keyboard.press('Escape');
  });

  await step('confirm', async () => {
    await go(desk, 'AdminBookings');
    await desk.locator('#bk-main button', { hasText: 'Open' }).first().click();
    await idle(desk);
    await desk.locator('.bk-mbox button', { hasText: 'Cancel' }).first().click();
    await askOpen(desk, 'bk');
    await shot(desk, 'ask_cancel');
    await askNo(desk, 'bk');
  });

  const site = await (await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 })).newPage();
  await step('public', async () => {
    await go(site, 'Home');
    await shot(site, 'home');
    await site.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await site.waitForTimeout(500);
    await shot(site, 'home_foot');
  });

  const phone = await (await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true })).newPage();
  await step('phone', async () => {
    await go(phone, 'Home');
    await shot(phone, 'm_home');
    await signIn(phone, USER, PASS);
    await shot(phone, 'm_dashboard');
  });

  await browser.close();
  console.log('errors', errors.join(' | ') || 'none');
  console.log(failed ? 'FAILED STEPS ' + failed : 'ALL STEPS OK');
  process.exit(failed ? 1 : 0);
})();
