# STRATEGY.md — Claims vs. Reality Audit

**Question that triggered this:** STRATEGY.md says IntelAI uses **ChromaDB**, but ChromaDB
was removed from `requirements.txt` and isn't in the code. So what *else* does STRATEGY.md
claim is present that isn't actually implemented?

**Short answer:** a lot — because most of [STRATEGY.md](../STRATEGY.md) is an **audit of the
pre-split OmniIntelOS codebase**, written before IntelAI was scoped down. Section 3 even says
*"Real Codebase Inventory (Audited) — Verified by reading the repo… Line counts are exact
from `wc -l`,"* and the intro claims the doc is *"grounded in the actual code in this repo."*
After the Day-8 scope-down (which deleted OCR, voice, n8n, monitoring, integrations,
SQLAlchemy models, the second chatbot, etc.), those sections describe code that **no longer
exists in IntelAI**.

This is **documentation drift**, not (mostly) broken code — with one important exception
(§E), the drift is the doc over-claiming, while the actual app is the leaner, working subset.

**Method:** cross-checked each concrete claim in STRATEGY.md against the live repo —
`requirements.txt`, the `src/**/*.py` tree, `frontend/src/pages/`, and `grep` of the source.

**Legend:** ❌ claimed present, not implemented · ⚠️ stale / now-different · ✅ claimed and
actually present · 💬 recommendation (aspirational — *not* drift).

---

## A. Vector store / RAG stack (the ChromaDB family)

| Claim in STRATEGY.md | Where | Reality | |
|---|---|---|---|
| "omnismart_chatbot.py … **LangChain RAG, ChromaDB integration**" | L282 | No `langchain` dep; no `chromadb` dep; not imported anywhere in `src/`. The copilot uses the **Groq SDK directly** + a custom retriever. | ❌ |
| "RAG, **LangChain, ChromaDB**, document Q&A" positioning | L209 | Same — neither library is used. | ❌ |
| "from pure **ChromaDB cosine similarity** to hybrid retrieval + reranker" | L691 | There is no Chroma store; retrieval is **BM25 + in-memory dense embeddings** (when ML extras load) fused via RRF. | ⚠️ |
| "README should say **'ChromaDB for dev, Qdrant for prod'**" | L737–738 | **Qdrant** is not implemented (no dep, no client). | 💬 / ❌ |
| Project-1 feature line "… GraphRAG-lite, **Qdrant**" | L62 | GraphRAG-lite ✅; Qdrant ❌. | ⚠️ |
| (implied) a persistent vector store | — | The actual vector store is **none** — `knowledge_docs.embedding` is stored as empty text; dense vectors are computed **in-memory at fit time** each process. Not Chroma, not Qdrant, not pgvector. | ❌ |

**Bottom line (original audit):** the "ChromaDB/LangChain/Qdrant/pgvector" framing was
inaccurate when this audit was written.

> **✅ Update — RAG-core PR:** the vector-store claims are now **real and verified**. A
> pluggable `VECTOR_STORE` backend (`memory` | `chroma` | `pgvector` | `qdrant`) was added
> ([vector_store.py](../src/services/vector_store.py)); Chroma + pgvector (on Neon) + Qdrant
> were each verified to index 236 docs and retrieve. The BGE reranker was fixed (now a
> `CrossEncoder`, so the "+ BGE reranker" claim holds). **Still outstanding:** LangChain is
> not used (planned: a LangChain adapter in `omnismart-personas`).

---

## B. Deleted backend modules still listed as present (Section 3 inventory)

Section 3 presents these as the current codebase (with exact line counts). All are **deleted**
in IntelAI:

