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

## RAG retrieval — why it returned nothing (all measured, not inferred)

Retrieval returned **zero documents** for most queries. The knowledge base was never
the problem (733 docs; "cash runway" appears in 7, "Rule of 40" in 9). Four independent
defects, each sufficient on its own to produce an ungrounded answer:

8. **No chunking at all.** `CHUNK_SIZE`/`CHUNK_OVERLAP` have sat in `core/config.py`
   unreferenced by any code. Documents were embedded whole — 7 docs over 30k chars, max
   50k. A single fixed-length vector cannot represent a 50k-char report and anything past
   the model's context window is silently truncated; BM25 term weights dilute the same
   way. Now split into overlapping passages (733 docs → 1,368 passages) with the matching
   *passage* returned, not the whole document.
9. **`TfidfVectorizer(max_features=100)`.** Measured on the real corpus: a 100-word
   vocabulary in which "runway" does not appear, so "What is our cash runway in months?"
   scored **0.0000 against every one of the 733 documents** and the path returned nothing.
   With a realistic vocabulary the same query scores **0.6318** and matches 26 documents.
   Fixed (50k features, bigrams, sublinear tf, title indexed alongside content).
10. **The TF-IDF path returned its empty result instead of falling through** to the
    keyword search below it, so a zero-match TF-IDF run ended retrieval entirely.
11. **The production embedding endpoint was dead.** `api-inference.huggingface.co` has
    been retired by HF; dense retrieval had been non-functional in production regardless
    of the above. Working replacement verified: `router.huggingface.co` (1024-dim, 1.5s).
    A dead embedding host also killed the *whole* hybrid retriever (BM25 included) —
    now it degrades to BM25-only with a loud error instead of returning nothing.

### Retrieval, before vs after (same queries, same corpus, measured)
| Query | Before | After | Top match |
|---|---|---|---|
| What is our cash runway in months? | **0 docs** | **1.000** | Glossary: Cash Runway (26.78 months) |
| What is our renewable energy ratio? | **0 docs** | 0.905 | Glossary: Renewable Energy % |
| What is our LTV to CAC ratio? | **0 docs** | 0.994 | Glossary: LTV:CAC |
| What is our change failure rate? | **0 docs** | 0.994 | Glossary: Change Failure Rate |
| Quelle est notre marge brute ? | **0 docs** → 0.137 (wrong doc: LTV) | **1.000** | Glossaire: Marge brute (Gross Margin) |
| Quel est notre taux de rotation du personnel ? | **0 docs** | **1.000** | Glossaire: Taux de rotation du personnel |

The French rows are the fix in defect 14 below; the rest are defects 8–11.

14. **French documents never contained the French name of their own metric.** The FR
    glossary translated definition/benchmark but kept the English term as the title, so
    "marge brute" appeared nowhere in the Gross Margin document and no French query could
    retrieve it. Added 63 French term names + an explicit alias line, only where a genuine
    standard French term exists — metrics French business usage keeps in English (churn,
    EBITDA, NRR, OEE, MTTR, KPI, ARR/MRR, uptime) are deliberately left in English rather
    than given an invented translation.

### Inference backends — measured
| Backend | Embed | Rerank |
|---|---|---|
| HF router | 200, 1024-dim, 1.5s | 0.82 (relevant) vs 0.000016 (irrelevant) |
| Orchestrator `/api/inference` | 200, (2,1024), BAAI/bge-m3 | 0.833 vs 0.0000164 |

The orchestrator's studio tunnel was down (Cloudflare **1033**, all 4 studios HTTP 530)
until woken via `POST /api/studios/1/wake`; both capabilities work once it is up. First
embed after a cold wake took ~25s, so production timeouts are set generously
(`EMBED_TIMEOUT=120`, `RERANK_TIMEOUT=90`). Production embed+rerank now point at the
orchestrator.

## Deployment — why production was broken

12. **Every Render deploy has failed since at least 2026-08-09**: `COPY frontend
    /app/frontend` → `"/frontend": not found`, because `.dockerignore` excluded all of
    `frontend/` while the Dockerfile still copied it. The live service has been serving
    stale code. Fixed (explicit excludes, keep `frontend/dist`, copy only `dist`).
13. **`SECRET_KEY` was missing on Render while `ENVIRONMENT=production`** — the exact
    combination `validate_required_keys()` aborts startup on. Set, along with 19 other
    required vars (delegation URLs, explicit providers, CORS, demo config).

## RAGeval re-measurement — preconditions now met (2026-08-11)

The re-run was deferred while RAGeval was mid-flight, because measuring against a stale
evaluator would have produced numbers about the evaluator rather than IntelAI. All three
preconditions now hold:

