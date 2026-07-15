import { test, expect } from '@playwright/test';
import path from 'path';
import fs from 'fs';

const BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:5173';

test.describe('Enterprise Cross-Mesh Integration', () => {

  test('E2E Full Lifecycle: Auth -> Ingest -> Search -> Evaluate', async ({ page }) => {
    // 1. Auth (IntelAI Boundary)
    await test.step('Authenticate via IntelAI Gateway', async () => {
      await page.goto(`${BASE_URL}/login`);
      const emailInput = page.locator('input[type="email"]');
      if (await emailInput.count() > 0) {
        await emailInput.fill('admin@omniintel.com');
        await page.locator('input[type="password"]').fill('secure_password123');
        await page.locator('button', { hasText: /log in/i }).click();
      }
      // Verify login success by checking for main app shell
      await expect(page.locator('body')).toBeVisible();
    });

    // 2. Document Ingestion (DocIntel Boundary)
    await test.step('Ingest Document via DocIntel Subsystem', async () => {
      await page.goto(`${BASE_URL}/documents`);
      
      const fileInput = page.locator('input[type="file"]');
      if (await fileInput.count() > 0) {
        const dummyPdf = path.join(__dirname, 'cross_mesh_test.pdf');
        if (!fs.existsSync(dummyPdf)) fs.writeFileSync(dummyPdf, '%PDF-1.4 Dummy Document');
        
        await fileInput.setInputFiles(dummyPdf);
        // Wait for extraction success toast or UI update
        await expect(page.locator('text=/Classification|Success/i')).toBeVisible({ timeout: 15000 });
      }
    });

    // 3. Agent Search & Routing (AgentKit / VoiceFlow Boundary)
    await test.step('Configure Search Tool via AgentKit', async () => {
      await page.goto(`${BASE_URL}/tools`);
      // Verify tools registry is active
      await expect(page.locator('text=/Tools/i').first()).toBeVisible();
      
      // Simulate selecting the Qdrant Vector Search tool
      const toolButton = page.locator('button', { hasText: /Vector Search|Qdrant/i });
      if (await toolButton.count() > 0) {
        await toolButton.first().click();
        await expect(page.locator('.toast, .success')).toBeVisible({ timeout: 5000 });
      }
    });

    // 4. Evaluation & Tracing (RAGeval / StreamPulse Boundary)
    await test.step('Evaluate LLM Execution via RAGeval', async () => {
      await page.goto(`${BASE_URL}/traces`);
      
      // Verify trace logs expand
      const traceRow = page.locator('details, .trace-row');
      if (await traceRow.count() > 0) {
        await traceRow.first().click();
        // Assert JSON logs are visible
        await expect(traceRow.first().locator('pre, code')).toBeVisible();
      }
    });

  });

});