| Claimed file | Where | Reality |
|---|---|---|
| `src/services/advanced_chatbot.py` (5 Groq patterns, agentic, **Tavily** search) | L283 | ❌ deleted; no `tavily` dep |
| `src/integrations/dispatcher.py` (Gmail/Sheets/n8n/TTS/Voice) | L284 | ❌ no `src/integrations/` at all |
| `src/services/data_ingestion_manager.py` | L285 | ❌ deleted |
| `src/services/realtime_pipeline.py` | L286 | ❌ deleted |
| `src/integrations/n8n.py` | L287 | ❌ deleted |
| `src/services/ocr_enhancement.py` (pdfplumber + tesseract) | L288 | ❌ deleted; no OCR deps |
| `src/models/pg_models.py` (**SQLAlchemy** models) | L292 | ❌ `src/models/` deleted; no `sqlalchemy` dep (data layer is raw `psycopg`) |
| `src/services/auth.py` | L300 | ❌ deleted (canonical auth is `core/jwt_auth.py`) |
| `src/integrations/camera.py` (QR pairing/mobile upload) | L301 | ❌ deleted |
| `src/services/lazy_loader.py` | L302 | ❌ deleted |
| `src/core/performance.py` (latency tracking) | L303 | ❌ deleted |
| `src/integrations/tts.py` | L304 | ❌ deleted |
| `src/core/monitoring.py` (**Prometheus** emitter) | L305 | ❌ deleted; no `prometheus-client` dep |
| `src/core/pg_engine.py` / `src/core/db_engine.py` | L306, L314 | ❌ deleted |
| `src/services/voice/main.py` (faster-whisper + edge-tts) | L307 | ❌ deleted; no whisper/tts deps |
| `src/services/ocr/main.py` (Tesseract) | L308 | ❌ deleted |
| `src/models/schemas.py` | L310 | ❌ `src/models/` deleted |
| `src/services/ingestion.py` | L313 | ❌ deleted |

Also stale **line counts / totals**: "Backend ~14,000 lines", `server.py` **2,579** (actual
≈1,340), `omnismart_chatbot.py` **1,658** (actual ≈842), `pg_store.py` **1,669** (now larger).

---

## C. Frontend inventory drift (Section 3)

| Claim | Where | Reality |
|---|---|---|
| "**19 pages**" | L319 | ❌ **16** pages |
| `ScannerPage.jsx` (Camera + OCR) | L325 | ❌ deleted |
| `IntegrationsPage.jsx` (Gmail/Sheets/ClickUp) | L330 | ❌ deleted |
| `MonitoringPage.jsx` (Prometheus) | L337 | ❌ deleted |
| `BulkDataPage.jsx` (stub) | L341 | ❌ deleted (ingestion folded into DataHub) |
| `ChatPage.jsx` "**uses HTTP not WebSocket**" | L326 | ⚠️ now wired to `/ws/chat` streaming (Day 10) |
| `AnalyticsPage.jsx` "**hand-coded SVG bar charts**" | L328 | ⚠️ now Recharts |
| `ForecastingPage.jsx` "**lacks proper chart**" | L336 | ⚠️ now AreaChart + CI bands |
| `FinancialPage.jsx` "**Stub — 70 lines**" | L340 | ⚠️ now a full page (and bug-fixed; see BUGS §3.1) |
| components incl. `PairingModal`, `DataIngestionPanel`, `FloatingChat` | L343 | ⚠️ replaced by the shared `ui.jsx` kit + `ContextualExplainer` |

---

## D. Removed feature surface still described

| Claim | Where | Reality |
|---|---|---|
| `docker-compose.yml` "**13 services**: postgres, fastapi, frontend, prometheus, grafana, n8n, ocr, voice, tunnels" | L350–351 | ⚠️ single-app `docker-compose.dev.yml` + `railway.toml` |
| `monitoring/` (Prometheus + Grafana) | L356 | ❌ removed |
| `n8n_workflows/` (4 workflows) | L358 | ❌ removed |
| `tunnels/` (Cloudflare configs) | L359 | ❌ removed |
| `db/schema.sql` | L360 | ❌ removed (tables created idempotently in `pg_store`) |
| `scripts/` "10 ops shell scripts" | L357 | ⚠️ not in the repo |
| API group "**INTEGRATIONS (9)** Gmail/Sheets/ClickUp OAuth" | L373 | ❌ removed |
| API group "**VOICE/OCR (4)** transcribe, tts, ocr/extract" | L374 | ❌ removed |
| API group "**CAMERA (5)** pair, upload, sessions" | L375 | ❌ removed |
| ADMIN includes "**monitoring, /metrics**" | L376 | ❌ removed (and a test for `/metrics` was deleted) |
| "**60+ endpoints**" | L363 | ⚠️ ~62 routes, but a *different* set (no voice/ocr/camera/integrations) |
| Personas "All **6 domains**" | L383+ | ⚠️ there are **7** domains (Finance, Growth, People, Operations, IT, Logistics, ESG) |

