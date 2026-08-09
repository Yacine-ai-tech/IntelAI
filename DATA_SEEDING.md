# IntelAI Data Seeding & Multi-Domain Data Model

How IntelAI's demo/seed dataset is built, what it's grounded in, and the two ways to load
it. This describes the actual current implementation (`src/data/seed.py`,
`scripts/seed_via_api.py`) — not an aspirational spec.

## 1. Shape of the catalog

- **78 months** of continuous history, 2020-01 through 2026-06 (`MONTHS = 78` in
  `src/data/seed.py`).
- **7 domains**: Finance, Growth, People, Operations, Logistics, IT, ESG.
- **146 metrics** per period, three layers:
  - **Driver metrics** (`STRATEGIC_KPIS` + `OPERATIONAL_DETAIL`) — independently modeled
    with trend + seasonality + noise. Every `STRATEGIC_KPIS` metric has a sourced,
    benchmarked definition in `src/data/glossary.py`.
  - **Derived metrics** (`DERIVED_KPIS`) — computed FROM driver values via the actual
    documented formula for that metric (e.g. Gross Margin = `(Revenue-COGS)/Revenue`),
    not a second independent random walk that happens to start near a plausible number.
    Some are deliberately cross-domain (Rule of 40 needs Finance's EBITDA margin; Revenue
    per Employee needs both Finance and People) — that's the same synthesis the Overall
    Enterprise Health Index does, applied at the individual-metric level.
- Base values are calibrated to sit inside each metric's documented "healthy" band (see
  §3) so the `healthy` scenario actually reads as healthy against real benchmarks, not
  just a plausible-looking number in isolation.

## 2. Why drift is decayed, and why some metrics are ratios

A metric compounding a constant month-over-month drift for 78 straight months runs away
to unrealistic extremes — no real company grows or shrinks at a fixed rate for 6.5 years
straight. Two mitigations, both in `generate_kpi_rows()`:

- **Decayed drift**: every driver's drift is multiplied by `0.5 ** (i / 30)` — a ~30-month
  half-life, so the trend is strongest in year one and settles into a plateau rather than
  diverging.
- **Ratio-derived costs**: metrics that are naturally a *fraction of another metric*
  (COGS, Operating Costs, CAC, Carrying Cost) are computed as `driver * ratio(month)`
  instead of drifting independently — otherwise two independently-compounding trends (say,
  Revenue growing while COGS shrinks) diverge into an implausible margin over 6.5 years.
  See `_ramp()` and the `DERIVED_KPIS` entries that use it.

## 3. Sources & benchmarks

Base values and healthy/risk thresholds are calibrated against public corporate filings
and industry benchmark reports, not invented numbers:

- **Finance**: SaaS gross-margin and Rule-of-40 norms (Bessemer Cloud Index), general
  corporate financial-health ratios (cash runway, D/E) from standard corporate finance
  benchmarking.
- **Growth**: SaaS NRR/churn/LTV:CAC/CAC-payback benchmarks (Bessemer Cloud Index,
  common SaaS-metrics industry reporting).
- **People**: turnover, time-to-hire, eNPS, revenue-per-employee tech-industry norms
  (SHRM, common HR-analytics benchmarking).
- **Operations**: OEE/FPY/defect-rate Six Sigma / lean-manufacturing world-class
  benchmarks.
- **Logistics**: on-time-delivery, inventory-turnover, carrying-cost supply-chain
  benchmarking norms.
- **IT**: uptime/MTTR/change-failure-rate DORA (DevOps Research and Assessment) metrics,
  standard SLA/vulnerability-management targets.
- **ESG**: renewable-energy ratio, board-diversity, audit-compliance norms drawn from GRI
  (Global Reporting Initiative) — style CSRD/ESG reporting benchmarks.

This grounds *where the numbers should sit*, not a claim that the generated series is
real historical data for a real company — it's a synthetic, seeded, reproducible dataset
calibrated against real-world benchmarks. See `eval/BENCHMARK.md` (if present) for any
actual measured accuracy/eval numbers, which are a separate, honestly-labeled thing from
this seed catalog.

## 4. The 7 health scenarios + cross-domain cascade

`UNHEALTHY_SCENARIOS` in `src/data/seed.py` (plus `healthy`) — selectable via
`Admin → Scenarios` or `POST /api/v1/admin/scenario`:

| Scenario | What it stresses |
|---|---|
| `healthy` | Baseline, occasional minor anomalies |
| `declining_financial` | Revenue/margin collapse, cash crunch, debt spike |
| `high_churn_crisis` | Churn/NRR/LTV:CAC breakdown |
| `operational_meltdown` | OEE/quality/downtime failure |
| `talent_crisis` | Turnover/eNPS/hiring collapse |
| `cybersecurity_breach` | Security incidents, uptime/SLA breach |
| `esg_compliance_failure` | ESG score/compliance/governance failure |

Each scenario starts with anomalies in its primary domain, then adds a short **cross-domain
cascade** — secondary anomalies in *other* domains at later month offsets — modeling the
same chain a real incident follows: an IT/Cybersecurity failure cascades into
Logistics/Operations delays, which cascades into Growth/customer churn, which cascades
into Finance/revenue. Severity multipliers are calibrated to land inside each metric's
documented Risk/Failure Threshold band, not arbitrary numbers — see the comments next to
each entry in `UNHEALTHY_SCENARIOS`.

## 5. Two ways to load it — which one to use

| | `src/data/seed.py` (`seed_database()`) | `scripts/seed_via_api.py` |
|---|---|---|
| Path | Direct write to Postgres via `pg_store` | `POST /api/v1/ingest/csv` per domain, through the real API |
| Speed | Instant | Real HTTP round-trips, auth, CSV parsing |
| Used by | Server first-boot, `POST /api/v1/admin/seed`/`/admin/scenario` (needs to be instant) | Standalone script, run manually |
| What it exercises | Nothing but the DB write path | The actual self-hoster-facing upload flow: auth, CSV schema, RBAC, the `metric_name`→`metric` column mapping |
| Good for | Local dev bootstrap, instant scenario switching in the Admin UI | Demoing/testing the real ingestion pipeline end-to-end; feeding IntelAI *your own* CSVs instead of the generated catalog (`--path`) |

Both consume the exact same `generate_kpi_rows()` catalog — one source of truth for the
dataset; the only difference is the delivery mechanism.

```bash
# Fast, direct (what the server does on first boot):
python -m src.data.seed declining_financial

# Through the real API (what a self-hoster demoing the upload pipeline would run):
python scripts/seed_via_api.py declining_financial

# Ingest your own data instead of the generated catalog:
python scripts/seed_via_api.py --path /path/to/your/csvs/
```

## 6. Bringing your own data

`scripts/seed_via_api.py --path <file-or-dir>` ingests real CSVs instead of the generated
catalog — point it at your own exports. Expected columns (matches
`POST /api/v1/ingest/csv`'s contract, documented in `server.py`):

```
period,category,segment,metric_name,value,unit,direction,source
2026-01,Finance,Global,Revenue,2500000,USD,up,my_export
```

Only `metric_name` and `value` are required; the rest default sensibly (see
`store_kpi_metrics()` in `src/services/pg_store.py`).
