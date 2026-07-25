const { chromium } = require('@playwright/test');

const apps = [
  { name: 'IntelAI', url: 'https://intelai.ysiddo-ai-projects.app' },
  { name: 'AgentKit', url: 'https://agentkit.ysiddo-ai-projects.app' },
  { name: 'DocIntel', url: 'https://docintel.ysiddo-ai-projects.app' },
  { name: 'StreamPulse', url: 'https://streampulse.ysiddo-ai-projects.app' },
  { name: 'RAGeval', url: 'https://rageval.ysiddo-ai-projects.app' },
  { name: 'VoiceFlow', url: 'https://voiceflow.ysiddo-ai-projects.app' }
];

async function verifyApps() {
  const browser = await chromium.launch({ headless: true });
  
  for (const app of apps) {
    console.log(`\n========================================`);
    console.log(`Testing ${app.name} at ${app.url}`);
    
    const context = await browser.newContext();
    const page = await context.newPage();
    let hasConsoleError = false;
    
    page.on('pageerror', error => {
      console.log(`[PAGE ERROR] ${app.name}: ${error.message}`);
      hasConsoleError = true;
    });
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        const text = msg.text();
        if (!text.includes('favicon.ico') && !text.includes('Failed to load resource')) {
          console.log(`[CONSOLE ERROR] ${app.name}: ${text}`);
          hasConsoleError = true;
        }
      }
    });

    try {
      const response = await page.goto(app.url, { waitUntil: 'networkidle', timeout: 15000 });
      console.log(`[STATUS] HTTP ${response ? response.status() : 'Unknown'}`);
      
      const rootExists = await page.locator('#root').count();
      if (rootExists === 0) {
        console.log(`[ERROR] No #root element found. Blank page?`);
      } else {
        const rootHtml = await page.locator('#root').innerHTML();
        if (rootHtml.trim().length < 50) {
          console.log(`[ERROR] #root element seems empty: ${rootHtml}`);
        } else {
          console.log(`[SUCCESS] #root has content.`);
        }
      }
      
      if (!hasConsoleError) {
        console.log(`[SUCCESS] No JS runtime errors detected for ${app.name}`);
      }
    } catch (e) {
      console.log(`[FATAL] Error navigating to ${app.name}: ${e.message}`);
    } finally {
      await context.close();
    }
  }
  
  await browser.close();
}

verifyApps().catch(console.error);
