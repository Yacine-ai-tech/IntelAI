const { chromium } = require('@playwright/test');

const apps = [
  'intelai',
  'docextract',
  'voiceflow',
  'rageval',
  'agentkit',
  'streampulse'
];

(async () => {
  const browser = await chromium.launch();
  
  for (const app of apps) {
    console.log(`\nTesting ${app}...`);
    const page = await browser.newPage();
    let hasError = false;
    page.on('console', msg => {
      if (msg.type() === 'error') {
        hasError = true;
        console.log(`[${app}] CONSOLE ERROR:`, msg.text());
      }
    });
    page.on('pageerror', error => {
      hasError = true;
      console.log(`[${app}] PAGE ERROR:`, error.message);
    });

    await page.goto(`https://gateway.ysiddo-ai-projects.app/${app}/`, { waitUntil: 'networkidle' }).catch(e => console.log(e));
    if (!hasError) console.log(`[${app}] OK - No errors detected.`);
    await page.close();
  }
  
  await browser.close();
})();
