const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  page.on('pageerror', err => {
    console.log("PAGE ERROR:", err.message);
    console.log("STACK:", err.stack);
  });
  await page.goto('https://intelai.ysiddo-ai-projects.app/', { waitUntil: 'networkidle' });
  await browser.close();
})();