---

## E. Drift that is also a *live bug* (needs a code fix, not just a doc edit)

**`/api/v1/knowledge/search` is broken.** The endpoint in [server.py](../src/api/server.py)
is headed `# VECTOR SEARCH (ChromaDB)` and does `from src.services.pg_store import
search_vectors` — but **`search_vectors` does not exist** in `pg_store` (it was a
Chroma-era function dropped in the scope-down). The import raises, the broad `try/except`
swallows it, and the endpoint silently returns empty. The frontend "Search the knowledge
base" on [KnowledgePage.jsx](../frontend/src/pages/KnowledgePage.jsx) and
[DataHubPage.jsx](../frontend/src/pages/DataHubPage.jsx) therefore never returns results.

→ Tracked in [BUGS_AND_FIXES.md](BUGS_AND_FIXES.md) §1.4. **✅ Fixed in the RAG-core PR** —
the endpoint now calls the shared retriever (vector store + hybrid), and the missing
`search_vectors` import and "ChromaDB" label are gone.

Minor cosmetic residue: `chromadb` still appears in the noisy-logger suppression list in
[logger.py](../src/core/logger.py) (harmless).

---

## F. What is NOT drift (legitimate, leave as-is)

These read like claims but are correctly framed as **strategy / recommendations / other
projects** — not assertions about IntelAI's current code:

- The per-project "2026 stack upgrades" for **other** products (VoiceFlow WhisperX/Deepgram,
  RAGeval multi-judge/pgvector, StreamPulse n8n/Prefect, AgentKit CrewAI/DSPy) — sections
  1.10/2.10/4.10/5.10/6.10. These describe siblings, not IntelAI.
- The "swap ChromaDB → Qdrant/pgvector for prod" guidance and vector-DB comparison table —
  explicitly *recommendations* (💬), though they now read oddly since IntelAI never shipped
  Chroma in the first place.
- Model/pricing tables and market positioning commentary.

---

## G. Things STRATEGY.md *under*-claims (already fixed but still listed as weaknesses)

Section 4 ("What's Weak…") lists issues that have since been resolved — so the doc now
understates IntelAI:

- "**WebSocket streaming chat is built but not wired**" (L449–451) → it **is** wired now.
- "hand-coded SVG bars" (L433) / Recharts conversion "to-do" → **done** on all 5 chart pages.
- GraphRAG-lite / hybrid retrieval framed as future → **implemented** and behind flags.

---

## Recommendation

STRATEGY.md is doing two jobs at once: (1) a **historical audit of OmniIntelOS** and (2) the
**forward strategy for IntelAI**. Post-split, job (1) is misleading because it's presented as
IntelAI's current state. Options, in order of preference:

1. **Replace Section 3** ("Real Codebase Inventory") with the *actual* IntelAI inventory
   (the `src/` tree above, 16 pages, ~62 routes, Postgres-only data layer, BM25+BGE+RRF
   retrieval, no Chroma/LangChain/OCR/voice/n8n), and update Section 4 to drop the
   already-fixed weaknesses. Keep Sections 1–2 + the strategy/recommendations.
2. Or **label Section 3 clearly** as "Historical — pre-split OmniIntelOS audit (not IntelAI's
   current code)" so the "grounded in the actual code" claim isn't violated.
3. Either way, **fix §E** (the broken knowledge search) since that's real code, not docs.

I can do (1) + (3) on request — say the word and I'll update STRATEGY.md to match reality and
wire the knowledge-search endpoint to the working retriever (with tests + the usual 3-way
sync).
