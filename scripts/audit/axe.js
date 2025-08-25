const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

async function run() {
  const url = process.env.AUDIT_URL || 'http://127.0.0.1:8080/';
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox','--disable-setuid-sandbox']
  });
  try {
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
    const axePath = require.resolve('axe-core/axe.min.js');
    const axeSrc = fs.readFileSync(axePath, 'utf8');
    await page.addScriptTag({ content: axeSrc });
    const results = await page.evaluate(async () => {
      return await (window.axe && window.axe.run(document, { resultTypes: ['violations'] }));
    });
    if (!results) {
      console.error('axe-core did not run');
      process.exit(1);
    }
    const { violations } = results;
    if (violations.length) {
      console.error(`axe violations: ${violations.length}`);
      for (const v of violations) {
        console.error(`- ${v.id}: ${v.help} (${v.impact})`);
      }
      process.exit(1);
    }
    console.log('OK: axe violations 0');
  } finally {
    await browser.close();
  }
}

run().catch(err => { console.error(err); process.exit(1); });

