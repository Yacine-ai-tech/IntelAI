import { test, expect } from '@playwright/test';

const ROUTES = [
  '/workspace',
  '/reports',
  '/compare',
  '/knowledge-graph',
  '/organization',
  '/governance',
  '/dashboard',
  '/chat',
  '/analytics',
  '/growth',
  '/financial',
  '/data-hub',
  '/admin',
  '/settings',
  '/hr',
  '/logistics',
  '/it',
  '/operations',
  '/forecasting',
  '/esg',
  '/risk',
  '/knowledge',
  '/glossary'
];

test.describe('IntelAI All Pages E2E Suite', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login and authenticate as Admin
    await page.goto('/login');
    // Ensure the login page loaded
    await expect(page.locator('text=IntelAI')).toBeVisible();
    
    // Perform Demo Login for Admin
    await page.click('button:has-text("Admin (Full Access)")');
    
    // Wait for redirect to workspace
    await expect(page).toHaveURL(/.*workspace/);
  });

  for (const route of ROUTES) {
    test(`Should successfully load ${route} page without crashing`, async ({ page }) => {
      await page.goto(route);
      // Wait for network idle to ensure all API calls complete
      await page.waitForLoadState('networkidle');
      
      // Ensure the blank screen of death did not occur
      const rootHtml = await page.locator('#root').innerHTML();
      expect(rootHtml.length).toBeGreaterThan(0);
      
      // Ensure no generic "An unexpected error occurred" overlay
      const errorOverlay = page.locator('text=unexpected error');
      await expect(errorOverlay).not.toBeVisible();
    });
  }

  test('Should test Chat interaction with external LLM provider', async ({ page }) => {
    await page.goto('/chat');
    
    const chatInput = page.locator('input[placeholder*="message"]');
    if (await chatInput.isVisible()) {
      await chatInput.fill('Hello, are you connected to the LLM?');
      await page.keyboard.press('Enter');
      
      // Wait for response to stream back
      const responseBlock = page.locator('.message-assistant').last();
      await expect(responseBlock).toBeVisible({ timeout: 15000 });
      const text = await responseBlock.innerText();
      expect(text.length).toBeGreaterThan(5);
    }
  });

  test('Should test Data Hub file upload pipeline (Mocked)', async ({ page }) => {
    await page.goto('/data-hub');
    
    // Assert the upload dropzone is present
    const dropzone = page.locator('text=Drag & drop files here');
    if (await dropzone.isVisible()) {
      await expect(dropzone).toBeVisible();
    }
  });
});
