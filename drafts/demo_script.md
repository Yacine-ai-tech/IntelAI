# IntelAI — 3-Minute Loom Demo Script

> **DRAFT.** Record once for timing (no audio), then a final take with audio. Upload to
> Loom (free 5-min plan). Put the link at the top of the README, Upwork profile, and every
> proposal. Use the seeded demo data (`make seed`) so every panel has content.

**Setup before recording:** Studio running (`bash ~/switch-project.sh IntelAI`), frontend
`npm run dev` (laptop), logged out, browser at full screen, seeded DB.

---

**0:00–0:15 — Hook.**
"Hi, I'm Yacine. IntelAI is a production AI analytics backend with a 9-persona RAG copilot —
each role talks to its *own* data. Let me show you." (Land on the login page — note the new
Indigo Nebula UI.)

**0:15–0:45 — Login + persona-scoped dashboard.**
Log in as `admin` (or the CFO role). Land on the Dashboard: health index, KPI cards with
sparkline trends. "Every number here is real data from the seeded multi-domain warehouse —
Finance, HR, IT, Operations, Logistics, ESG."

**0:45–1:15 — The copilot (streaming + citations).**
Open Chat as the **CFO** persona. Ask: *"Why might gross margin move this quarter?"* Watch
the answer stream token-by-token with **source citations**. "The CFO persona only sees
Finance and Growth data — that scoping is enforced before retrieval, so it can't leak HR data."

**1:15–1:35 — Persona switch.**
Switch to **CHRO** mid-session. Ask: *"What's our headcount and turnover trend?"* Different
voice, different data scope. "Same retrieval system, different role — that's persona-routed RAG."

**1:35–2:05 — Forecasting + Risk.**
Forecasting page: select Revenue → AreaChart with confidence-interval bands. Risk page:
RadarChart + the seeded anomalies (churn spike, security incident). "Anomaly detection feeds
the Risk radar automatically."

**2:05–2:30 — GraphRAG-lite (the differentiator).**
Back in Chat, ask a multi-hop question: *"How does headcount relate to finance margin
recently?"* "With GraphRAG-lite on, it ranks KPI records by entity overlap instead of
returning disjoint snippets."

**2:30–2:45 — Trust.**
"It ships with an eval gate — `make eval` scores groundedness on 25 prompts and fails the
build if quality drops. And it's bilingual EN/FR."

**2:45–3:00 — CTA.**
"Live demo at <URL>. Code at github.com/Yacine-ai-tech/IntelAI. The persona layer is on PyPI
as `omnismart-personas`. Find me on Upwork." (End on the dashboard.)
