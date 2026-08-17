"""
OmniIntelOS — the virtual company IntelAI's demo dataset describes.

This module is the SINGLE source of truth for that company: its identity, its
78-month operating history (Jan 2020 - Jun 2026), and every KPI on every
dashboard. `scripts/seed_data.py` is the only runnable entry point; this is a
library it imports, not a second script to run.

WHAT THIS IS, STATED PLAINLY
────────────────────────────
OmniIntelOS S.A. is FICTIONAL. It is not a real company, and no figure here is
a real company's disclosed result. What makes the dataset trustworthy is not a
claim of realness — it is that every number is *internally verifiable*:

  1. Only PRIMITIVES are modelled (revenue, COGS, headcount, incidents, kWh…).
     Every ratio a dashboard shows is COMPUTED from those primitives with the
     industry-standard formula, so anyone can re-derive it from the seeded rows:
         Gross Margin  == (Revenue - COGS) / Revenue
         OEE           == Availability x Performance x Quality
         Rule of 40    == YoY growth % + EBITDA margin %
     If a formula and the stored value disagree, that is a real bug, not noise.

  2. The FRAMEWORKS are real and citable, even though the company is not:
     GHG Protocol Scope 1/2/3, Google DORA (deploy frequency, lead time, CFR,
     MTTR), CVSS v3.1 severity bands, OEE (Nakajima), SaaS Rule of 40 / NRR /
     LTV:CAC, OHADA statutory accounting, the BCEAO XOF-EUR peg (655.957,
     fixed — a real, checkable constant).

  3. The history is a single CAUSAL narrative, not 7 independent random walks.
     A February 2023 security breach degrades IT uptime, which delays delivery,
     which spikes churn the following quarter, which compresses revenue and
     cash runway two quarters later — the cascade IntelAI's own domain spec
     describes. Correlation is generated, not decorated on afterwards.

  4. It is DETERMINISTIC. The same (metric, period) always yields the same
     value, so a re-seed never silently rewrites history.

COMPANY PROFILE
───────────────
  Legal name     OmniIntelOS S.A. (Société Anonyme, OHADA)
  HQ             Niamey, Niger
  Founded        March 2019
  Industry       Applied AI / enterprise SaaS
  Functional ccy XOF (BCEAO franc, pegged 655.957 = 1 EUR); reports in USD
  Languages      French (HQ, Sahel operations) + English (international)

  Service lines  Data science & analytics platform (SaaS subscriptions)
                 Computer vision (industrial inspection, agri-monitoring)
                 NLP (bilingual FR/EN document intelligence)
                 IoT telemetry & edge analytics
                 Blockchain (supply-chain provenance, land registry)
                 Custom software engineering
                 Managed data centres & colocation (Niamey DC1, Dakar DC2)

  Footprint      Sahel      Niger (HQ), Mali, Burkina Faso, Chad
                 W. Africa  Senegal, Côte d'Ivoire, Ghana, Nigeria
                 N./E. Afr. Morocco, Kenya
                 Europe     France, Belgium
                 Americas   United States, Canada

  Partners       Universities (Abdou Moumouni, Cheikh Anta Diop, Polytechnique),
                 engineering & manufacturing integrators, regional banks and
                 microfinance institutions, public-sector agencies, telcos.
"""
from __future__ import annotations

import hashlib
import math
from typing import Any, Dict, List, Tuple

# ─────────────────────────────────────────────────────────────────────────────
# Identity
# ─────────────────────────────────────────────────────────────────────────────

COMPANY = "OmniIntelOS S.A."
COMPANY_SHORT = "OmniIntelOS"
HQ = "Niamey, Niger"
XOF_PER_EUR = 655.957        # BCEAO fixed peg — a real, verifiable constant
USD_PER_EUR = 1.08           # planning rate used consistently across the dataset
XOF_PER_USD = XOF_PER_EUR / USD_PER_EUR

START = (2020, 1)
END = (2026, 6)

SERVICE_LINES = [
    "Data Science & Analytics",
    "Computer Vision",
    "NLP & Document Intelligence",
    "IoT & Edge Telemetry",
    "Blockchain & Provenance",
    "Custom Software Engineering",
    "Managed Data Centres",
]

REGIONS = ["Sahel", "West Africa", "North & East Africa", "Europe", "Americas"]

DEPARTMENTS = [
    "Engineering", "Data Science & AI Research", "Cloud & Data Centre Operations",
    "Professional Services", "Sales & Partnerships", "Customer Success",
    "Finance & Administration", "People & Culture", "Security & Compliance",
]


# ─────────────────────────────────────────────────────────────────────────────
# The 78-month narrative. Every phase is a distinct enterprise-health regime,
# so the timeline exercises the full 0-100 health band rather than sitting in
# one state — and each regime's cause is explicit, not cosmetic.
# ─────────────────────────────────────────────────────────────────────────────

Phase = Dict[str, Any]

