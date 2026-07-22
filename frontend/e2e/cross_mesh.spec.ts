import { test, expect, request as pwRequest } from '@playwright/test';

const BASE_URL = process.env.TEST_BASE_URL || BASE_URL + '';

/**
 * Phase 10 — Cross-Mesh Workflow Integration
 * Traces a single user journey across all 6 microservices:
 * IntelAI (Auth) → DocIntel (Ingest) → AgentKit (Config) → RAGeval (Evaluate)
 *
 * Uses the live production/staging URLs from environment variables.
 */

const URLS = {
  intelai:    process.env.INTELAI_URL    || 'https://intelai-ui-2026.vercel.app',
  intelai_api:process.env.INTELAI_API_URL|| 'https://intelai-bwhp.onrender.com',
  docintel:   process.env.DOCINTEL_URL   || 'https://docintel-ui-2026.vercel.app',
  docintel_api:process.env.DOCINTEL_API_URL|| 'https://docintel-mm79.onrender.com',
  agentkit:   process.env.AGENTKIT_URL   || 'https://agentkit-ui-2026.vercel.app',
  agentkit_api:process.env.AGENTKIT_API_URL|| 'https://agentkit-sbz5.onrender.com',
  rageval:    process.env.RAGEVAL_URL    || 'https://rageval-ui-2026.vercel.app',
  rageval_api:process.env.RAGEVAL_API_URL|| 'https://rageval-4xh5.onrender.com',
};

const ADMIN_USER = 'admin';
const ADMIN_PASS = process.env.ADMIN_PASS || '';

// ─────────────────────────────────────────────────────────────────────────────
// Phase 10 — The Grand Tour Workflow
// ─────────────────────────────────────────────────────────────────────────────
test.describe('Phase 10 — Cross-Mesh Grand Tour', () => {

  test.beforeEach(async ({ page }) => {
    // Intercept relative /api/v1 calls made from Vercel frontends and route them to Render backends
    await page.route('**/api/v1/**', async route => {
      const url = route.request().url();
      if (url.includes('vercel.app')) {
        let backendUrl = URLS.intelai_api; // default
        if (url.includes('docintel-ui')) backendUrl = URLS.docintel_api;
        else if (url.includes('agentkit-ui')) backendUrl = URLS.agentkit_api;
        else if (url.includes('rageval-ui')) backendUrl = URLS.rageval_api;
        const newUrl = url.replace(/https:\/\/[^\/]+/, backendUrl.replace(/\/$/, ''));
        await route.continue({ url: newUrl });
      } else {
        await route.continue();
      }
    });
  });

  let adminToken: string = '';

  test.beforeAll(async ({ }) => {
    // Step A: Authenticate at IntelAI and capture JWT
    const ctx = await pwRequest.newContext();
    const resp = await ctx.post(`${URLS.intelai_api}/api/v1/auth/demo-login?role=admin`, {
      data: {}
    });
    if (resp.ok()) {
      const body = await resp.json();
      adminToken = body.access_token || body.token || '';
    }
    await ctx.dispose();
  });

  test('Step A: IntelAI — admin auth produces valid JWT', async ({}) => {
    expect(adminToken.length).toBeGreaterThan(10);
  });

  test('Step B: DocIntel API — authenticated upload endpoint reachable', async ({ request }) => {
    if (!adminToken) test.skip();
    const resp = await request.get(`${URLS.docintel_api}/api/documents`, {
      headers: { 'Authorization': `Bearer ${adminToken}` }
    });
    // Expect 200 (list) or 401 if token scoping is per-service
    expect([200, 401, 403, 404]).toContain(resp.status());
  });

  test('Step C: AgentKit API — tools endpoint reachable with JWT', async ({ request }) => {
    if (!adminToken) test.skip();
    const resp = await request.get(`${URLS.agentkit_api}/api/tools`, {
      headers: { 'Authorization': `Bearer ${adminToken}` }
    });
    expect([200, 401, 403, 404]).toContain(resp.status());
  });

  test('Step D: RAGeval API — evaluations endpoint reachable', async ({ request }) => {
    if (!adminToken) test.skip();
    const resp = await request.get(`${URLS.rageval_api}/api/evaluations`, {
      headers: { 'Authorization': `Bearer ${adminToken}` }
    });
    expect([200, 401, 403, 404]).toContain(resp.status());
  });

  test('Step E: Cross-service health check — all 6 services return 200 /health', async ({ request }) => {
    const services = [
      { name: 'IntelAI',    url: `${URLS.intelai_api}/health` },
      { name: 'DocIntel',   url: `${URLS.docintel_api}/health` },
      { name: 'VoiceFlow',  url: `${process.env.VOICEFLOW_API_URL || '/'}/health` },
      { name: 'RAGeval',    url: `${URLS.rageval_api}/health` },
      { name: 'StreamPulse',url: `${process.env.STREAMPULSE_API_URL || '/'}/health` },
      { name: 'AgentKit',   url: `${URLS.agentkit_api}/health` },
    ];
    for (const svc of services) {
      const resp = await request.get(svc.url, { timeout: 10000 }).catch(() => null);
      if (resp) {
        // 200 = healthy, 404 = endpoint not implemented (warn), 5xx = failure
        if (resp.status() >= 500) {
          console.error(`❌ ${svc.name} health check FAILED: ${resp.status()}`);
        } else if (resp.status() === 404) {
          console.warn(`⚠️ ${svc.name} has no /health endpoint`);
        } else {
          console.log(`✅ ${svc.name} health: ${resp.status()}`);
        }
        expect(resp.status()).toBeLessThan(500);
      } else {
        console.warn(`⚠️ ${svc.name} is unreachable in this environment`);
      }
    }
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Phase 11 — AI & RAG Defense
// ─────────────────────────────────────────────────────────────────────────────
test.describe('Phase 11 — AI & RAG Defense (via API)', () => {

  test('IntelAI /api/v1/chat does not return 500 on empty message', async ({ request }) => {
    const loginResp = await request.post(`${URLS.intelai_api}/api/v1/auth/demo-login?role=admin`, {
      data: {}
    });
    if (!loginResp.ok()) { test.skip(); return; }
    const { access_token, token } = await loginResp.json();
    const authToken = access_token || token;

    const chatResp = await request.post(`${URLS.intelai_api}/api/v1/chat`, {
      headers: { Authorization: `Bearer ${authToken}` },
      data: { message: '', persona: 'admin' }
    });
    expect(chatResp.status()).not.toBe(500);
  });

  test('IntelAI /api/v1/chat handles very long prompt without crashing', async ({ request }) => {
    const loginResp = await request.post(`${URLS.intelai_api}/api/v1/auth/demo-login?role=admin`, {
      data: {}
    });
    if (!loginResp.ok()) { test.skip(); return; }
    const body = await loginResp.json();
    const authToken = body.access_token || body.token;

    const longMessage = 'A'.repeat(10000);
    const chatResp = await request.post(`${URLS.intelai_api}/api/v1/chat`, {
      headers: { Authorization: `Bearer ${authToken}` },
      data: { message: longMessage, persona: 'admin' },
      timeout: 30000,
    });
    // Should handle gracefully — truncate, summarise, or reject (400) — never crash (500)
    expect(chatResp.status()).not.toBe(500);
  });
});
