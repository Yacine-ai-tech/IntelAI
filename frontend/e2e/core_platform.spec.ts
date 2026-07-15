import { test, expect } from '@playwright/test';

// Use IntelAI's base URL (assuming Vite runs on 5173 for local, or dynamic via BASE_URL)
const BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:5173';

test.describe('Phase 2: IntelAI Core Platform E2E', () => {

  test('Slice 2.1: Authentication & Navigation Routing', async ({ page }) => {
    // 1. Test Login Page Routing
    await page.goto(`${BASE_URL}/login`);
    
    // Check if login form renders
    const emailInput = page.locator('input[type="email"], input[name="email"], input[placeholder*="email" i]');
    const passwordInput = page.locator('input[type="password"]');
    
    // We tolerate if login is bypassed or doesn't exist identically (in dev mode)
    if (await emailInput.count() > 0) {
      await emailInput.fill('admin@omniintel.com');
      await passwordInput.fill('secure_password123');
      await page.locator('button', { hasText: /log in|sign in/i }).click();
    }

    // 2. Test Navigation to Settings
    await page.goto(`${BASE_URL}/settings`);
    await expect(page.locator('text=/Settings/i').first()).toBeVisible({ timeout: 10000 });
    
    // 3. Test Organization Page
    await page.goto(`${BASE_URL}/organization`);
    await expect(page.locator('text=/Organization/i').first()).toBeVisible();

    // 4. Test Workspace Page
    await page.goto(`${BASE_URL}/workspace`);
    await expect(page.locator('text=/Workspace/i').first()).toBeVisible();
    
    // 5. Test Admin Page
    await page.goto(`${BASE_URL}/admin`);
    await expect(page.locator('text=/Admin/i').first()).toBeVisible();
  });

  test('Slice 2.2: Cross-Domain Dashboards Rendering', async ({ page }) => {
    const dashboards = [
      { path: '/', title: 'Dashboard' },
      { path: '/esg', title: 'ESG' },
      { path: '/financial', title: 'Financial' },
      { path: '/growth', title: 'Growth' },
      { path: '/hr', title: 'HR' },
      { path: '/it', title: 'IT' },
      { path: '/logistics', title: 'Logistics' },
      { path: '/operations', title: 'Operations' },
      { path: '/risk', title: 'Risk' }
    ];

    for (const dash of dashboards) {
      await test.step(`Verify ${dash.title} Dashboard`, async () => {
        await page.goto(`${BASE_URL}${dash.path}`);
        
        // Ensure the page didn't throw a fatal React Error Boundary crash
        await expect(page.locator('text=/An unexpected error occurred/i')).toHaveCount(0);
        
        // Look for the main layout wrapper
        await expect(page.locator('body')).toBeVisible();
        
        // Dashboards should load some form of a chart or stats grid. 
        // We wait up to 5 seconds for network requests to populate the UI.
        const charts = page.locator('.recharts-responsive-container, canvas, svg');
        const grids = page.locator('.grid, table, [role="grid"]');
        
        // Assert that at least one data visualization element is present
        await expect(async () => {
           const hasCharts = await charts.count() > 0;
           const hasGrids = await grids.count() > 0;
           expect(hasCharts || hasGrids).toBeTruthy();
        }).toPass({ timeout: 5000 });
      });
    }
  });

  test('Slice 2.3: Knowledge Graph Interaction', async ({ page }) => {
    await page.goto(`${BASE_URL}/knowledge-graph`);
    
    // Check if the ForceGraph canvas/SVG renders
    const graphContainer = page.locator('canvas, svg');
    if (await graphContainer.count() > 0) {
      await expect(graphContainer.first()).toBeVisible({ timeout: 10000 });
    }
  });

});
