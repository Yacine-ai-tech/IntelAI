# GAP_REPORT — IntelAI (redesign v2 — 2026-07-06)

## 1. Session-A finding that changed the plan

The v1 redesign prompt assumed a generic dashboard needing a ground-up rebuild. The audit
found the opposite: `frontend/` is a designed, production-verified Vite + React SPA with its
own coherent token system (`index.css` "Copilot" design system: deep-navy layers,
indigo→cyan gradients, per-persona accent colors, Space Grotesk display type), 18 routed
pages, JWT auth with role-based `ProtectedRoute`, TanStack Query, WS-streaming Copilot with
sessions/citations, and full i18n (EN/FR). It is the live flagship (Vercel + Railway).

**Decision (per protocol §"extend > rewrite"):** a destructive reskin would risk the
flagship for marginal gain. The redesign is applied surgically, in the app's own design
language, closing the ONE structural gap the v2 SPEC identified: the app was chat-first
(`/` → `/chat`), with personas buried inside the chat page.

## 2. What shipped

- **New Executive Workspace landing** (`src/pages/WorkspacePage.jsx`), built from the
  app's own primitives (`Stat`, `StatGrid`, `Panel`) and token palette:
  - time-aware greeting (proper EN/FR i18n keys added, not hardcoded strings);
  - live pulse row — Business Health (`/insights/health`), Active Anomalies
    (`/insights/anomalies`), persona count (`/personas`), Indexed Documents
    (`/knowledge/stats`) — all real, same query patterns as DashboardPage;
  - **persona lens grid** — the defining feature surfaced as first-class cards (real
    `display_name`s, per-persona accent colors, focus lines); clicking a lens deep-links
    into the Copilot with that persona active;
  - quick actions routing to real capabilities (Copilot, Forecasting, Anomalies,
    Knowledge, Financial statement, Risk);
  - "Latest executive brief" panel rendering the real `/insights/summary` text.
- **Routing:** `/workspace` registered (permission: `assistant`); index, login redirect
  and catch-all now land on the Workspace instead of the chat. Sidebar gains a Workspace
  entry (EN/FR).
- **Copilot deep-link:** `ChatPage` now honors `?persona=` (mirrors the existing `?q=`
  pattern) so persona cards and future surfaces can open the Copilot pre-scoped.

## 3. Verification (against the LIVE Railway backend)

- Demo-login (admin) via CDP-driven headless Chrome → lands on `/workspace`; screenshot
  shows real data: 9 personas, health 0/100 "Critical" (the seeded declining-financials
  scenario), 547 anomalies, 245 indexed documents, real executive brief text.
- Persona card "CFO Analyst" click → `/chat` with the CFO persona chip ACTIVE (verified
  via DOM inspection).
- Unauthenticated `/workspace` correctly redirects to login. `npx vite build` clean.

## 4. Remaining scope (logged, not attempted in this pass — protect the flagship)

- Page-by-page visual migration of the 17 legacy pages onto a shared kit (they are
  already on-palette via the existing token system; value is incremental).
- Answer-block structuring of Copilot responses (needs response-shape work in the chat
  endpoint — minor backend extension, separate session).
- Governance surface for `/admin/users|roles|audit` beyond the existing AdminPage.

## 5. Real-vs-Demo

Everything on the new Workspace is real (five live endpoints). Nothing demo-labeled.