| | 2026-08-10 (blocked) | 2026-08-11 (verified) |
|---|---|---|
| RAGeval working tree | 12 uncommitted files | **clean**, at `7183196` "bump to 0.1.16, published to PyPI" |
| PyPI latest | 0.1.14 | **0.1.16** |
| Installed here | 0.1.9 | **0.1.16** |

The package imports as `rageval`; `RAGEvaluator.score_interaction(...)` is unchanged, so
the existing scripts are compatible. 0.1.16 adds
`score_groundedness_consensus(answer, context)` — multi-judge consensus across the
configured `JUDGE_MODELS` — which is the right instrument for the research benchmarking
in steps 12–15.

**The evaluation set had to be rebuilt first, and this matters for interpreting any
score.** The previous 30 cases asked about gross margin, EBITDA and net profit — metrics
that belonged to the deleted generated data. Against the real corpus those questions have
no answer, so the scores would have measured the mismatch, not the system. The set is now
generated from the database by `scripts/build_rag_eval_set.py`: 38 cases (19 KPI, 7
French, 9 document, 2 glossary, 1 cross-domain) across 8 personas, each naming a metric
that exists for a period that exists or a document present in `knowledge_base`. Cases
that cannot be verified are dropped rather than shipped — one was, for a glossary term
that does not exist.

The old measurement (25/30 cases, avg groundedness 22.8%, overall 11.6%) is stale on
**three** counts now — it predates every retrieval fix here, used evaluator 0.1.9, and
was scored against a corpus that no longer exists. It is not a baseline for anything and
should not be quoted.

## Step 10 — production-parity run (prod CMD, same origin, no dev proxy)

Ran the Dockerfile's actual CMD (`uvicorn src.api.server:app`) with FastAPI serving
`frontend/dist` itself — the single-container topology from SELF_HOSTING.md — rather than
the Vite dev server. That immediately surfaced a bug dev mode cannot show:

15. **Every client-side route 404'd in the single-container deployment.** `/dashboard`,
    `/chat`, `/api-docs`, `/settings`, `/knowledge-graph`, `/financial` — all 404; only
    `/` worked. The frontend is a client-side-routed React app, so those paths exist only
    in the browser's router and FastAPI had no fallback. Practical effect for a
    self-hoster: the app loads and in-app navigation works, but **refreshing any page,
    opening a bookmark, or following a shared link fails**. The hosted demo masks it
    entirely — `vercel.json` already rewrites `/(.*)` to `/index.html` — which is exactly
    why it survived this long. (VoiceFlow already had such a catch-all; IntelAI was the
    outlier.) Fixed with a last-registered SPA fallback that excludes api/health/docs/
    assets paths so a wrong endpoint still returns a JSON 404 rather than HTML.
    Verified after the fix: all six deep links 200 and return the SPA; a bogus
    `/api/v1/does-not-exist` still returns `{"detail":"Not Found"}` with 404.

Static analysis (`pyflakes src/ scripts/ main.py`) is clean — only cosmetic findings
(duplicate `import os`/`uuid` in server.py, one unused local in pg_store.py, one unused
import in scripts/api_audit.py); no correctness defects.

**Docker itself was not run** — no docker binary and no passwordless sudo in this
environment — so the image build is unverified. What was verified is the thing the image
would run: the exact production CMD, same-origin static serving from `frontend/dist`, and
the API under that topology.

## Steps 7 & 9 — cross-project integration + real writes

16. **Three id sequences had fallen behind their tables — every INSERT was failing.**
    Found by exercising the HMAC-signed webhook's *happy path* (the auth paths were
    already correct: 501 with no secret configured, 401 for missing and for wrong
    signature). A correctly-signed request returned **500**:
    `psycopg.errors.UniqueViolation: duplicate key value violates unique constraint
    "kpi_metrics_pkey" DETAIL: Key (id)=(3) already exists.`

    | table | rows / max(id) | sequence was at |
    |---|---|---|
    | `kpi_metrics` | 10,452 | **3** |
    | `kpi_entities` | 50,783 | **1** |
    | `audit_trail` | 23 | **1** |

    So KPI ingestion (webhook **and** CSV **and** metrics), GraphRAG entity writes, and
    audit logging were all broken on insert — a silent, total write outage on the live
    database. The INSERTs never name `id`, so this came from rows arriving outside the
    sequence (bulk COPY / dump-restore / a migration carrying ids across), which is how a
    seeded database normally gets populated — meaning it will recur.

    Fixed durably rather than by hand: `_resync_serial_sequences()` runs at startup,
    finds every SERIAL sequence in `public`, and `setval`s it to
    `GREATEST(max(id), current sequence value)` — never rewinds a healthy sequence, is
    idempotent, and self-heals after any future bulk load. Confirmed in the startup log
    of a fresh boot: `Verified/resynced 3 id sequence(s)`.

    Verified after the fix, against the real database: a correctly-signed webhook returns
    `{"status":"success","processed":1,"type":"kpi_metrics"}` 200. The single probe row
    was written with an unmistakable tag (`metric='WebhookVerifyProbe'`,
    `source='CLAUDE_VERIFY_PROBE'`), then deleted with verification — `kpi_metrics` is
    back to exactly 10,452 rows and 0 probe rows remain.

