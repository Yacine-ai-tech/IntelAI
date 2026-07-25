const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('https://intelai.ysiddo-ai-projects.app/', { waitUntil: 'networkidle' });
  await page.screenshot({ path: '/home/ai-sniper/.gemini/antigravity-ide/brain/f9b48d1d-aff9-4cc2-a243-e4259b60db9b/intelai_prod_screenshot.png' });
  await browser.close();
})();