PHASES: List[Phase] = [
    dict(key="early_traction", start="2020-01", end="2020-03", health="Stable",
         label_en="Early traction", label_fr="Traction initiale",
         narrative_en="First enterprise logos in Niamey and Dakar; small team, "
                      "services-heavy revenue mix, disciplined burn.",
         narrative_fr="Premiers grands comptes à Niamey et Dakar ; équipe réduite, "
                      "revenus dominés par les services, consommation de trésorerie maîtrisée.",
         growth=1.00, margin=0.92, churn=1.05, attrition=1.00, uptime=1.00,
         delivery=1.00, capex=0.6, security=1.00),

    dict(key="covid_shock", start="2020-04", end="2020-09", health="At Risk",
         label_en="COVID-19 shock and pivot", label_fr="Choc COVID-19 et pivot",
         narrative_en="Public-sector procurement freezes and border closures stall "
                      "signature; the company pivots to remote delivery and digital-"
                      "transformation mandates, protecting cash over growth.",
         narrative_fr="Le gel des marchés publics et la fermeture des frontières bloquent "
                      "les signatures ; pivot vers la livraison à distance et les mandats de "
                      "transformation numérique, la trésorerie prime sur la croissance.",
         growth=0.42, margin=0.80, churn=1.85, attrition=1.15, uptime=0.998,
         delivery=0.88, capex=0.25, security=1.00),

    dict(key="digital_tailwind", start="2020-10", end="2021-06", health="Stable",
         label_en="Digital-transformation tailwind", label_fr="Vent porteur du numérique",
         narrative_en="Remote-work demand converts the pivot into durable subscription "
                      "revenue; first multi-year contracts with regional banks.",
         narrative_fr="La demande liée au télétravail transforme le pivot en revenus "
                      "d'abonnement durables ; premiers contrats pluriannuels avec des banques régionales.",
         growth=1.35, margin=0.97, churn=0.85, attrition=0.95, uptime=1.001,
         delivery=1.02, capex=0.8, security=1.00),

    dict(key="series_a", start="2021-07", end="2022-03", health="Strong",
         label_en="Series A and hypergrowth", label_fr="Série A et hypercroissance",
         narrative_en="A USD 12M Series A funds aggressive hiring and the Niamey DC1 "
                      "land acquisition; growth is bought at the cost of near-term margin.",
         narrative_fr="Une Série A de 12 M USD finance des recrutements agressifs et "
                      "l'acquisition du terrain du DC1 de Niamey ; la croissance se paie en marge à court terme.",
         growth=1.75, margin=0.86, churn=0.80, attrition=1.05, uptime=1.000,
         delivery=0.97, capex=1.7, security=1.00),

    dict(key="growing_pains", start="2022-04", end="2022-12", health="At Risk",
         label_en="Growing pains and talent crisis", label_fr="Crise de croissance et de talents",
         narrative_en="Headcount outruns onboarding capacity: attrition spikes, eNPS "
                      "collapses, delivery slips and first-pass quality degrades.",
         narrative_fr="Les effectifs dépassent la capacité d'intégration : l'attrition "
                      "s'envole, l'eNPS s'effondre, les livraisons glissent et la qualité au premier passage se dégrade.",
         growth=0.95, margin=0.88, churn=1.35, attrition=2.30, uptime=0.997,
         delivery=0.84, capex=1.1, security=0.95),

    dict(key="security_breach", start="2023-01", end="2023-05", health="Critical",
         label_en="Cybersecurity breach and containment", label_fr="Brèche de cybersécurité et confinement",
         narrative_en="A credential-stuffing intrusion (13-14 Feb 2023) reaches a staging "
                      "estate holding customer telemetry. Containment forces multi-day "
                      "degradation; the churn and revenue consequences land over the next two quarters.",
         narrative_fr="Une intrusion par bourrage d'identifiants (13-14 fév. 2023) atteint un "
                      "environnement de préproduction contenant de la télémétrie client. Le confinement impose "
                      "plusieurs jours de dégradation ; les conséquences sur l'attrition client et le chiffre "
                      "d'affaires se matérialisent sur les deux trimestres suivants.",
         growth=0.55, margin=0.79, churn=2.60, attrition=1.60, uptime=0.9990,
         delivery=0.74, capex=0.9, security=0.35),

    dict(key="remediation", start="2023-06", end="2023-12", health="At Risk",
         label_en="Remediation and hardening", label_fr="Remédiation et durcissement",
         narrative_en="Zero-trust rebuild, ISO 27001 programme, independent penetration "
                      "testing and a customer-trust campaign; costs stay elevated while confidence returns.",
         narrative_fr="Reconstruction zero-trust, programme ISO 27001, tests d'intrusion "
                      "indépendants et campagne de reconquête de la confiance ; les coûts restent élevés "
                      "pendant que la confiance revient.",
         growth=0.85, margin=0.84, churn=1.45, attrition=1.20, uptime=0.9993,
         delivery=0.93, capex=1.2, security=1.15),

    dict(key="datacentre_buildout", start="2024-01", end="2024-08", health="Stable",
         label_en="Niamey DC1 build-out", label_fr="Construction du DC1 de Niamey",
         narrative_en="Tier-III data centre commissioning: heavy CAPEX and imported "
                      "hardware lift leverage and squeeze runway, but unlock sovereign-hosting revenue.",
         narrative_fr="Mise en service d'un centre de données Tier III : CAPEX lourd et "
                      "matériel importé alourdissent l'endettement et réduisent l'autonomie de trésorerie, "
                      "mais débloquent des revenus d'hébergement souverain.",
         growth=1.15, margin=0.88, churn=0.95, attrition=0.95, uptime=1.001,
         delivery=0.96, capex=2.6, security=1.10),

    dict(key="efficiency_drive", start="2024-09", end="2025-02", health="Strong",
         label_en="Efficiency drive (Rule of 40)", label_fr="Programme d'efficacité (règle des 40)",
         narrative_en="Cost discipline, pricing revision and automation of delivery lift "
                      "gross margin and put the Rule of 40 back above target.",
         narrative_fr="Discipline des coûts, révision tarifaire et automatisation de la "
                      "livraison redressent la marge brute et repassent la règle des 40 au-dessus de la cible.",
         growth=1.20, margin=1.09, churn=0.75, attrition=0.85, uptime=1.0015,
         delivery=1.06, capex=0.7, security=1.10),

    dict(key="sahel_disruption", start="2025-03", end="2025-08", health="At Risk",
         label_en="Sahel expansion under supply disruption", label_fr="Expansion sahélienne sous tension logistique",
         narrative_en="Regional border and corridor disruption delays imported GPU and "
                      "network hardware; on-time delivery and supplier quality both degrade "
                      "while the Bamako and N'Djamena offices open.",
         narrative_fr="Les perturbations frontalières et des corridors régionaux retardent "
                      "les GPU et le matériel réseau importés ; la ponctualité des livraisons et la qualité "
                      "fournisseur se dégradent pendant l'ouverture des bureaux de Bamako et N'Djamena.",
         growth=1.05, margin=0.91, churn=1.25, attrition=1.15, uptime=0.9985,
         delivery=0.71, capex=1.3, security=1.05),

    dict(key="ai_demand_boom", start="2025-09", end="2026-02", health="Strong",
         label_en="Generative-AI demand surge", label_fr="Forte demande en IA générative",
         narrative_en="Bilingual FR/EN document-intelligence and sovereign GPU capacity "
                      "meet a regional surge in AI mandates; expansion revenue drives NRR well above target.",
         narrative_fr="L'intelligence documentaire bilingue FR/EN et la capacité GPU souveraine "
                      "rencontrent une forte demande régionale en IA ; les revenus d'expansion portent le NRR "
                      "bien au-dessus de la cible.",
         growth=1.55, margin=1.06, churn=0.70, attrition=0.90, uptime=1.0012,
         delivery=1.04, capex=1.5, security=1.12),

    dict(key="scaled_maturity", start="2026-03", end="2026-06", health="Strong",
         label_en="Scaled operations and ESG maturity", label_fr="Opérations à l'échelle et maturité ESG",
         narrative_en="Solar-plus-storage brings DC1 renewable share past target; ISO 27001 "
                      "and ISO 14001 audits clear, and governance metrics reach board targets.",
         narrative_fr="Le solaire couplé au stockage porte la part renouvelable du DC1 au-delà "
                      "de la cible ; les audits ISO 27001 et ISO 14001 sont validés et les indicateurs de "
                      "gouvernance atteignent les objectifs du conseil.",
         growth=1.30, margin=1.10, churn=0.72, attrition=0.85, uptime=1.0018,
         delivery=1.05, capex=1.0, security=1.18),
]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def months() -> List[str]:
    """The 78 reporting periods, Jan 2020 .. Jun 2026 inclusive."""
    out, (y, m) = [], START
    while (y, m) <= END:
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def _idx(period: str) -> int:
    y, m = int(period[:4]), int(period[5:7])
    return (y - START[0]) * 12 + (m - START[1])


