# IntelAI Data: OmniIntelOS, and why every number in it can be checked

This describes the dataset IntelAI runs on, how to rebuild it, and what is deliberately
missing. It documents the current implementation, not an intended one.

**The dataset is a generated virtual company: OmniIntelOS S.A.** It is fictional. No
figure here is any real company's disclosed result, and nothing in this repository should
be read as one. What makes it trustworthy is not a claim of realness — it is that the
data is *internally verifiable*, *causally coherent*, and *honestly labelled* at every
layer, right down to the disclosure line printed inside each generated PDF.

---

## 1. The company

|  |  |
|---|---|
| Legal name | OmniIntelOS S.A. (Société Anonyme, OHADA) |
| Headquarters | Niamey, Niger |
| Founded | March 2019 |
| Industry | Applied AI / enterprise SaaS |
| Functional currency | XOF (BCEAO franc, fixed peg 655.957 = 1 EUR); reports in USD |
| Languages | French (HQ, Sahel operations) and English (international) |
| Scale at Jun 2026 | ~USD 52M annualised revenue, ARR ~USD 33M, 411 employees, ~USD 128k revenue per employee |

**Service lines** — data science & analytics platform (SaaS), computer vision (industrial
inspection, agri-monitoring), NLP & bilingual FR/EN document intelligence, IoT & edge
telemetry, blockchain provenance, custom software engineering, managed data centres.

**Footprint** — Sahel (Niger HQ, Mali, Burkina Faso, Chad); West Africa (Senegal, Côte
d'Ivoire, Ghana, Nigeria); North & East Africa (Morocco, Kenya); Europe (France,
Belgium); Americas (US, Canada).

**Partners** — universities (Abdou Moumouni, Cheikh Anta Diop), engineering and
manufacturing integrators, regional banks and microfinance institutions, public-sector
agencies, telcos.

---

## 2. Why generated rather than assembled from public sources

An earlier version of this dataset was built from real public series — FRED, World Bank,
NVD, an IBM HR survey, Sonatel's published communiqués. That approach failed for a
specific, measurable reason:

- The metrics enterprise dashboards actually need — SLA compliance, MTTR, ticket volume,
  MRR/ARR/CAC/LTV, recruiting funnel, OEE — describe **one company's private internal
  systems**. No publisher reports them for an arbitrary company.
- So the corpus filled up with external macro context instead. **53% of all rows were US
  national statistics**, each correctly carrying a "not this company's own measured
  output" disclaimer. Ask the copilot about the company and it hedged, because the honest
  answer was that the data was about the US economy.
- Coverage was also uneven: company-specific data existed for **18 of 78 months**. Any
  question about 2020–2024 had nothing behind it.

Generating a coherent company fixes both. The cost is that the company is fictional — so
the rest of this document is about making that cost safe.

---

## 3. What makes the numbers trustworthy

### 3.1 Only primitives are modelled; every ratio is computed

`scripts/omniintelos.py` models primitives — revenue, COGS, headcount, incidents, kWh,
customers, cash. Every ratio a dashboard displays is then **computed from those
primitives using the standard formula**, so it can be re-derived from other rows in the
same period:

```
Gross Margin   == (Revenue - COGS) / Revenue          exact, all 78 months
EBITDA Margin  == EBITDA / Revenue
Net Margin     == Net Income / Revenue
Debt to Equity == Total Debt / Shareholders Equity
OEE            == Availability x Performance x Quality
Rule of 40     == YoY revenue growth % + EBITDA margin %
NRR            == (Start ARR + Expansion - Contraction - Churn) / Start ARR
Turnover %     == Separations x 12 / Headcount
```

If a stored value and its formula disagree, that is a real bug, not modelling noise. This
is the single most important property of the dataset: **it is checkable.**

### 3.2 The frameworks are real, even though the company is not

