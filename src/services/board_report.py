"""Board-ready PDF report — executive summary, per-domain KPI tables, and an anomaly
watchlist, rendered with reportlab (pure-Python, no system libs). Used by the
``/data/export`` endpoint when ``format=pdf``."""
from __future__ import annotations

from datetime import datetime
from io import BytesIO

from src.core.logger import get_logger

log = get_logger(__name__)

_INDIGO = "#4f46e5"
_INK = "#111827"
_MUTED = "#6b7280"
_HEADER_BG = "#eef2ff"


def generate_board_pdf() -> bytes:
    """Render the live KPI data + insights into a multi-section board report PDF (bytes)."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
    )

    from src.services.insights import compute_health_index, compute_risk_score, detect_anomalies
    from src.services.pg_store import get_kpi_metrics

    df = get_kpi_metrics()
    health = compute_health_index(df) if not df.empty else {"score": 0, "label": "n/a"}
    risk = compute_risk_score(df) if not df.empty else {"score": 0, "label": "n/a"}
    latest = sorted(df["period"].unique())[-1] if not df.empty else "—"

    styles = getSampleStyleSheet()
    title = ParagraphStyle("t", parent=styles["Title"], textColor=colors.HexColor(_INDIGO), fontSize=22)
    sub = ParagraphStyle("s", parent=styles["Normal"], textColor=colors.HexColor(_MUTED), fontSize=9)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=colors.HexColor(_INK), fontSize=13, spaceBefore=10)
    h3 = ParagraphStyle("h3", parent=styles["Heading3"], textColor=colors.HexColor(_INDIGO), fontSize=11, spaceBefore=6)

    def _table(rows, widths, header=True):
        t = Table(rows, colWidths=widths, hAlign="LEFT")
        style = [
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor(_INK)),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]
        if header:
            style += [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(_HEADER_BG)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor(_INDIGO)),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        t.setStyle(TableStyle(style))
        return t

    story = [
        Paragraph("IntelAI — Executive Board Report", title),
        Paragraph(f"Generated {datetime.utcnow():%Y-%m-%d %H:%M} UTC · Reporting period {latest}", sub),
        Spacer(1, 6 * mm),
        Paragraph("Executive Summary", h2),
        _table(
            [
                ["Indicator", "Value"],
                ["Company Health Index", f"{health.get('score', 0)} / 100  ({health.get('label', '')})"],
                ["Risk Score", f"{risk.get('score', 0)} / 100  ({risk.get('label', '')})"],
                ["Revenue growth (latest)", f"{float(health.get('growth', 0)):.1f}%"],
                ["Gross margin", f"{float(health.get('margin', 0)):.1f}%"],
                ["Anomalies flagged", str(risk.get("anomaly_count", 0))],
            ],
            [70 * mm, 95 * mm],
        ),
        Spacer(1, 4 * mm),
    ]

    # Per-domain KPI tables (latest period)
    if not df.empty:
        latest_df = df[df["period"] == latest]
        story.append(Paragraph("Key Metrics by Domain", h2))
        for cat in sorted(latest_df["category"].unique()):
            cdf = latest_df[latest_df["category"] == cat].sort_values("metric")
            rows = [["Metric", "Latest", "Unit", "Better when"]]
            for r in cdf.itertuples():
                better = "higher" if getattr(r, "direction", "") == "up" else "lower"
                rows.append([str(r.metric), f"{float(r.value):,.2f}", str(r.unit), better])
            story.append(Paragraph(cat, h3))
            story.append(_table(rows, [72 * mm, 33 * mm, 30 * mm, 30 * mm]))
            story.append(Spacer(1, 3 * mm))

    # Anomaly watchlist
    try:
        an = detect_anomalies(df) if not df.empty else None
        if an is not None and not an.empty:
            aw = an[an["is_anomaly"] == True] if "is_anomaly" in an.columns else an  # noqa: E712
            if not aw.empty:
                story.append(Paragraph("Risk Watchlist — Recent Anomalies", h2))
                rows = [["Metric", "Category", "Period", "Value"]]
                for r in aw.head(12).itertuples():
                    rows.append([
                        str(getattr(r, "metric", "")), str(getattr(r, "category", "")),
                        str(getattr(r, "period", "")), f"{float(getattr(r, 'value', 0)):,.2f}",
                    ])
                story.append(_table(rows, [55 * mm, 45 * mm, 30 * mm, 35 * mm]))
    except Exception as e:  # never fail the whole report on the optional section
        log.warning("Board report anomaly section skipped: %s", e)

    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(
        "Generated by IntelAI · Persona-Aware AI Analytics & RAG Copilot. Figures are drawn "
        "from the live KPI store for the reporting period shown.", sub,
    ))

    buf = BytesIO()
    SimpleDocTemplate(
        buf, pagesize=A4, topMargin=16 * mm, bottomMargin=16 * mm,
        leftMargin=16 * mm, rightMargin=16 * mm, title="IntelAI Board Report",
    ).build(story)
    return buf.getvalue()