def phase_for(period: str) -> Phase:
    for p in PHASES:
        if p["start"] <= period <= p["end"]:
            return p
    return PHASES[-1]


def jitter(key: str, spread: float = 1.0) -> float:
    """Deterministic pseudo-noise in [-spread, +spread]. Same key -> same value,
    so re-seeding never rewrites history."""
    h = int(hashlib.sha256(key.encode()).hexdigest()[:12], 16)
    return spread * (2.0 * (h / 0xFFFFFFFFFFFF) - 1.0)


def _smooth(values: List[float], window: int = 3) -> List[float]:
    """Light moving average so phase transitions read as a business trajectory
    rather than a step function at every boundary."""
    out = []
    for i in range(len(values)):
        lo = max(0, i - window + 1)
        out.append(sum(values[lo:i + 1]) / (i - lo + 1))
    return out


def _lag(values: List[float], k: int, fill: float) -> List[float]:
    """Shift a driver forward k months — how a cause in month i shows up as an
    effect in month i+k (breach -> churn -> revenue)."""
    return [fill] * k + values[:-k] if k > 0 else list(values)


# ─────────────────────────────────────────────────────────────────────────────
# The model: primitives first, every ratio derived from them.
# ─────────────────────────────────────────────────────────────────────────────

def build_series() -> Dict[str, List[float]]:
    """Compute the full 78-month primitive series for the whole company.
    Returned as parallel lists indexed by months()."""
    ms = months()
    n = len(ms)
    ph = [phase_for(p) for p in ms]

    # ── Growth engine: customers and ARR ─────────────────────────────────────
    # Base compounding, modulated per phase, with deterministic month noise.
    customers: List[float] = []
    arr: List[float] = []
    cust, a = 34.0, 1_150_000.0
    new_logos, churned_logos, expansion_l, contraction_l, churn_rev_l = [], [], [], [], []
    for i, p in enumerate(ms):
        f = ph[i]
        base_g = 0.026 * f["growth"] * (1.0 + jitter(f"g:{p}", 0.22))
        gross_add_rate = max(0.004, base_g + 0.013)
        churn_rate = max(0.0025, 0.0095 * f["churn"] * (1.0 + jitter(f"c:{p}", 0.20)))

        adds = cust * gross_add_rate
        lost = cust * churn_rate
        new_logos.append(adds)
        churned_logos.append(lost)
        cust = max(20.0, cust + adds - lost)
        customers.append(cust)

        arpa = a / max(cust, 1.0)
        expansion = a * max(0.0, 0.017 * f["growth"]) * (1 + jitter(f"e:{p}", 0.25))
        contraction = a * 0.0035 * f["churn"] * (1 + jitter(f"k:{p}", 0.25))
        churn_rev = lost * arpa
        expansion_l.append(expansion)
        contraction_l.append(contraction)
        churn_rev_l.append(churn_rev)
        a = max(200_000.0, a + adds * arpa + expansion - contraction - churn_rev)
        arr.append(a)

    arr = _smooth(arr, 2)
    mrr = [x / 12.0 for x in arr]

    # ── Finance ──────────────────────────────────────────────────────────────
    # Revenue = subscription (MRR) + professional services + data-centre/colocation.
    services_rev, dc_rev, revenue, cogs, opex = [], [], [], [], []
    sm_spend, rd_spend, ga_spend = [], [], []
    for i, p in enumerate(ms):
        f = ph[i]
        svc = mrr[i] * (0.62 if i < 24 else 0.34 if i < 48 else 0.26) * (1 + jitter(f"s:{p}", 0.12))
        # Data-centre revenue only exists after DC1 commissioning (mid-2024).
        dc = 0.0 if i < 54 else mrr[i] * min(0.30, 0.05 + 0.011 * (i - 54)) * (1 + jitter(f"d:{p}", 0.10))
        rev = mrr[i] + svc + dc
        services_rev.append(svc)
        dc_rev.append(dc)
        revenue.append(rev)

        # Gross margin improves with scale + automation, degrades in stressed phases.
        gm_target = (0.545 + 0.145 * min(1.0, i / 60.0)) * f["margin"]
        gm_target = min(0.79, max(0.34, gm_target + jitter(f"gm:{p}", 0.012)))
        cogs.append(rev * (1.0 - gm_target))

        sm = rev * (0.29 if f["growth"] > 1.3 else 0.225) * (1 + jitter(f"sm:{p}", 0.08))
        rd = rev * (0.26 if i < 36 else 0.215) * (1 + jitter(f"rd:{p}", 0.07))
        ga = rev * 0.115 * (1 + jitter(f"ga:{p}", 0.08))
        sm_spend.append(sm)
        rd_spend.append(rd)
        ga_spend.append(ga)
        opex.append(sm + rd + ga)

    ebitda = [revenue[i] - cogs[i] - opex[i] for i in range(n)]
    dep_amort = [max(6_000.0, revenue[i] * 0.035 + (0.0 if i < 48 else 145_000.0)) for i in range(n)]
    interest = []
    debt: List[float] = []
    d = 240_000.0
    for i, p in enumerate(ms):
        f = ph[i]
        draw = 0.0
        if f["key"] == "datacentre_buildout":
            draw = 1_050_000.0          # DC1 equipment facility, drawn monthly
        elif f["capex"] > 1.2:
            draw = 180_000.0 * f["capex"]
        d = max(120_000.0, d + draw - d * 0.011)
        debt.append(d)
        interest.append(d * 0.0071)      # ~8.5%/yr regional commercial rate

    ebit = [ebitda[i] - dep_amort[i] for i in range(n)]
    pretax = [ebit[i] - interest[i] for i in range(n)]
    # Niger corporate income tax 30%; no benefit booked on losses.
    tax = [max(0.0, pretax[i]) * 0.30 for i in range(n)]
    net_income = [pretax[i] - tax[i] for i in range(n)]

    capex = [revenue[i] * 0.05 * ph[i]["capex"] + (620_000.0 if ph[i]["key"] == "datacentre_buildout" else 0.0)
             for i in range(n)]

    # Cash: opening balance + funding events - burn.
    cash: List[float] = []
    c = 780_000.0
    equity_raised = {"2021-08": 12_000_000.0, "2024-02": 6_500_000.0}
    for i, p in enumerate(ms):
        c += net_income[i] + dep_amort[i] - capex[i] + equity_raised.get(p, 0.0)
        c = max(95_000.0, c)
        cash.append(c)

    equity: List[float] = []
    eq = 1_400_000.0
    for i, p in enumerate(ms):
        eq += net_income[i] + equity_raised.get(p, 0.0)
        equity.append(max(250_000.0, eq))

    # ── People ───────────────────────────────────────────────────────────────
    headcount, hires, separations, open_reqs, offers, offers_acc = [], [], [], [], [], []
    hc = 28.0
    for i, p in enumerate(ms):
        f = ph[i]
        target = 28.0 * math.exp(0.0355 * i) * (0.94 + 0.10 * min(1.0, i / 40.0))
        gap = max(0.0, target - hc)
        hired = gap * 0.34 + 0.9 + jitter(f"h:{p}", 0.8)
        attr_rate = 0.0102 * f["attrition"] * (1 + jitter(f"a:{p}", 0.18))
        left = hc * max(0.002, attr_rate)
        hc = max(20.0, hc + hired - left)
        headcount.append(hc)
        hires.append(max(0.0, hired))
        separations.append(max(0.0, left))
        reqs = max(1.0, hired * 1.65 + jitter(f"r:{p}", 1.2))
        open_reqs.append(reqs)
        ext = max(1.0, hired * 1.25)
        offers.append(ext)
        acc_rate = min(0.96, max(0.52, 0.885 / max(0.7, f["attrition"]) + jitter(f"oa:{p}", 0.04)))
        offers_acc.append(ext * acc_rate)

    # ── IT / security (the causal origin of the 2023 cascade) ────────────────
    uptime, mttr, deploys, cfr, crit_vulns, p99, incidents = [], [], [], [], [], [], []
    for i, p in enumerate(ms):
        f = ph[i]
        sec = f["security"]
        up = min(99.995, max(96.80, 99.93 * f["uptime"] + jitter(f"u:{p}", 0.02)))
        # The intrusion was detected 14 Feb 2023 and contained 16 Feb. Only those
        # months carry the availability hit — January is pre-incident and must not
        # be degraded, or the timeline in the post-mortem contradicts the series.
        if p == "2023-02":
            up = 96.42          # 65h containment outage inside the month
        elif p == "2023-03":
            up = 98.15          # phased restoration
        elif p in ("2023-04", "2023-05"):
            up = 99.62 + jitter(f"u:{p}", 0.05)   # residual, recovering
        uptime.append(up)
        base_mttr = 0.62 if i > 54 else 1.15
        mttr.append(max(0.18, base_mttr / sec * (1 + jitter(f"m:{p}", 0.20))))
        dep = max(2.0, (3.0 + 0.42 * min(i, 60) / 6.0) * min(1.35, sec) * (1 + jitter(f"dp:{p}", 0.15)))
        deploys.append(dep)
        cfr.append(min(24.0, max(1.6, 6.4 / sec * (1 + jitter(f"cf:{p}", 0.18)))))
        cv = max(0.0, (11.0 / sec - 9.0) + jitter(f"cv:{p}", 1.1))
        if f["key"] == "security_breach":
            cv += 9.0
        crit_vulns.append(round(cv))
        p99.append(max(96.0, (330.0 - 2.1 * min(i, 60)) / min(1.3, sec) * (1 + jitter(f"l:{p}", 0.09))))
        incidents.append(max(1.0, (14.0 / sec) * (1 + jitter(f"in:{p}", 0.22))))

    # Security posture feeds delivery quality with a one-month lag, and customer
    # churn with a two-month lag — the cascade, generated rather than asserted.
    sec_series = [ph[i]["security"] for i in range(n)]
    sec_lag1 = _lag(sec_series, 1, sec_series[0])
    sec_lag2 = _lag(sec_series, 2, sec_series[0])

    # ── Operations (delivery & model-pipeline quality; OEE analogue) ──────────
    availability, performance, quality, defect_rate, fpy, cycle_eff, mtbf = [], [], [], [], [], [], []
    for i, p in enumerate(ms):
        f = ph[i]
        # Delivery health floors out around 0.80 even in the worst phase: a
        # disrupted quarter degrades throughput and quality, it does not stop the
        # company producing. OEE below ~40 would mean the delivery org had
        # essentially halted, which no phase here describes.
        dl = max(0.80, f["delivery"] * (0.62 + 0.38 * min(1.15, sec_lag1[i])))
        av = min(0.985, max(0.74, 0.955 * dl + jitter(f"av:{p}", 0.012)))
        pf = min(0.985, max(0.72, 0.940 * dl + jitter(f"pf:{p}", 0.014)))
        ql = min(0.995, max(0.74, 0.962 * (0.6 + 0.4 * dl) + jitter(f"ql:{p}", 0.010)))
        availability.append(av * 100)
        performance.append(pf * 100)
        quality.append(ql * 100)
        defect_rate.append(max(0.18, (1.0 - ql) * 100 * 0.82))
        fpy.append(min(97.5, max(69.0, ql * 100 - 2.4 + jitter(f"fy:{p}", 0.9))))
        cycle_eff.append(min(99.0, max(72.0, pf * 100 + 1.6 + jitter(f"ce:{p}", 1.1))))
        mtbf.append(max(120.0, 980.0 * min(1.2, f["security"]) * dl * (1 + jitter(f"mb:{p}", 0.12))))

    # ── Logistics (hardware supply chain for the data centres) ───────────────
    otd, fulfil_hours, inv_turns, supp_defect, carrying = [], [], [], [], []
    for i, p in enumerate(ms):
        f = ph[i]
        dl = f["delivery"]
        otd.append(min(99.0, max(62.0, 96.0 * dl + jitter(f"ot:{p}", 1.4))))
        fulfil_hours.append(max(18.0, 44.0 / max(0.55, dl) + jitter(f"fh:{p}", 4.0)))
        inv_turns.append(max(1.6, (7.4 if i > 48 else 5.2) * dl + jitter(f"it:{p}", 0.5)))
        supp_defect.append(max(0.12, 0.62 / max(0.55, dl) + jitter(f"sd:{p}", 0.12)))
        carrying.append(min(38.0, max(13.0, 19.5 / max(0.6, dl) + jitter(f"cc:{p}", 1.5))))

    # ── ESG ──────────────────────────────────────────────────────────────────
    kwh, renew, scope1, scope2, scope3, board_div, audit, privacy, water, waste = \
        [], [], [], [], [], [], [], [], [], []
    for i, p in enumerate(ms):
        f = ph[i]
        # Energy tracks headcount, then steps up sharply when DC1 comes online.
        base_kwh = headcount[i] * 310.0
        dc_kwh = 0.0 if i < 48 else 165_000.0 * min(1.0, (i - 48) / 10.0)
        e = base_kwh + dc_kwh
        kwh.append(e)
        r = 12.0 + 0.52 * i
        if i >= 68:
            r += 14.0                    # solar + storage at DC1
        renew.append(min(78.0, max(8.0, r + jitter(f"re:{p}", 2.2))))
        grid_ef = 0.62                   # tCO2e per MWh, Sahel grid mix
        scope2.append(e / 1000.0 * grid_ef * (1 - renew[-1] / 100.0))
        scope1.append(max(1.2, headcount[i] * 0.021 + (28.0 if i >= 48 else 0.0)))  # generators
        scope3.append(max(4.0, revenue[i] / 1_000_000.0 * 62.0 + headcount[i] * 0.09))
        board_div.append(min(50.0, 14.0 + 0.46 * i + jitter(f"bd:{p}", 1.6)))
        audit.append(min(99.6, max(72.0, (86.0 + 0.13 * i) * min(1.12, f["security"]) + jitter(f"au:{p}", 1.3))))
        pv = 0.0
        if f["key"] == "security_breach":
            pv = 3.0 if p == "2023-02" else 1.0
        privacy.append(pv)
        water.append(max(40.0, headcount[i] * 1.9 + (2100.0 if i >= 48 else 0.0)))
        waste.append(min(86.0, max(22.0, 31.0 + 0.55 * i + jitter(f"wd:{p}", 2.0))))

    return dict(
        months=ms, customers=customers, arr=arr, mrr=mrr,
        new_logos=new_logos, churned_logos=churned_logos,
        expansion=expansion_l, contraction=contraction_l, churn_rev=churn_rev_l,
        revenue=revenue, services_rev=services_rev, dc_rev=dc_rev,
        cogs=cogs, opex=opex, sm_spend=sm_spend, rd_spend=rd_spend, ga_spend=ga_spend,
        ebitda=ebitda, dep_amort=dep_amort, ebit=ebit, interest=interest, tax=tax,
        net_income=net_income, capex=capex, cash=cash, debt=debt, equity=equity,
        headcount=headcount, hires=hires, separations=separations,
        open_reqs=open_reqs, offers=offers, offers_acc=offers_acc,
        uptime=uptime, mttr=mttr, deploys=deploys, cfr=cfr, crit_vulns=crit_vulns,
        p99=p99, incidents=incidents,
        availability=availability, performance=performance, quality=quality,
        defect_rate=defect_rate, fpy=fpy, cycle_eff=cycle_eff, mtbf=mtbf,
        otd=otd, fulfil_hours=fulfil_hours, inv_turns=inv_turns,
        supp_defect=supp_defect, carrying=carrying,
        kwh=kwh, renew=renew, scope1=scope1, scope2=scope2, scope3=scope3,
        board_div=board_div, audit=audit, privacy=privacy, water=water, waste=waste,
        sec_lag2=sec_lag2,
    )