| Framework | Used for | Real? |
|---|---|---|
| GHG Protocol Corporate Standard | Scope 1/2/3 boundary and accounting | Yes |
| Google DORA | Deployment frequency, lead time, change failure rate, MTTR | Yes |
| CVSS v3.1 | Critical = base score ≥ 9.0 | Yes |
| OEE (Nakajima) | Availability × Performance × Quality | Yes |
| SaaS standards | Rule of 40, NRR, LTV:CAC, CAC payback | Yes |
| OHADA / SYSCOHADA | Statutory accounting basis for a Niger S.A. | Yes |
| BCEAO XOF/EUR peg | 655.957, fixed | Yes — verifiable constant |
| Niger corporate income tax | 30% | Yes |

The healthy/risk thresholds every generated document judges itself against are
transcribed from IntelAI's own published domain specification, so a statement like
"below target" is checkable against both the stored value and the published band.

### 3.3 The history is one causal narrative, not seven random walks

Domains are correlated because they are **generated from shared drivers with realistic
lags**, not decorated after the fact. The clearest case is the February 2023 breach:

| Month | Uptime % | SLA % | Security score | Logo churn % | Revenue USD | Health |
|---|---|---|---|---|---|---|
| 2022-12 | 99.63 | 96.2 | 81.8 | 1.42 | 658,935 | Stable |
| 2023-01 | 99.83 | 98.8 | **51.6** | 2.47 | 676,785 | ← posture degrades first |
| 2023-02 | **96.42** | **68.0** | 54.6 | 2.78 | 656,747 | **Critical** |
| 2023-03 | 98.15 | 78.4 | 49.9 | 2.28 | 655,399 | recovering |
| 2023-04 | 99.65 | 96.3 | 52.6 | **2.80** | 652,146 | ← churn peaks *after* uptime recovers |
| 2023-05 | 99.67 | 96.3 | 51.2 | 2.20 | 654,978 | revenue still depressed |
| 2023-06 | 99.84 | 98.8 | **92.2** | 1.56 | 662,438 | post-remediation |

Security posture degrades **before** the incident (the latent MFA gap and stale
contractor credential the post-mortem describes). Availability collapses during
containment. SLA follows availability, because SLA compliance is derived from it. Churn
and revenue stay depressed into April and May — **after** uptime has recovered — which is
the lagged customer consequence, and the cascade IntelAI's own domain spec describes.

### 3.4 It is deterministic

All variation comes from a SHA-256 hash of `(metric, period)`. The same period always
produces the same value, so re-seeding never silently rewrites history.

---

## 4. The 78-month timeline: 12 health regimes

Jan 2020 → Jun 2026, every month populated for all 7 domains. The composite health index
spans **26.2 to 94.9** and visits all four bands, because each phase is a distinct
operating regime with an explicit cause.

| # | Period | Months | Regime | Health |
|---|---|---|---|---|
| 1 | 2020-01 → 2020-03 | 3 | Early traction | Stable |
| 2 | 2020-04 → 2020-09 | 6 | COVID-19 shock and pivot | At Risk |
| 3 | 2020-10 → 2021-06 | 9 | Digital-transformation tailwind | Stable |
| 4 | 2021-07 → 2022-03 | 9 | Series A and hypergrowth | Strong |
| 5 | 2022-04 → 2022-12 | 9 | Growing pains and talent crisis | At Risk |
| 6 | 2023-01 → 2023-05 | 5 | **Cybersecurity breach (INC-2023-0214)** | **Critical** |
| 7 | 2023-06 → 2023-12 | 7 | Remediation and hardening | At Risk → Stable |
| 8 | 2024-01 → 2024-08 | 8 | Niamey DC1 build-out | Stable |
| 9 | 2024-09 → 2025-02 | 6 | Efficiency drive (Rule of 40) | Strong |
| 10 | 2025-03 → 2025-08 | 6 | Sahel expansion under supply disruption | At Risk |
| 11 | 2025-09 → 2026-02 | 6 | Generative-AI demand surge | Strong |
| 12 | 2026-03 → 2026-06 | 4 | Scaled operations and ESG maturity | Strong |

Health-band distribution across the 78 months: **Stable 43, Strong 18, At Risk 12,
Critical 5.**

---

