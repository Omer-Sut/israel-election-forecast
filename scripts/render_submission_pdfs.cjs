// Render the generated local HTML notes. No website or user browser profile is opened.
const path = require('node:path');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

async function main() {
  const root = path.resolve(__dirname, '..', 'reports', 'submission-package-2026-10-26');
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_EXECUTABLE || undefined,
    headless: true,
  });
  try {
    for (const lang of ['en', 'he']) {
      const page = await browser.newPage();
      await page.goto('file:///' + path.join(root, `method.${lang}.html`).replaceAll('\\', '/'));
      await page.pdf({path: path.join(root, `method.${lang}.pdf`), format: 'A4', printBackground: true, preferCSSPageSize: true});
      await page.close();
    }
  } finally {
    await browser.close();
  }
}

main().catch(err => { console.error(err); process.exitCode = 1; });
