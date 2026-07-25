const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  let errors = [];
  page.on('pageerror', err => {
    errors.push(err.message);
  });
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });
  await page.goto('https://intelai.ysiddo-ai-projects.app/', { waitUntil: 'networkidle' });
  console.log("Errors:");
  console.log(errors);
  await browser.close();
})();
