# IntelAI Data: what is in the database, and where every number came from

This describes the dataset IntelAI actually runs on, how it is rebuilt, and what is
known to be missing. It documents the current implementation, not an intended one.

The short version: **the KPI baseline is real published data, not generated.** Every
row in `kpi_metrics` carries the identifier of the statistical series it came from, so
any figure on a dashboard can be traced to a publisher and re-checked by a third party.

## 1. Why the generated catalog is no longer the baseline

An earlier dataset filled `kpi_metrics` with 10,452 rows of `source='seed_healthy'` —
values produced by `src/data/seed.py`'s model of a plausible company. Alongside it,
413 knowledge-base documents summarised those values in prose that described itself as
"the authoritative, comprehensive record … audited by the internal compliance team",
above figures such as `Gross Margin: 100.0 %`.

Nothing about that is checkable, and the wording asserted an authority the data did not
have. Both were removed. The generator itself is kept — it is genuinely useful for
offline demos and for the scenario switcher — but it is no longer what the database is
seeded with, and its rows are labelled so they can never be mistaken for measurements.
See §6.

## 2. The real KPI layer

`scripts/fetch_real_kpis.py` downloads the sources; `scripts/build_real_kpis.py` turns
them into KPI rows; `scripts/seed_real_kpis_via_api.py` loads them through the public
API. Nothing in that chain generates, interpolates, smooths or extends a value: where a
publisher has no observation for a period, no row is written.

```bash
python scripts/fetch_real_kpis.py          # download to data/<Domain>/
python scripts/build_real_kpis.py          # -> data/real_kpis/<domain>_real.csv
python scripts/seed_real_kpis_via_api.py   # -> POST /api/v1/ingest/csv (global scope)
```

**Measured result: 2,070 rows, 7 domains, 26 distinct sources, 0 rows without provenance.**

| Domain | Rows | Metrics | Sources |
|---|---|---|---|
| ESG | 644 | 5 | World Bank (4 indicators), FRED |
| People | 366 | 9 | FRED (4 series), IBM HR survey |
| IT | 251 | 8 | FRED (2 series), NVD |
| Finance | 242 | 6 | FRED (4 series), Sonatel |
| Growth | 209 | 3 | FRED (3 series) |
| Operations | 180 | 2 | FRED (INDPRO, TCU) |
| Logistics | 178 | 2 | FRED (BUSINV, TSIFRGHTC) |

Provenance strings are `fred:<SERIES_ID>`, `worldbank:<INDICATOR>`, `nvd:cve-2.0`,
`ibm-hr:attrition-survey`, `sonatel:<period>` — each resolves to a public URL, which
the digests in §4 print next to the figures.

### What each source is, and its real limitations

| Source | Used for | Frequency | Honest limitation |
|---|---|---|---|
| FRED (St. Louis Fed) | 18 series across all 7 domains | monthly, some quarterly | US-only macro indicators; they describe an economy, not one company |
| World Bank Open Data | 4 ESG indicators | **annual** | latest year is 2022–2024 depending on indicator; no monthly ESG data exists free |
| NVD 2.0 API | published CVE counts by severity | monthly | a **400-per-window sample**, not the full population — comparable between months because every window is sampled identically, and the metric is named "Published CVEs (sampled)" for that reason |
| IBM HR attrition survey | 5 workforce aggregates | **single period** | a cross-section of individual employees with no date column. It yields point-in-time aggregates under one period; inventing a monthly history from it would be fabrication |
| Sonatel communiqués | 3 published FCFA figures | half-year / 9-month | transcribed from the official release text, in FCFA (XOF) |

Two consequences worth stating plainly rather than hiding behind a filled-in grid:

- **The domains are not equally deep.** Real monthly series are abundant for Finance,
  People, Operations and Logistics, and scarce-to-nonexistent for ESG. ESG gets breadth
  of indicator instead of frequency, because that is the frequency at which the data
  exists.
- **There are no "scenarios" in real data.** The seven health scenarios (§6) are a
  property of the generator. Published statistics do not come with a healthy/declining
  switch, and none was invented for them.

World Bank data is filtered to a relevant set of countries and aggregates (world total,
the FCFA zone matching the Sonatel/Orange material, and the largest emitters) — see
`WORLDBANK_SEGMENTS` in `build_real_kpis.py`. That is a relevance filter on *which*
published rows are loaded; the values themselves are exactly as published.

## 3. The document, image and audio corpus

