# IntelAI Data: what is in the database, and where every number came from

This describes the dataset IntelAI runs on, how to rebuild it, and what is known to be
missing. It documents the current implementation, not an intended one.

The short version: **the KPI baseline is real published data, not generated.** Every
row in `kpi_metrics` carries the identifier of the statistical series it came from, so
any figure on a dashboard can be traced to a publisher and re-checked by a third party.

## The virtual company

IntelAI's seeded data describes one company: a **West African telecom group,
headquartered in Senegal**, operating bilingually in **French and English** — matching
Sonatel/Orange Group, whose own published result communiqués are the one genuinely
real per-company data source used (Finance domain). Every domain's `segment` field
says exactly what it represents:

| Segment | Meaning |
|---|---|
| `Sonatel Group` | The company's own real, published figures (Finance) |
| `Senegal`, `Africa Western and Central`, `World` | The company's real ESG/environmental footprint (Senegal + its region), plus a global benchmark |
| `External — US Market Context` | Real published US macro statistics (FRED), kept as genuine external planning context — **not** the company's own measured output |
| `Global` | NVD's worldwide published-CVE sample (IT) |
| `IBM Sample` | The IBM HR attrition survey's own cross-section, company-wide (People) |
| `Sales`, `Research & Development`, `Human Resources` | The same IBM HR survey, broken out by its real `Department` column — real per-department headcount/attrition/salary/satisfaction, not invented (People) |
| `External — US Safety Benchmark` | Real BLS/OSHA annual workplace-safety survey rate, external industry context, not this company's own measured incident rate (Operations) |
| `External — SaaS Industry Benchmark` | Real published median SaaS churn rate (Benchmarkit 2025), external context (Growth) |
| `External — Supply Chain Benchmark` | Real published median inventory turnover (Netstock 2025), external context (Logistics) |

