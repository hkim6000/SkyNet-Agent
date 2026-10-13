const { chromium } = require(require.resolve('playwright', { paths: [process.cwd(), __dirname].concat((process.env.NODE_PATH || '').split(require('path').delimiter).filter(Boolean)) }));

const base = (process.argv[2] || 'http://localhost:5180/').replace(/\/?$/, '/');
const launch = process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {};
let fails = 0;

function ok(cond, label) {
  console.log((cond ? 'PASS ' : 'FAIL ') + label);
  if (!cond) fails++;
}

async function settle(page) {
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(250);
}

(async () => {
  const browser = await chromium.launch(launch);
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));

  await page.goto(base + 'Shop', { waitUntil: 'networkidle' });
  await page.click('#sh-chips .sh-chip:has-text("Botanical")');
  await settle(page);
  ok(await page.locator('#sh-grid .sh-card').count() === 2, 'category filter shows 2 prints');
  ok(page.url().includes('c=botanical'), 'filter updates the URL');

  await page.selectOption('#sh-sort', 'high');
  await settle(page);
  const first = await page.locator('#sh-grid .sh-card em').first().textContent();
  ok(first === '$42', 'sort by price, highest first: ' + first);

  await page.fill('#sh-q', 'fern');
  await page.waitForTimeout(400);
  await settle(page);
  ok(await page.locator('#sh-sugg .sh-sg').count() === 1, 'search suggestions');

  await page.goto(base + 'Contact', { waitUntil: 'networkidle' });
  await page.click('.ct-form button[type=submit]');
  await settle(page);
  ok((await page.locator('#ct-e-name').textContent()).length > 0, 'server validation shows errors');
  await page.fill('#ct-name', 'Alex Morgan');
  await page.fill('#ct-email', 'alex@example.com');
  await page.selectOption('#ct-topic', 'order');
  await page.fill('#ct-msg', 'A question about my order.');
  await page.click('.ct-form button[type=submit]');
  await settle(page);
  ok((await page.locator('#ct-sent').textContent()).includes('Thank you'), 'form accepted');

  ok(errors.length === 0, 'no JavaScript errors ' + errors.slice(0, 3).join(' | '));
  await browser.close();
  console.log(fails ? `FAILS ${fails}` : 'ALL PASS');
  process.exit(fails ? 1 : 0);
})();