`scripts/ingest_real_corpus.py` walks `data/<Domain>/` and posts each file to the
endpoint for its type — documents and images to `POST /api/v1/ingest/document`, audio to
`POST /api/v1/ingest/audio`. IntelAI performs **no** extraction itself: documents and
images go to the configured document processor, audio to the audio processor
(STRATEGY.md's standalone rule). The directory name becomes the row's category.

```bash
python scripts/ingest_real_corpus.py --purge     # re-ingest everything
python scripts/ingest_real_corpus.py --only sonatel --dry-run
```

Measured: **15 of 17 files ingested, 434,548 characters.**

| Domain | File | Source | Result |
|---|---|---|---|
| Finance | Salesforce 10-K FY2026 | SEC EDGAR | 53,981 chars |
| Finance | Salesforce 10-Q ×2 | SEC EDGAR | 31,874 + 27,929 chars |
| Finance | Sonatel results (FCFA, French) | sonatel.sn communiqués | 1,341 chars |
| Growth | Salesforce Q1 FY27 earnings release | SEC EDGAR 8-K exhibit | 20,293 chars |
| Growth | Richmond Fed podcast episode (MP3, 5.4MB) | Richmond Fed official RSS | **13,186 chars transcript** via the audio processor |
| People | IBM HR attrition | IBM employee-attrition repo | 128,965 chars (**832 records**) |
| People | HR employee churn | public mirror | 154,025 chars (**4,093 records**) |
| IT | DORA 2024 findings | dora.dev | 1,638 chars |
| Finance/Ops/Logistics/People | 5 FRED chart PNGs | FRED published charts | 211–286 chars each, via OCR |
| ESG | Salesforce FY25 Stakeholder Impact Report | salesforce.com | **32 chars — see below** |

**Corrections to earlier claims in this file.** The IBM dataset is **832 rows, not
1,470**, and the churn dataset is **4,093 rows, not ~14,999** — both downloads are
partial relative to the canonical published datasets. The aggregates in §2 are computed
from what is actually on disk, so they describe the sample held here, not the full
datasets.

**Images are real, and deliberately so.** The six PNGs are FRED's own published charts
of series that are already in `kpi_metrics` — so a vision/OCR result can be checked
against the stored numbers, which a decorative stock image would not allow.

**Raw series are not knowledge-base documents.** `fred_*.csv`, `worldbank_*.json`,
`nvd_*.json` and `.log` files are the *input* to the KPI layer and are skipped by the
corpus ingester. A CSV of 90 numbers retrieves badly and only restates data the KPI
tables already hold exactly; 10,000 lines of Apache access logs chunk into thousands of
near-identical passages that crowd out real answers.

### Known gaps, unresolved

- **Orange S.A. H1-2025 report (890KB, 82pp, French): not ingested.** The document
  processor's origin returns a Cloudflare 502 on this file specifically, on every route,
  while `/health` and smaller files succeed. It extracted 276,265 characters in earlier
  testing, so this is a processor-side regression, not a missing capability.
- **`fred_chart_RSXFS.png`: not ingested.** Consistent 502 from the same processor,
  while the other five charts of near-identical size succeed.
- **Salesforce ESG PDF: 32 characters.** The file is malformed at source. It previously
  yielded 31,729 characters, so the processor could read it before; it cannot now.

These three are external to IntelAI and are recorded here rather than papered over.

## 4. KPI digests — how numbers become retrievable text

The retrieval index searches `knowledge_base`, not `kpi_metrics`, so without a text
representation the assistant cannot answer "what was unemployment in June 2026" even
though the number is in the database. `scripts/build_kpi_digest_docs.py` writes that
text, in **English and French**, for the most recent 18 periods per domain.

Every line is a restatement of a stored value plus the series it came from. There is no
commentary, no target, no explanation of why a number moved, and no claim of audit —
which is precisely how the documents this replaced went wrong.

```bash
python scripts/build_kpi_digest_docs.py --months 18   # -> data/kpi_digests/<Domain>/
python scripts/ingest_real_corpus.py --only _en.md
```

## 5. Glossary

202 rows, 101 terms × EN/FR, seeded from `src/data/glossary.py` +
`src/data/glossary_fr.py` on startup (idempotent — the count is stable across restarts).
French names are only assigned where a genuine standard French term exists, rather than
machine-translating every entry.

A legacy single-language set of 101 rows under `glossary/<domain>/…` was removed: it
duplicated the English entries with slightly different wording, and near-duplicate
passages compete with each other in retrieval.

## 6. The generator, and what it is now for

`src/data/seed.py` still builds a modelled 7-domain catalog with driver metrics, formula-
derived metrics, decayed drift, seven health scenarios with cross-domain cascades, and
three verticals (`saas`, `healthcare`, `esg`). It remains the right tool for an offline
demo, for the Admin scenario switcher, and for testing the pipeline without network
access.

It is **not** what the live database is seeded with, and its output must never be
presented as measurement. Anything it writes is labelled `seed_*` so it is separable
from sourced rows by a single query:

```sql
SELECT source, COUNT(*) FROM kpi_metrics GROUP BY 1;   -- generated vs sourced
```

```bash
python -m src.data.seed healthy healthcare           # DB-direct, generated data
python -m src.data.seed declining_financial saas     # scenario + vertical compose
```

Verticals rescale the same catalog and add the metrics that vertical is judged on
(SaaS: trial conversion, expansion MRR, logo retention; healthcare: bed occupancy,
readmission, HCAHPS; ESG: CSRD readiness, Scope 3 coverage). Measured output, seed=42:
generic 11,376 rows / 146 metrics; saas 11,922 / 153; healthcare 12,156 / 156; esg
11,844 / 152.

## 7. Bringing your own data

`POST /api/v1/ingest/csv` takes:

```
period,category,segment,metric_name,value,unit,direction,source
2026-01,Finance,Global,Revenue,2500000,USD,up,my_export
```

Only `metric_name` and `value` are required. Two behaviours worth knowing:

- **A per-row `source` column is preserved** as that row's provenance; `source_name`
  labels rows that don't carry one. (Previously every row was stamped with the single
  form field, which erased exactly the provenance that makes a figure checkable.)
- **Rows are scoped to the uploader by default**, so one visitor's upload never appears
  on another's dashboard. `global_scope=true` writes the shared baseline with a NULL
  owner and is restricted to admins — this is what the seeding scripts use.

## 8. Evaluation set

`tests/rag_eval.jsonl` is generated by `scripts/build_rag_eval_set.py` from the database,
not written by hand. Each case names a metric that exists for a period that exists, or a
document that is present in `knowledge_base`; cases that cannot be verified are dropped
rather than shipped.

This matters because the previous set asked about gross margin, EBITDA and net profit —
metrics that belonged to the deleted generated data. Against the real corpus those
questions have no answer, so the scores would have measured the mismatch rather than the
system.
