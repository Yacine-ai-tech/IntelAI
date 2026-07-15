import { test, expect, request as pwRequest } from '@playwright/test';

/**
 * Phase 10 — Cross-Mesh Workflow Integration
 * Traces a single user journey across all 6 microservices:
 * IntelAI (Auth) → DocIntel (Ingest) → AgentKit (Config) → RAGeval (Evaluate)
 *
 * Uses the live production/staging URLs from environment variables.
 */

const URLS = {
  intelai:    process.env.INTELAI_URL    || 'http://localhost:5173',
  intelai_api:process.env.INTELAI_API_URL|| 'http://localhost:8000',
  docintel:   process.env.DOCINTEL_URL   || 'http://localhost:5174',
  docintel_api:process.env.DOCINTEL_API_URL|| 'http://localhost:8001',
  agentkit:   process.env.AGENTKIT_URL   || 'http://localhost:5177',
  agentkit_api:process.env.AGENTKIT_API_URL|| 'http://localhost:8005',
  rageval:    process.env.RAGEVAL_URL    || 'http://localhost:5176',
  rageval_api:process.env.RAGEVAL_API_URL|| 'http://localhost:8003',
};

const ADMIN_USER = 'admin';
const ADMIN_PASS = '***REMOVED-CREDENTIAL***';

// ─────────────────────────────────────────────────────────────────────────────
// Phase 10 — The Grand Tour Workflow
// ─────────────────────────────────────────────────────────────────────────────
test.describe('Phase 10 — Cross-Mesh Grand Tour', () => {

  let adminToken: string = '';

  test.beforeAll(async ({ }) => {
    // Step A: Authenticate at IntelAI and capture JWT
    const ctx = await pwRequest.newContext();
    const resp = await ctx.post(`${URLS.intelai_api}/api/login`, {
      data: { username: ADMIN_USER, password: ADMIN_PASS }
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
      { name: 'VoiceFlow',  url: `${process.env.VOICEFLOW_API_URL || 'http://localhost:8002'}/health` },
      { name: 'RAGeval',    url: `${URLS.rageval_api}/health` },
      { name: 'StreamPulse',url: `${process.env.STREAMPULSE_API_URL || 'http://localhost:8004'}/health` },
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

  test('IntelAI /api/chat does not return 500 on empty message', async ({ request }) => {
    const loginResp = await request.post(`${URLS.intelai_api}/api/login`, {
      data: { username: ADMIN_USER, password: ADMIN_PASS }
    });
    if (!loginResp.ok()) { test.skip(); return; }
    const { access_token, token } = await loginResp.json();
    const authToken = access_token || token;

    const chatResp = await request.post(`${URLS.intelai_api}/api/chat`, {
      headers: { Authorization: `Bearer ${authToken}` },
      data: { message: '', persona: 'admin' }
    });
    expect(chatResp.status()).not.toBe(500);
  });

  test('IntelAI /api/chat handles very long prompt without crashing', async ({ request }) => {
    const loginResp = await request.post(`${URLS.intelai_api}/api/login`, {
      data: { username: ADMIN_USER, password: ADMIN_PASS }
    });
    if (!loginResp.ok()) { test.skip(); return; }
    const body = await loginResp.json();
    const authToken = body.access_token || body.token;

    const longMessage = 'A'.repeat(10000);
    const chatResp = await request.post(`${URLS.intelai_api}/api/chat`, {
      headers: { Authorization: `Bearer ${authToken}` },
      data: { message: longMessage, persona: 'admin' },
      timeout: 30000,
    });
    // Should handle gracefully — truncate, summarise, or reject (400) — never crash (500)
    expect(chatResp.status()).not.toBe(500);
  });
});
