from __future__ import annotations

from radar_comercial.models import RadarReport


def render_radar_report_markdown(report: RadarReport) -> str:
    positive = "\n".join(f"- {item}" for item in report.signals_positive) or "- Sin señales positivas registradas"
    risks = "\n".join(f"- {item}" for item in report.signals_risk) or "- Sin riesgos registrados"
    next_steps = "\n".join(f"- {item}" for item in report.next_steps) or "- Sin próximos pasos registrados"
    score_breakdown = "\n".join(f"- {item}" for item in report.score_breakdown) or "- Sin breakdown registrado"

    extra = ""
    if report.rationale:
        extra += f"\n## Rationale\n{report.rationale}\n"
    if report.score_total or report.score_breakdown:
        extra += (
            f"\n## Scoring\n**Tipo de caso:** {report.case_type}\n\n"
            f"**Confianza:** {report.confidence}\n\n**Score total:** {report.score_total}\n\n### Breakdown\n{score_breakdown}\n"
        )

    return (
        "# Radar Comercial\n\n"
        f"## Resumen\n{report.summary}\n\n"
        f"**Prioridad:** {report.priority}\n\n"
        "## Señales positivas\n"
        f"{positive}\n\n"
        "## Riesgos\n"
        f"{risks}{extra}\n"
        "## Próximos pasos\n"
        f"{next_steps}\n"
    )


def render_report_markdown(report: dict) -> str:
    return render_radar_report_markdown(RadarReport(**report))
