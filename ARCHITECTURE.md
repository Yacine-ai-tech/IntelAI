# IntelAI — Architecture & Verification Status

Single source of truth for what's actually confirmed working, what's unverified, and
known drift — kept current as this audit progresses. Everything under "Confirmed
working" was actually run and observed, not inferred from reading code.

Last updated: 2026-08-10 (live audit session).

## Confirmed working (actually run and observed)

- **Backend boots and serves traffic** against the real production Neon Postgres —
  confirmed via `GET /health` returning `{"status":"healthy", ...}` repeatedly.
- **Bilingual glossary seeding** — 202 real EN+FR knowledge docs (101 terms × 2
  languages) seeded into `knowledge_base` on startup, verified in server logs.
- **Auth** — `POST /api/v1/auth/demo-login?role=admin` returns a working JWT.
- **Document ingestion** (`POST /api/v1/ingest/document`) — verified with 14 real
  documents (SEC filings, Salesforce ESG PDF, Orange SA French PDF, IBM/HR CSVs, FRED
  CSVs, NVD JSON) across all 7 domains; all returned 200 with substantial extracted
  text.
- **Cross-project document delegation** — `DOC_PROCESSOR_URL` pointed at the real live
  DocIntel (`docintel.ysiddo-ai-projects.app`), confirmed reachable and responding.
- **Cross-project audio delegation config** — `AUDIO_PROCESSOR_URL` pointed at the real
  live VoiceFlow (`voiceflow.ysiddo-ai-projects.app`), confirmed reachable via `/health`.
  Endpoint itself (`POST /api/v1/ingest/audio`) not yet exercised with a real file — next
  in this pass.
- **RAGeval package-based evaluation** — ran for real against the live DB + Groq/
  Anthropic judges; results in progress, see eval/RAGEVAL_PACKAGE_REPORT.json for the
  latest run once complete.
- **Data seeding**: 146 formula-derived KPI metrics × 78 months × 7 domains generate
  correctly for all 7 scenarios (verified via direct Python invocation, not just reading
  the code).

## Real bugs found live and fixed in this pass

1. **App couldn't boot at all** — `ENVIRONMENT=production` with no `SECRET_KEY` set in
   `.env` hit `validate_required_keys()`'s production guard and crashed on every
   startup. Fixed: added a real `SECRET_KEY` to the local `.env` (does not affect the
   live Render deployment, which has its own separately-configured env vars).
2. **Glossary auto-seed silently broken** — `pg_store.seed_glossary_knowledge_docs()`
   imported from `src.knowledge.glossary` (an empty, orphaned directory left over from
   an incomplete refactor) instead of the real `src.data.glossary`, and passed an
   unsupported `lang=` kwarg. Every server start silently failed to seed the glossary
   docs the RAG copilot depends on for grounded definitions. Fixed, and extended to seed
   both EN and FR (previously English-only).
3. **PDF ingestion crashed the request** — `psycopg.DataError: PostgreSQL text fields
   cannot contain NUL (0x00) bytes` when a real-world PDF's pypdf extraction produced an
   embedded NUL byte. Fixed at the source (`store_knowledge_docs`) so it can't recur for
   any caller, not just this one endpoint.
4. **Document delegation ordering was backwards** — with `DOC_PROCESSOR_URL` configured,
   `ingest_document` delegated to the external processor *first*, unconditionally, and
   only fell back to inline extraction on total failure. For a text-native PDF this is
   worse: DocIntel's OCR route (Route C) got 80 chars from a real 60-page PDF, because
   it renders pages to images and OCRs them instead of reading the PDF's actual text
   layer. Fixed: try pypdf first, only delegate if it yields under 200 chars (a real
   signal of a scanned/image-only PDF pypdf genuinely can't read). Correction to an
   earlier note in this doc: the "669,913 chars" figure from the very first ingestion
   test (before delegation existed) was NOT clean pypdf text — that specific source PDF
   (see item 4b) is malformed enough that pypdf's constructor throws, and the code's
   *old* fallback (`content.decode("utf-8", errors="ignore")`) was raw-decoding the
   entire binary PDF as UTF-8, producing a large blob of low-value garbled text. The
   current code no longer has that silent-garbage fallback for the case pypdf raises
   entirely (falls through to delegation instead) — see item 4b for what's actually
   ingested for that one file now.
4b. **One real source document is malformed at the origin, not a download artifact** —
   the Salesforce FY25 Stakeholder Impact Report PDF, verified byte-identical (matching
   MD5) across three independent downloads including a manual byte-range reassembly, is
   missing a proper `%%EOF`/trailer. pypdf and poppler's `pdftotext` both refuse it;
   DocIntel's OCR fallback extracts only ~80 chars. This is the actual file Salesforce
   serves at that URL, not a transfer problem — documented here rather than silently
   left as "ingested successfully" (`chars: 80` in the ingest response is the honest,
   real number, just a low-value one for this specific file).
5b. **Real audio transcription exceeds the live gateway's timeout in practice** — tested
   `POST /pipeline` and `POST /transcribe` directly against the live VoiceFlow instance
   with a real ~90-second MP3; both attempts hit Cloudflare's 524 (timeout) at ~130s.
   Likely a cold-start/on-demand model-load cost on VoiceFlow's Render free tier rather
   than a code defect — but IntelAI's own `_delegate_to_audio_processor` uses a 120s
   httpx timeout, shorter than what was observed, so a real caller would see IntelAI's
   own timeout fire first. `POST /api/v1/ingest/audio` was NOT successfully verified
   end-to-end with real content in this pass — configuration and reachability are
   confirmed, full pipeline completion is not.
5. **CI env var mismatch** (`.github/workflows/ci.yml` exported `INTERNAL_TOKEN`, the
   test read `OMNIINTEL_INTERNAL_TOKEN`) — integration tests' auth was always failing.
6. **Self-hosting-breaking auth gate undocumented** — `REQUIRE_INTERNAL_TOKEN` defaults
   `true` and gates every route past login; nothing in `.env.example`/README/
   SELF_HOSTING.md mentioned it. A fresh `docker compose up` self-hoster would 403 on
   every real feature with no explanation. Documented.
7. **Dense retrieval silently dead in production** — `sentence-transformers` is
   commented out of `requirements.txt` (too heavy for a 512MB host), and no remote-
   embedding fallback existed, so hybrid retrieval's dense half never ran despite
   `USE_HYBRID_RETRIEVAL=true`. Added remote embedding (HF Inference API or a generic
   Studio/orchestrator contract), verified against the real orchestrator's actual
   `POST /api/inference/embed` contract.
8. **`rag_eval.jsonl` tested a persona that doesn't exist** (`cmo` — the real roster is
   ceo/cfo/cto/coo/chro/esg/risk/analyst/general) and topics never ingested (board
   meetings, marketing budget, ISO 27001, disaster recovery plans) — this, not a RAG
   defect, was the root cause of a very low first-pass RAGeval score. Rewritten against
   real seeded content and real personas, plus French-language cases.