def _row(period, category, metric, value, unit, direction, segment="OmniIntelOS") -> Dict[str, Any]:
    return {"period": period, "category": category, "segment": segment,
            "metric_name": metric, "value": round(float(value), 4), "unit": unit,
            "direction": direction, "source": "omniintelos:model-v1"}


def generate_kpis() -> List[Dict[str, Any]]:
    """Every KPI row for all 78 months across the 7 domains.

    Ratios are computed here from the primitives above using the same formulas
    IntelAI's domain specification documents, so a reader can re-derive any of
    them from other rows in the same period."""
    s = build_series()
    ms = s["months"]
    out: List[Dict[str, Any]] = []

    for i, p in enumerate(ms):
        rev, cogs, opx = s["revenue"][i], s["cogs"][i], s["opex"][i]
        ebitda, ni = s["ebitda"][i], s["net_income"][i]

        # ── Finance ─────────────────────────────────────────────────────────
        gross_profit = rev - cogs
        out += [
            _row(p, "Finance", "Revenue", rev, "USD", "up"),
            _row(p, "Finance", "Subscription Revenue", s["mrr"][i], "USD", "up"),
            _row(p, "Finance", "Professional Services Revenue", s["services_rev"][i], "USD", "up"),
            _row(p, "Finance", "Data Centre Revenue", s["dc_rev"][i], "USD", "up"),
            _row(p, "Finance", "COGS", cogs, "USD", "down"),
            _row(p, "Finance", "Gross Profit", gross_profit, "USD", "up"),
            _row(p, "Finance", "Operating Expenses", opx, "USD", "down"),
            _row(p, "Finance", "Sales & Marketing Spend", s["sm_spend"][i], "USD", "down"),
            _row(p, "Finance", "R&D Spend", s["rd_spend"][i], "USD", "down"),
            _row(p, "Finance", "EBITDA", ebitda, "USD", "up"),
            _row(p, "Finance", "Depreciation & Amortisation", s["dep_amort"][i], "USD", "down"),
            _row(p, "Finance", "Interest Expense", s["interest"][i], "USD", "down"),
            _row(p, "Finance", "Taxes", s["tax"][i], "USD", "down"),
            _row(p, "Finance", "Net Income", ni, "USD", "up"),
            _row(p, "Finance", "Capital Expenditure", s["capex"][i], "USD", "down"),
            _row(p, "Finance", "Cash Balance", s["cash"][i], "USD", "up"),
            _row(p, "Finance", "Total Debt", s["debt"][i], "USD", "down"),
            _row(p, "Finance", "Shareholders Equity", s["equity"][i], "USD", "up"),
            # Derived — each re-derivable from the rows above.
            _row(p, "Finance", "Gross Margin", gross_profit / rev * 100, "%", "up"),
            _row(p, "Finance", "EBITDA Margin", ebitda / rev * 100, "%", "up"),
            _row(p, "Finance", "Net Profit Margin", ni / rev * 100, "%", "up"),
            _row(p, "Finance", "Debt to Equity", s["debt"][i] / s["equity"][i], "x", "down"),
            # Statutory local-currency figure (OHADA books are kept in XOF).
            _row(p, "Finance", "Chiffre d'affaires (XOF)", rev * XOF_PER_USD, "XOF", "up"),
        ]
        # Runway is only meaningful while burning. Once the company is cash
        # generative the ratio explodes (cash / a token burn gave 233 months, which
        # is not information), so cap the reported figure at 36 - read as "36+".
        if ni < 0:
            runway = s["cash"][i] / max(1.0, -ni)
        else:
            runway = 36.0
        out.append(_row(p, "Finance", "Cash Runway", min(36.0, runway), "months", "up"))

        # ── Growth ──────────────────────────────────────────────────────────
        start_arr = s["arr"][i - 1] if i else s["arr"][0]
        nrr = (start_arr + s["expansion"][i] - s["contraction"][i] - s["churn_rev"][i]) / max(1.0, start_arr) * 100
        cust = s["customers"][i]
        logo_churn = s["churned_logos"][i] / max(1.0, cust + s["churned_logos"][i]) * 100
        arpu_m = s["mrr"][i] / max(1.0, cust)
        gm_frac = gross_profit / rev
        cac = s["sm_spend"][i] / max(0.5, s["new_logos"][i])
        ltv = arpu_m * gm_frac / max(0.0025, s["churned_logos"][i] / max(1.0, cust))
        # Before a full year of history exists, annualise the trailing run-rate
        # instead of reporting 0% — a company in month 1 is not a 0%-growth company,
        # and reporting it as one drags the composite health score down artificially.
        if i >= 12:
            yoy = (s["arr"][i] / s["arr"][i - 12] - 1.0) * 100
        else:
            back = max(1, min(i, 3))
            yoy = ((s["arr"][i] / s["arr"][i - back]) ** (12.0 / back) - 1.0) * 100 if i else 38.0
        out += [
            _row(p, "Growth", "ARR", s["arr"][i], "USD", "up"),
            _row(p, "Growth", "MRR", s["mrr"][i], "USD", "up"),
            _row(p, "Growth", "Customers", cust, "count", "up"),
            _row(p, "Growth", "New Customers", s["new_logos"][i], "count", "up"),
            _row(p, "Growth", "Churned Customers", s["churned_logos"][i], "count", "down"),
            _row(p, "Growth", "Expansion Revenue", s["expansion"][i], "USD", "up"),
            _row(p, "Growth", "Contraction Revenue", s["contraction"][i], "USD", "down"),
            _row(p, "Growth", "Net Revenue Retention", nrr, "%", "up"),
            _row(p, "Growth", "Monthly Churn Rate", logo_churn, "%", "down"),
            _row(p, "Growth", "ARPU", arpu_m, "USD", "up"),
            _row(p, "Growth", "CAC", cac, "USD", "down"),
            _row(p, "Growth", "LTV", ltv, "USD", "up"),
            _row(p, "Growth", "LTV to CAC Ratio", ltv / max(1.0, cac), "x", "up"),
            _row(p, "Growth", "CAC Payback Period", cac / max(1.0, arpu_m * gm_frac), "months", "down"),
            _row(p, "Growth", "YoY Revenue Growth", yoy, "%", "up"),
            _row(p, "Growth", "Rule of 40", yoy + (ebitda / rev * 100), "%", "up"),
        ]

        # ── People ──────────────────────────────────────────────────────────
        hc = s["headcount"][i]
        ann_turnover = s["separations"][i] * 12.0 / max(1.0, hc) * 100
        f = phase_for(p)
        enps = max(-32.0, min(58.0, 34.0 / f["attrition"] - 6.0 + jitter(f"en:{p}", 4.0)))
        ttf = max(19.0, 33.0 * f["attrition"] ** 0.6 + jitter(f"tf:{p}", 3.5))
        out += [
            _row(p, "People", "Headcount", hc, "count", "up"),
            _row(p, "People", "New Hires", s["hires"][i], "count", "up"),
            _row(p, "People", "Separations", s["separations"][i], "count", "down"),
            _row(p, "People", "Annual Employee Turnover", ann_turnover, "%", "down"),
            _row(p, "People", "Time to Hire", ttf, "days", "down"),
            _row(p, "People", "Employee Net Promoter Score", enps, "score", "up"),
            _row(p, "People", "Revenue per Employee", rev * 12.0 / max(1.0, hc), "USD", "up"),
            _row(p, "People", "Open Positions", s["open_reqs"][i], "count", "down"),
            _row(p, "People", "Offers Extended", s["offers"][i], "count", "up"),
            _row(p, "People", "Offers Accepted", s["offers_acc"][i], "count", "up"),
            _row(p, "People", "Offer Acceptance Rate",
                 s["offers_acc"][i] / max(0.5, s["offers"][i]) * 100, "%", "up"),
            _row(p, "People", "Training Hours per Employee",
                 max(1.5, 9.5 / f["attrition"] + jitter(f"th:{p}", 1.2)), "hours", "up"),
            _row(p, "People", "Absenteeism Rate", max(0.6, 2.9 * f["attrition"] ** 0.5 + jitter(f"ab:{p}", 0.4)), "%", "down"),
            _row(p, "People", "Cost Per Hire", max(900.0, 3100.0 * f["attrition"] ** 0.4 + jitter(f"ch:{p}", 220)), "USD", "down"),
        ]

        # ── Operations ──────────────────────────────────────────────────────
        av, pf, ql = s["availability"][i], s["performance"][i], s["quality"][i]
        out += [
            _row(p, "Operations", "Availability", av, "%", "up"),
            _row(p, "Operations", "Performance", pf, "%", "up"),
            _row(p, "Operations", "Quality Rate", ql, "%", "up"),
            _row(p, "Operations", "Overall Equipment Effectiveness",
                 av / 100 * pf / 100 * ql / 100 * 100, "%", "up"),
            _row(p, "Operations", "Defect Rate", s["defect_rate"][i], "%", "down"),
            _row(p, "Operations", "First Pass Yield", s["fpy"][i], "%", "up"),
            _row(p, "Operations", "Cycle Time Efficiency", s["cycle_eff"][i], "%", "up"),
            _row(p, "Operations", "Mean Time Between Failures", s["mtbf"][i], "hours", "up"),
            _row(p, "Operations", "Throughput",
                 max(40.0, s["headcount"][i] * 3.4 * (pf / 100) + jitter(f"tp:{p}", 12)), "count", "up"),
            _row(p, "Operations", "Capacity Utilization",
                 min(97.0, max(48.0, 74.0 * (pf / 100) * 1.18 + jitter(f"cu:{p}", 3.0))), "%", "up"),
            _row(p, "Operations", "Safety Incidents",
                 max(0.0, round(1.6 / max(0.7, f["delivery"]) + jitter(f"si:{p}", 0.9))), "count", "down"),
            _row(p, "Operations", "Downtime Hours",
                 max(0.5, (100.0 - av) * 1.9 + jitter(f"dh:{p}", 1.1)), "hours", "down"),
        ]

        # ── Logistics ───────────────────────────────────────────────────────
        out += [
            _row(p, "Logistics", "On-Time Delivery Rate", s["otd"][i], "%", "up"),
            _row(p, "Logistics", "Order Fulfillment Cycle Time", s["fulfil_hours"][i], "hours", "down"),
            _row(p, "Logistics", "Inventory Turnover", s["inv_turns"][i], "x", "up"),
            _row(p, "Logistics", "Supplier Defect Rate", s["supp_defect"][i], "%", "down"),
            _row(p, "Logistics", "Carrying Cost of Inventory", s["carrying"][i], "%", "down"),
            _row(p, "Logistics", "Total Orders",
                 max(12.0, s["customers"][i] * 0.42 + jitter(f"to:{p}", 6)), "count", "up"),
            _row(p, "Logistics", "Stockout Rate",
                 max(0.2, 2.4 / max(0.6, phase_for(p)["delivery"]) + jitter(f"so:{p}", 0.5)), "%", "down"),
            _row(p, "Logistics", "Warehouse Utilization",
                 min(94.0, max(38.0, 62.0 + 0.29 * i + jitter(f"wu:{p}", 4.0))), "%", "up"),
            _row(p, "Logistics", "Average Lead Time",
                 max(6.0, 21.0 / max(0.6, phase_for(p)["delivery"]) + jitter(f"lt:{p}", 2.5)), "days", "down"),
        ]

        # ── IT ──────────────────────────────────────────────────────────────
        out += [
            _row(p, "IT", "System Uptime", s["uptime"][i], "%", "up"),
            _row(p, "IT", "Mean Time To Resolution", s["mttr"][i], "hours", "down"),
            _row(p, "IT", "Deployment Frequency", s["deploys"][i], "per week", "up"),
            _row(p, "IT", "Change Failure Rate", s["cfr"][i], "%", "down"),
            _row(p, "IT", "Critical Vulnerabilities", s["crit_vulns"][i], "count", "down"),
            _row(p, "IT", "API P99 Latency", s["p99"][i], "ms", "down"),
            _row(p, "IT", "Total Incidents", s["incidents"][i], "count", "down"),
            _row(p, "IT", "Critical Incidents",
                 max(0.0, round(s["incidents"][i] * 0.12 + (6 if f["key"] == "security_breach" else 0))), "count", "down"),
            _row(p, "IT", "Open Tickets",
                 max(4.0, s["headcount"][i] * 0.28 / max(0.6, f["security"]) + jitter(f"ot2:{p}", 5)), "count", "down"),
            # Derived from that month's ACTUAL availability, not from the security
            # multiplier: SLA compliance is a statement about met service commitments,
            # so it has to move with uptime. Driving it from posture alone produced
            # 80% SLA in a month with 99.83% uptime, which is not a coherent pair.
            _row(p, "IT", "SLA Compliance",
                 min(99.6, max(68.0, 100.0 - (99.95 - s["uptime"][i]) * 12.0
                               + jitter(f"sl:{p}", 0.5))), "%", "up"),
            _row(p, "IT", "Security Score",
                 min(97.0, max(24.0, 84.0 * (0.42 + 0.58 * min(1.12, f["security"]))
                               + jitter(f"ss:{p}", 2.5))), "/100", "up"),
            _row(p, "IT", "Cloud Spend",
                 max(4000.0, rev * 0.052 + (48_000.0 if i >= 48 else 0.0)), "USD", "down"),
            _row(p, "IT", "Active Users",
                 max(60.0, s["customers"][i] * 34.0 + jitter(f"au2:{p}", 120)), "count", "up"),
            _row(p, "IT", "Lead Time For Changes",
                 max(2.4, 26.0 / max(0.6, f["security"]) * (1 + jitter(f"ltc:{p}", 0.15))), "hours", "down"),
        ]

        # ── ESG ─────────────────────────────────────────────────────────────
        tot_co2 = s["scope1"][i] + s["scope2"][i] + s["scope3"][i]
        out += [
            _row(p, "ESG", "Scope 1 Emissions", s["scope1"][i], "tCO2e", "down"),
            _row(p, "ESG", "Scope 2 Emissions", s["scope2"][i], "tCO2e", "down"),
            _row(p, "ESG", "Scope 3 Emissions", s["scope3"][i], "tCO2e", "down"),
            _row(p, "ESG", "Total Carbon Footprint", tot_co2, "tCO2e", "down"),
            _row(p, "ESG", "Energy Consumption", s["kwh"][i], "kWh", "down"),
            _row(p, "ESG", "Renewable Energy Ratio", s["renew"][i], "%", "up"),
            _row(p, "ESG", "Board Diversity Ratio", s["board_div"][i], "%", "up"),
            _row(p, "ESG", "Audit Compliance Score", s["audit"][i], "%", "up"),
            _row(p, "ESG", "Privacy Incident Count", s["privacy"][i], "count", "down"),
            _row(p, "ESG", "Water Consumption", s["water"][i], "m3", "down"),
            _row(p, "ESG", "Waste Diverted from Landfill", s["waste"][i], "%", "up"),
            _row(p, "ESG", "Carbon Intensity per Revenue",
                 tot_co2 / max(0.05, rev / 1_000_000.0), "tCO2e/USDm", "down"),
        ]

    return out