## 5. One script, going through the real API

**`scripts/seed_data.py` is the only script you run.** `scripts/omniintelos.py` (the KPI
model) and `scripts/omniintelos_corpus.py` (the document estate) are libraries it
imports, not separate entry points.

Every stage that writes data does it through IntelAI's own public API — `POST
/api/v1/ingest/csv`, `/api/v1/ingest/document`, `/api/v1/ingest/audio` — the same
endpoints, auth, validation and audit trail a real user's UI upload hits.

```bash
python scripts/seed_data.py                        # everything
python scripts/seed_data.py --only build           # regenerate KPIs + documents, write nothing remote
python scripts/seed_data.py --only build,seed-kpis # rebuild and reseed KPIs only
python scripts/seed_data.py --purge                # wipe existing global rows first
python scripts/seed_data.py --dry-run              # describe every stage, write nothing
```

| Stage | What it does |
|---|---|
| `build` | Generate the KPI series → `data/omniintelos_kpis/*.csv`, and the document estate → `data/omniintelos/` |
| `seed-kpis` | `POST` each CSV to `/api/v1/ingest/csv` with `global_scope=true` (admin-only) |
| `digests` | Write bilingual EN/FR annual knowledge-base digests of the KPI series |
| `corpus` | `POST` every generated document through `/api/v1/ingest/{document,audio}` |

The only steps that are not API-mediated are the `--purge` cleanups, which delete
existing global rows before a full re-seed. There is no public bulk-delete endpoint, and
adding one would be a genuinely dangerous thing to expose.

**Environment variables** (no hardcoded secrets or URLs): `INTELAI_API_URL`,
`SEED_ADMIN_USERNAME`, `SEED_ADMIN_PASSWORD`, `OMNIINTEL_INTERNAL_TOKEN`.

---

## 6. Measured output

**7,878 KPI rows · 7 domains · 78 months · 101 distinct metrics · 0 rows without provenance.**

| Domain | Rows | Metrics | Periods | Representative KPIs |
|---|---|---|---|---|
| Finance | 1,872 | 24 | 78 | Revenue, COGS, EBITDA, Gross/EBITDA/Net margin, Cash runway, D/E, XOF statutory revenue |
| Growth | 1,248 | 16 | 78 | ARR, MRR, NRR, churn, CAC, LTV, LTV:CAC, CAC payback, Rule of 40 |
| People | 1,092 | 14 | 78 | Headcount, turnover, time to hire, eNPS, revenue/employee, offer acceptance |
| IT | 1,092 | 14 | 78 | Uptime, MTTR, deployment frequency, change failure rate, critical vulns, P99, SLA |
| Operations | 936 | 12 | 78 | OEE, availability, performance, quality, defect rate, FPY, cycle-time efficiency, MTBF |
| ESG | 936 | 12 | 78 | Scope 1/2/3, total tCO2e, energy, renewable %, board diversity, audit score, privacy incidents |
| Logistics | 702 | 9 | 78 | On-time delivery, fulfilment cycle time, inventory turnover, supplier defect rate, carrying cost |

Every row carries `source = "omniintelos:model-v1"` and `segment = "OmniIntelOS"`, so
generated data is separable from anything else by one query:

```sql
SELECT source, COUNT(*) FROM kpi_metrics GROUP BY 1;
```

---

## 7. The document estate

Generated by `scripts/omniintelos_corpus.py`, grounded in the same model — **a figure
quoted in a board pack matches `kpi_metrics` for that period exactly.** That agreement is
what lets the copilot be checked rather than merely believed.

**49 documents · 203 PDF pages · ~1.06 MB**, plus 98 annual KPI digests.

| Format | Count | Contents |
|---|---|---|
| PDF | 24 | Annual reports 2020–2025 (EN) + 2023/2025 (FR); quarterly board packs ×10; incident post-mortem INC-2023-0214; employee handbook (EN+FR); DC1 technical whitepaper; ESG reports 2024–2025 |
| Markdown | 14 | Meeting minutes ×10 (EN/FR, spanning 2020–2026); information-security policy; French data-protection policy; SEV-1 runbook; architecture decision records |
| XLSX | 3 | Full KPI workbook (7 sheets, all 78 months); financial model with assumptions sheet; headcount plan |
| PNG | 6 | ARR, gross margin, uptime, headcount, health index, emissions — each annotated with the INC-2023-0214 marker |
| PPTX | 2 | Board decks (2023 Q1 crisis quarter, 2025 Q4 strong quarter) |
| Digests | 98 | Annual per (domain, year, language), each containing the full month-by-month table |

Annual reports contain a letter from the CEO, key figures, a consolidated statement of
operations, segment reporting by region and service line, computed MD&A per domain, a
domain review, risk factors, notes to the financial statements, governance, outlook, and
a full monthly data appendix.

**Digests are annual, not monthly, on purpose.** 78 months × 7 domains × 2 languages
would be 1,092 near-identical documents; hybrid retrieval would then return six adjacent
months of the same domain for almost any query, crowding out the narrative documents that
let the copilot actually reason. Annual rollups keep every monthly figure retrievable as
text while cutting the corpus to 98 — and exact period lookups are served directly from
`kpi_metrics` by `_retrieve_context()`'s period detection, which does not depend on these
files at all.

---

## 8. What is deliberately NOT here

**Audio files are not generated.** The corpus stage supports audio ingestion, and the
company's meeting recordings would be a natural fit — but no text-to-speech engine is
available in this environment (no espeak, gTTS or pyttsx3). A silent or tone-only WAV
would be a toy file: the audio processor would transcribe nothing from it and the
knowledge base would gain an empty document. Meeting **transcripts** are generated
instead as Markdown minutes, which is what the retrieval layer consumes anyway. If you
want real audio, install a TTS engine and extend `omniintelos_corpus.py`; the ingestion
path already exists and needs no changes.

**No invented qualitative facts.** The generator produces *metrics* computed from real
anchors. It does not invent the wording of a signed contract, a named individual, a
customer's identity, or a specific legal outcome — things a reader could mistake for
verifiable external fact.

**No claim of realness anywhere.** Every generated PDF cover, every digest header and
footer, and the model's own module docstring state that OmniIntelOS is fictional. The
copilot repeats this when asked: prompted "is this a real disclosed figure?", it answers
that the values are internally generated and not audited.

---

## 9. The synthetic scenario generator — a separate feature

`src/data/seed.py` is **application code**, not a seeding script. It is what
`POST /api/v1/admin/scenario` and the `Admin → Scenarios` UI tab call at runtime to switch
between modelled health scenarios for offline demos. It writes directly to Postgres and
labels every row `source = 'seed_*'`, so it is always separable from the OmniIntelOS
dataset above. It is not run by `scripts/seed_data.py`.

---

## 10. Bringing your own data

`POST /api/v1/ingest/csv` takes:

```
period,category,segment,metric_name,value,unit,direction,source
2026-01,Finance,Global,Revenue,2500000,USD,up,my_export
```

Only `metric_name` and `value` are required.

- A per-row `source` column is preserved as that row's provenance; `source_name` labels
  rows that don't carry one.
- **Rows are scoped to the uploader by default**, so one visitor's upload never appears on
  another's dashboard. `global_scope=true` writes the shared baseline with a NULL owner
  and is restricted to admins — this is what `seed_data.py` uses.

IntelAI is data-agnostic: nothing in the application hardcodes OmniIntelOS's domain names,
metric names or periods. Ship it against a completely different dataset and the
dashboards, RBAC scoping and retrieval all work from whatever categories exist in
`kpi_metrics`.

---

## 11. Evaluation set

`tests/rag_eval.jsonl` is generated by `scripts/build_rag_eval_set.py` from whatever is
actually in the database — not written by hand. Each case names a metric that exists for a
period that exists, or a document present in `knowledge_base`; cases that cannot be
verified against live data are dropped rather than shipped. Regenerate it after any
re-seed so the eval tracks the current dataset rather than testing questions the corpus
can no longer answer.