## Step 5 — live browser click-through (all 25 routes)

Actually launched the frontend (Vite dev server) + backend, logged in via demo-login,
and navigated every real route with Playwright (headless Chromium), checking console
errors, failed network requests, and rendered content length per page.

6. **`/api-docs` hung indefinitely (30s+ timeout, no response)** — root-caused live: the
   Vite dev proxy config matched requests by naive string prefix (`'/api'`), and
   `"/api-docs".startsWith("/api")` is true, so the frontend's own in-app documentation
   route was being silently forwarded to the FastAPI backend instead of served as the
   SPA shell. The backend has no handler for that exact path, so behavior was
   inconsistent — a fast 404 most of the time, but a full hang whenever it coincided
   with an intermittent Neon DNS resolution failure (a real, observed, if likely
   sandbox-specific, network flakiness — an unrelated middleware runs DB-dependent code
   on every request regardless of route match). Fixed: proxy prefix changed to `'/api/'`
   (trailing slash) so it only matches the real backend namespace. Verified: `curl
   /api-docs` went from a 10-30s hang to a 200 response in 0.06s. This is a **dev-only**
   bug — production's `vercel.json` rewrites don't have the same prefix-collision (its
   catch-all correctly falls through to `index.html` for `/api-docs`).
7. Every other of the 25 real routes rendered substantial content (10-30k+ characters)
   with **zero React console errors** once authenticated and once `REQUIRE_INTERNAL_TOKEN`
   was disabled for local testing (see finding 6 above in the earlier list — this is the
   same gate, now empirically confirmed to 403 every single API call the frontend makes,
   across every page, when left at its documented default with no gateway in front).
   Investigated one apparent "blank page" (Analytics, ~73 rendered characters under the
   all-403 condition) and determined it was NOT a bug: that's the app's own intentional
   error-boundary fallback text ("No Analytics Data Available…") correctly firing —
   working as designed, not broken.

## Known drift / not yet done

- **Audio ingestion untested with a real file** — `AUDIO_PROCESSOR_URL` is wired to the
  live VoiceFlow, but `POST /api/v1/ingest/audio` hasn't been called with a real audio
  file yet in this pass.
- **`/agent/run`, `/agent/tools`, `/chatbot/domain`, `/admin/vsdebug`** — real backend
  endpoints with zero UI callers anywhere in the frontend (only referenced in
  `ApiDocs.tsx`'s own documentation). Not confirmed broken, just confirmed unreachable
  from the app itself — worth a decision (wire to UI, or accept as API-only/
  power-user features).
- **Vertical positioning datasets** (3 flavored demo datasets per STRATEGY.md §1.4) —
  still not done.
- **Qdrant not exercised locally** — the dev/test environment doesn't have
  `qdrant-client` installed, so all local testing in this pass ran against in-process
  retrieval, not the configured `VECTOR_STORE=qdrant`. The live Render deployment may
  behave differently; not verified in this pass.
- **Production-parity deployment test** (Docker build, prod CMD) — not yet done in this
  pass.
- **Steps 8/9 (portfolio-wide env hygiene, further live-write verification)** — not yet
  done in this pass.

## Environment this was verified against

Local dev run (`python main.py`) pointed at the **real production Neon Postgres** (by
explicit user go-ahead, since no local/Docker Postgres was available in this sandbox).
Qdrant configured but unreachable from this environment (`qdrant-client` not installed
here) — falls back to in-process retrieval. LLM calls are real (Groq, Anthropic).