**Known limitation, stated rather than papered over:** FRED — the source for most of
Finance/Growth/Operations/Logistics/IT's real monthly series — publishes only US
national statistics; no West African equivalent exists at that frequency or coverage.
Those series are kept as real, genuinely-published macro context (a real multinational
operator's planning does track US/global rates, employment and demand indicators)
rather than removed or relabeled as the company's own — see the `External — US Market
Context` segment above, and the explicit note it triggers in every digest document (§4).

## One script, going through the real API

**`scripts/seed_data.py`** is the only data-seeding script. Every stage that writes
data does it through IntelAI's own public API — `POST /api/v1/ingest/csv`,
`/api/v1/ingest/document`, `/api/v1/ingest/audio` — the same endpoints, auth,
validation and audit trail a real user's UI upload hits. Nothing generates,
interpolates, smooths or extends a value: where a publisher has no observation for a
period, no row is written.

```bash
python scripts/seed_data.py                        # everything, using cached raw data
python scripts/seed_data.py --refetch               # re-download from source first
python scripts/seed_data.py --only build,seed-kpis  # rebuild + reseed KPIs only
python scripts/seed_data.py --purge --only corpus   # wipe + re-ingest the document corpus
python scripts/seed_data.py --dry-run               # describe every stage, write nothing
```

Stages, in order:

1. **`fetch`** — download raw sources to `data/<Domain>/` (skipped if already cached;
   `--refetch` forces a re-download).
2. **`build`** — turn the raw sources into per-domain CSVs in `data/real_kpis/`.
3. **`seed-kpis`** — `POST` each CSV to `/api/v1/ingest/csv` with `global_scope=true`
   (the shared baseline, NULL owner — restricted to admins).
4. **`digests`** — write bilingual EN/FR knowledge-base text of the KPI series. The
   retrieval index searches `knowledge_base`, not `kpi_metrics`, so without this text
   the assistant cannot answer "what was X in period Y" from semantic search alone
   (a separate, direct `kpi_metrics` lookup also covers exact period-in-message
   questions — see `src/services/omnismart_chatbot.py::_retrieve_context`).
5. **`corpus`** — `POST` every real document/image/audio file under `data/<Domain>/`,
   plus the digests just written, through `/api/v1/ingest/{document,audio}`.

Only one step is not API-mediated: `--purge` (corpus stage) directly deletes existing
non-glossary `knowledge_base` rows before a full re-ingest — a deliberate maintenance
operation with no public bulk-delete API equivalent, not part of the seeding path
itself.

**Measured result (current build): 1,596 KPI rows, 7 domains, 8 distinct sources, 0
rows without provenance.**

| Domain | Rows | Metrics | Sources |
|---|---|---|---|
| People | 393 | 12 | FRED (4 series, external context), IBM HR survey (company-wide + 3 real departments) |
| IT | 272 | 9 | FRED (2 series, external context), NVD (CVE counts + a real-CVSS-derived Security Score) |
| Finance | 242 | 6 | FRED (4 series, external context), **Sonatel (real, own)** |
| Growth | 211 | 4 | FRED (3 series, external context), Benchmarkit SaaS churn benchmark |
| Operations | 190 | 4 | FRED (INDPRO, TCU — external context), BLS/OSHA safety benchmark |
| Logistics | 179 | 3 | FRED (BUSINV, TSIFRGHTC — external context), Netstock inventory-turnover benchmark |
| ESG | 109 | 5 | World Bank (Senegal, Africa Western and Central, World), FRED (transport emissions) |

Provenance strings are `fred:<SERIES_ID>`, `worldbank:<INDICATOR>`, `nvd:cve-2.0`,
`ibm-hr:attrition-survey`, `sonatel:<period>`, `bls-osha:osh-annual-survey`,
`benchmarkit:2025-saas-performance-metrics`, `netstock:2025-supply-chain-planning-report`
— each resolves to a public URL, printed next to every figure in the digests (§ digests
stage) and by `_source_url()` in `seed_data.py`.

### What each source is, and its real limitations

| Source | Used for | Frequency | Honest limitation |
|---|---|---|---|
| FRED (St. Louis Fed) | 18 series across Finance/Growth/People/IT/Operations/Logistics | monthly, some quarterly | US-only; external market context, not this company's own numbers (see above) |
| World Bank Open Data | 4 ESG indicators, Senegal + region + world | **annual** | latest year is 2022–2024 depending on indicator; no monthly ESG data exists free |
| NVD 2.0 API | published CVE counts by severity, plus a real-CVSS-derived Security Score | monthly | a **400-per-window sample**, not the full population — comparable between months because every window is sampled identically |
| IBM HR attrition survey | Headcount, attrition, salary, tenure, age, satisfaction, training completion — company-wide and per real department (Sales, R&D, HR) | **single period** | a cross-section with no date column — a monthly history is not derivable from it. Job Satisfaction is the survey's real 1-4 scale, linearly rescaled to 0-100 (documented transform, not a different number) |
| Sonatel communiqués | 3 published FCFA figures | half-year / 9-month | transcribed from the official release text, in FCFA (XOF) — the company's own real numbers |
| BLS/OSHA annual safety survey | Operations' safety incident rate | annual, 2020-2024 | a real national private-industry rate, not this company's own measured incident rate — external benchmark |
| Benchmarkit 2025 SaaS Performance Metrics | Growth's churn rate | annual, 2024-2025 | a real cross-industry median (2,000+ companies), not this company's own measured churn — external benchmark. MRR/ARR/CAC/LTV are deliberately left unfilled: no real external source can honestly stand in for a specific company's own absolute revenue/cost figures the way a rate can |
| Netstock 2025 Supply Chain Planning Report | Logistics' inventory turnover | single point, 2025 | a real global median, not this company's own measured turnover — external benchmark |

**A wider, still-honest gap:** several dashboard fields this app's service layer already
looks for — IT's SLA compliance/MTTR/ticket volume/CPU-memory-utilization/deployment
frequency, Operations' near-misses/safety-training-completion/OEE, Logistics' warehouse
utilization/SKU counts, HR's recruiting funnel/cost-per-hire — have **no real, public,
per-company-specific data source**, because they describe a specific company's private
internal systems (its own ITSM tool, ERP, ticketing system), not something any publisher
reports externally for an arbitrary company. Where no honest real-data mapping exists,
these fields are left at their natural zero/empty state rather than filled with an
invented number.

There are no "scenarios" in this real data. Published statistics do not come with a
healthy/declining switch, and none is invented for them — see §5 for the separate
generator that does model scenarios, deliberately kept out of this pipeline.

## The document, image and audio corpus

The `corpus` stage walks `data/<Domain>/` and posts each file to the endpoint for its
type. IntelAI performs **no** extraction itself: documents and images go to the
configured document processor, audio to the audio processor — each tool in this
project family stays standalone. The directory name becomes the row's category.

Measured: **15 of 17 files ingestible, ~434,548 characters** (real documents; digest
counts are separate, see below).

| Domain | File | Source | Result |
|---|---|---|---|
| Finance | Salesforce 10-K FY2026 | SEC EDGAR | 53,981 chars |
| Finance | Salesforce 10-Q ×2 | SEC EDGAR | 31,874 + 27,929 chars |
| Finance | Sonatel results (FCFA, French) | sonatel.sn communiqués | 1,341 chars |
| Growth | Salesforce Q1 FY27 earnings release | SEC EDGAR 8-K exhibit | 20,293 chars |
| Growth | Richmond Fed podcast episode (MP3) | Richmond Fed official RSS | 13,186 chars transcript, via the audio processor |
| People | IBM HR attrition | IBM employee-attrition repo | 128,965 chars (832 records) |
| People | HR employee churn | public mirror | 154,025 chars (4,093 records) |
| IT | DORA 2024 findings | dora.dev | 1,638 chars |
| Finance/Ops/Logistics/People | FRED chart PNGs | FRED published charts | 211–286 chars each, via OCR |
| ESG | Salesforce FY26 Stakeholder Impact Report | salesforce.com | real, current version |

**Images are real, and deliberately so.** The FRED PNGs are FRED's own published
charts of series already in `kpi_metrics`, so a vision/OCR result can be checked
against the stored numbers.

**Raw series are not knowledge-base documents.** `fred_*.csv`, `worldbank_*.json`,
`nvd_*.json` are the *input* to the KPI layer and are skipped by the corpus stage. A
CSV of 90 numbers retrieves badly and only restates what the KPI tables already hold
exactly.

## Glossary

202 rows, 101 terms × EN/FR, seeded from `src/data/glossary.py` +
`src/data/glossary_fr.py` on startup (idempotent — the count is stable across
restarts). French names are only assigned where a genuine standard French term
exists, matching this company's own bilingual operating reality, rather than
machine-translating every entry.

## The synthetic scenario generator — a different, separate feature

`src/data/seed.py` is **application code**, not a seeding script — it's what
`POST /api/v1/admin/scenario` and the `Admin → Scenarios` UI tab call at runtime to
switch between seven modeled health scenarios (`healthy`, `declining_financial`,
`high_churn_crisis`, ...) and three verticals, for offline demos and pipeline testing
without network access. It writes directly to Postgres (fast, in-process — the same
path the server uses on first boot) and every row it writes is labelled `source =
'seed_*'`, so it is always separable from the real dataset above by one query:

```sql
SELECT source, COUNT(*) FROM kpi_metrics GROUP BY 1;   -- generated vs sourced
```

It is not run by `scripts/seed_data.py` and does not write anything presented as a
real measurement — see the module docstring in `src/data/seed.py` for the scenario
catalog and how to invoke it.

## Bringing your own data

`POST /api/v1/ingest/csv` takes:

```
period,category,segment,metric_name,value,unit,direction,source
2026-01,Finance,Global,Revenue,2500000,USD,up,my_export
```

Only `metric_name` and `value` are required.

- **A per-row `source` column is preserved** as that row's provenance; `source_name`
  labels rows that don't carry one.
- **Rows are scoped to the uploader by default**, so one visitor's upload never
  appears on another's dashboard. `global_scope=true` writes the shared baseline with
  a NULL owner and is restricted to admins — this is what `seed_data.py` uses.

## Evaluation set

`tests/rag_eval.jsonl` is generated by `scripts/build_rag_eval_set.py` from whatever
is actually in the database — not written by hand. Each case names a metric that
exists for a period that exists, or a document that is present in `knowledge_base`;
cases that cannot be verified against the live data are dropped rather than shipped.
Run it after any real re-seed (`python scripts/build_rag_eval_set.py`) so the eval set
tracks the current dataset rather than testing against questions the corpus can no
longer answer.