## The dataset was generated, not measured — replaced 2026-08-11

The per-project database migration was expected to deliver real data. It did not: the new
database (`ep-wandering-mode…/neondb`) was a verbatim copy of the old one — identical
counts (10,452 / 50,783 / 733 / 24) — and `kpi_metrics` was **100% `source='seed_healthy'`**,
the generated catalog. Of 733 knowledge documents only **17** were real; 413 were generated
KPI summaries that described themselves as *"the authoritative, comprehensive record …
audited by the internal compliance team"* above figures including `Gross Margin: 100.0 %`.

Replaced with published data, loaded through the public API:

| | before | after |
|---|---|---|
| `kpi_metrics` | 10,452 rows, 1 source (`seed_healthy`) | **2,070 rows, 26 real sources, 0 without provenance** |
| real documents | 17 (5 truncated at 50,000 chars) | 251 incl. 236 bilingual KPI digests |
| audio | none persisted | 13,186-char transcript (Richmond Fed MP3, via the audio processor) |
| images | **none existed in the corpus at all** | 5 FRED chart PNGs, OCR'd via the document processor |
| glossary | 303 rows, 101 duplicated titles | 202 rows, 0 duplicate titles |

Verification that the numbers are the publishers': `fred:INDPRO` 2026-06 stored `102.6395`
against `102.6395` in the downloaded series (2026-04 and 2026-05 also match exactly).
Generated rows were backed up before deletion.

### Bugs this surfaced, all fixed

1. **Silent 50,000-char truncation** (`server.py` document + audio ingest). An 82-page
   filing extracting 277k characters kept its first 50k and the response said nothing.
   Nothing downstream needs a pre-truncated row — `chunk_text()` splits at index time.
   Measured after: HR CSV 50,000 → **154,025**; attrition 50,000 → **128,965**; 10-K → 53,981.
2. **Per-row provenance was discarded.** `store_kpi_metrics()` stamped every row with the
   single `source_name` form field, erasing exactly what makes a figure checkable. A
   per-row `source` column now wins; `source_name` remains the default.
3. **The official API could not seed the shared baseline.** `/api/v1/ingest/csv` scoped
   rows to the uploader, so "seed through the API" could only produce data private to
   whoever ran it. Added admin-only `global_scope=true` (NULL owner), keeping the
   per-user default that exists for good multi-tenant reasons.
4. **One env var fed two endpoints with different route vocabularies.**
   `DOC_PROCESSOR_ROUTE=ocr_fallback` went to both `/process` (which accepts it) and
   `/extract/text` (which accepts `auto|marker|ocr`). Matching neither branch, it fell to
   the weakest path — and a 32-character result for a 1.2MB report was then accepted as
   success. Split into `DOC_PROCESSOR_TEXT_ROUTE` (default `ocr`, fast and $0 for digital
   PDFs) and `DOC_PROCESSOR_ROUTE`; added `DOC_PROCESSOR_MIN_CHARS` so a non-empty but
   implausibly short extraction escalates to the next endpoint instead of being accepted.
5. **101 duplicate glossary rows** — a legacy single-language set coexisting with the
   EN/FR set, near-identical passages competing in retrieval.

### Honest limits of the real data

- **The domains are not equally deep.** Real monthly series are abundant for Finance,
  People, Operations, Logistics; ESG has no free monthly series, so it gets breadth of
  indicator (4 World Bank annual indicators) instead of frequency.
- **NVD is a 400-per-window sample**, not the full population — comparable across months
  because every window is sampled identically, and named "Published CVEs (sampled)".
- **The IBM HR survey has no date column.** It yields point-in-time aggregates under one
  period; a monthly history was not invented from it.
- **There are no scenarios in real data.** The seven health scenarios remain a property of
  the generator, which is retained for offline demos and labelled `seed_*` so it can never
  be confused with measurement.
- Corrected two overstatements in the previous documentation: the IBM dataset is **832
  rows, not 1,470**, and the churn dataset **4,093, not ~14,999** — both downloads are
  partial relative to the published originals.

### Blocked externally (document processor)

Three files cannot currently be ingested: the Orange S.A. H1-2025 report (890KB, 82pp),
`fred_chart_RSXFS.png`, and the Salesforce ESG PDF (stuck at 32 chars). All return
Cloudflare **502s from the processor's origin on every route**, while `/health` and other
files of similar size succeed — and all three extracted successfully in earlier testing
(the Orange report yielded 276,265 chars). This is a processor-side regression, recorded
rather than worked around.

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
