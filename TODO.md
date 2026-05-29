# OmniIntelOS — Phase 1 TODO (Weeks 1–3, Days 8–27)

Checklist for Phase 1, derived from EXECUTION_PLAN.md §Phase 1 and STRATEGY.md §16.2.
Check items off in real time during the phase.

## Week 1 — Visual + Technical Fixes (Days 8–12)

### Day 8 — Recharts Conversion (Part 1)
- [ ] `cd frontend && npm install recharts` (already in package.json — verify lockfile)
- [ ] Replace SVG bars in `AnalyticsPage.jsx` with Recharts `LineChart`
- [ ] Verify in browser: charts render, data loads from API
- [ ] Replace `ForecastingPage.jsx` chart with `AreaChart` + CI bands (actual=green, forecast=blue dashed, upper/lower CI shaded)

### Day 9 — Recharts (Part 2) + Risk + Dashboard
- [ ] Add `RadarChart` to `RiskPage.jsx` (risk.components)
- [ ] Add sparkline `LineChart` (height 60) to `DashboardPage.jsx` (last 6 KPI values)
- [ ] Complete `FinancialPage.jsx`: statement-type dropdown + `BarChart` of line_items
- [ ] Manual smoke test all 4 pages in browser

### Day 10 — WebSocket Streaming Chat
- [ ] Read existing WS chat endpoint in `src/api/server_v2.py`; fix handler bugs (CORS, auth, persona routing)
- [ ] Wire `ChatPage.jsx` to `/ws/chat` instead of POST `/chat`
- [ ] Test all 9 personas through streaming; verify token-by-token render + reconnect logic

### Day 11 — Tests Expansion (→ 30+)
- [ ] Convert `tests/test_api.py` from live-httpx to FastAPI `TestClient`
- [ ] auth (5), chat (4), kpis (4), insights (3), forecast (2), ingest (3), rbac (4), monitoring (3), misc (3)
- [ ] `pytest` green locally; CI green on `develop`

### Day 12 — Railway Deploy + Smoke Test
- [ ] Deploy to Railway (or Fly.io); configure env vars
- [ ] Provision Postgres (Railway add-on or Supabase); run migrations
- [ ] Prod smoke test: `/health`, `/api/docs`, `/api/v1/auth/login`, `/chat`, `/kpis`, `/insights/health`, `/forecast`, WS `/ws/chat`
- [ ] Record the public URL → becomes the Upwork demo link

**Week 1 checkpoint:** 4 chart pages use Recharts · WS streaming chat works · 30+ tests pass · live prod URL exists.

## Week 2 — Demo + Profile + First Proposals (Days 13–18)
- [ ] Day 13: Rewrite README to <200 lines (one-liner, what-it-does, 3-cmd quickstart, default creds, /api/docs link, ASCII arch, demo link); tag v0.1.0
- [ ] Day 14: Record 3-min Loom walkthrough (login→dashboard→CFO persona→chat→Risk→Forecasting); upload
- [ ] Day 15: Pre-review Loom with 3–5 reviewers; mobile + incognito + Lighthouse checks
- [ ] Day 16: Iterate on feedback; set up Upwork profile; add OmniIntelOS as portfolio entry #1 (3 screenshots)
- [ ] Day 17: Write 3 vertical proposal templates (RAG/chatbot, FastAPI/backend, BI/analytics) from STRATEGY.md §26
- [ ] Day 18: Send first 10 proposals (4 RAG / 3 FastAPI / 3 BI); log each in Notion

**Week 2 checkpoint:** Loom recorded + reviewed · Upwork profile live with entry #1 · 10 proposals logged.

## Week 3 — Volume + Blog Post 1 + PyPI Package (Days 19–27)
- [ ] Days 19–21: 8–10 proposals/day (target 30/week); draft Blog Post 1 ("Persona-Routed RAG") in halves
- [ ] Day 22: Blog Post 1 reviewer pass (2 reviewers); add code snippets + arch diagram + eval table
- [ ] Day 23: Save draft to `drafts/blog_post_1_persona_rag.md` + LinkedIn/HN drafts to `writing_workspace/` — DO NOT publish (STRATEGY §5.1)
- [ ] Day 24: Extract `packages/omnismart-personas/` (templates.py, router.py, context.py, pyproject, tests); `pip install -e .`
- [ ] Day 25: Publish `omnismart-personas` to TestPyPI then PyPI; add badge; verify clean-venv install
- [ ] Day 26: 5–10 more proposals (cumulative 50); Phase 1 metrics review
- [ ] Day 27: Buffer + Phase 2 prep (open DocIntel STATUS.md, pre-stage 50 invoice sources)

**Phase 1 final checkpoint:** Deployed · Recharts on 4 pages · WS streaming · 30+ tests · README <200 lines · Loom reviewed · Upwork profile live · 50 proposals · Blog 1 drafted · omnismart-personas on PyPI · 0–3 interviews.