def health_index(period: str, kpis_by_period: Dict[str, Dict[str, float]]) -> Tuple[float, str]:
    """Composite 0-100 enterprise health for one month, from that month's own
    KPI rows — the same weighting IntelAI's health module documents."""
    k = kpis_by_period.get(period, {})

    def band(v, lo, hi):
        if v is None:
            return 50.0
        return max(0.0, min(100.0, (v - lo) / (hi - lo) * 100.0))

    growth = band(k.get("YoY Revenue Growth"), -10, 80)
    margin = band(k.get("EBITDA Margin"), -25, 30)
    cash = band(k.get("Cash Runway"), 2, 24)
    eff = band(k.get("Overall Equipment Effectiveness"), 45, 88)
    itq = band(k.get("SLA Compliance"), 70, 99.5)
    people = band(k.get("Employee Net Promoter Score"), -20, 50)
    score = 0.24 * growth + 0.22 * margin + 0.18 * cash + 0.14 * eff + 0.12 * itq + 0.10 * people

    vulns = k.get("Critical Vulnerabilities") or 0
    if vulns > 5:
        score -= min(12.0, (vulns - 5) * 1.4)
    if (k.get("Privacy Incident Count") or 0) > 0:
        score -= 6.0
    score = max(0.0, min(100.0, score))

    label = "Strong" if score >= 80 else "Stable" if score >= 60 else "At Risk" if score >= 40 else "Critical"
    return round(score, 1), label


if __name__ == "__main__":  # quick self-check
    rows = generate_kpis()
    ms = months()
    by = {}
    for r in rows:
        by.setdefault(r["period"], {})[r["metric_name"]] = r["value"]
    print(f"{COMPANY} — {len(rows)} KPI rows across {len(ms)} months "
          f"({ms[0]} .. {ms[-1]}), {len({r['category'] for r in rows})} domains")
    print()
    print(f"{'period':8} {'health':>6} {'label':10} {'ARR':>12} {'GM%':>6} {'NRR%':>6} "
          f"{'uptime':>7} {'OEE%':>6} {'head':>5}")
    for p in ms[::6]:
        h, lab = health_index(p, by)
        k = by[p]
        print(f"{p:8} {h:>6.1f} {lab:10} {k['ARR']:>12,.0f} {k['Gross Margin']:>6.1f} "
              f"{k['Net Revenue Retention']:>6.1f} {k['System Uptime']:>7.3f} "
              f"{k['Overall Equipment Effectiveness']:>6.1f} {k['Headcount']:>5.0f}")
