import { chromium } from 'playwright';
(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto('http://localhost:8000/login');
  await page.fill('input[type="email"], input[name="username"]', 'admin');
  await page.fill('input[type="password"]', 'REDACTED_SECRET');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(2000);
  console.log("Current URL:", page.url());
  console.log("Body innerText:", (await page.locator('body').innerText()).slice(0, 100));
  await browser.close();
})();
