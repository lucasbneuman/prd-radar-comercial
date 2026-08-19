from __future__ import annotations

from radar_comercial.llm_provider import (
    ReportNarrativeProvider,
    build_llm_provider_from_env,
    enrich_report_with_provider,
)
from radar_comercial.models import CommercialCase, RadarReport


CASE_TYPE_WEIGHTS = {
    "inbound_hot": 2,
    "outbound_warm": 1,
    "outbound_cold": 0,
    "generic": 0,
}


def analyze_commercial_case(case: CommercialCase) -> RadarReport:
    breakdown: list[str] = [f"tipo de caso: {case.case_type}"]
    score = CASE_TYPE_WEIGHTS.get(case.case_type, 0)

    if case.pain_points:
        score += 2
        breakdown.append("dolor operativo")
    if case.signals:
        score += 1
        breakdown.append("señal comercial inicial")
    if any("pidió demo" in signal.lower() for signal in case.signals):
        score += 2
        breakdown.append("interés activo")
    if any("equipo comercial activo" in signal.lower() for signal in case.signals):
        score += 1
        breakdown.append("capacidad interna de adopción")
    has_closing_urgency = any("urgencia de cierre" in signal.lower() for signal in case.signals)
    if has_closing_urgency:
        score += 2
        breakdown.append("urgencia de cierre")
    if any("pipeline roto" in risk.lower() for risk in case.risks):
        score += 1
        breakdown.append("pipeline comprometido")
    if case.risks:
        score += 1
        breakdown.append("riesgo declarado")

    if score >= 8 and has_closing_urgency:
        priority = "critica"
        confidence = "alta"
        next_steps = [
            "Agendar demo enfocada en prioridades y siguientes pasos.",
            "Preparar propuesta de activación inmediata con foco en cierre.",
        ]
        rationale = "Caso con urgencia comercial alta y señales suficientes para una activación inmediata."
    elif score >= 6:
        priority = "alta"
        confidence = "alta"
        next_steps = ["Agendar demo enfocada en prioridades y siguientes pasos."]
        rationale = "Caso con señales suficientes para una demo orientada a cierre."
    elif score >= 3:
        priority = "media"
        confidence = "media"
        next_steps = ["Validar urgencia real y criterio de compra."]
        rationale = "Falta evidencia suficiente para una urgencia alta."
    else:
        priority = "baja"
        confidence = "baja"
        next_steps = ["Mantener seguimiento liviano y buscar una señal concreta de oportunidad."]
        rationale = "Evidencia insuficiente para priorizar este caso en la ola actual."

    return RadarReport(
        summary=f"{case.company} necesita {case.objective}.",
        priority=priority,
        confidence=confidence,
        score_total=score,
        score_breakdown=breakdown,
        rationale=rationale,
        signals_positive=list(case.signals),
        signals_risk=list(case.risks),
        next_steps=next_steps,
        case_type=case.case_type,
    )


def analyze_case(case: dict, llm_provider: ReportNarrativeProvider | None = None) -> dict:
    commercial_case = CommercialCase.from_dict(case)
    report = analyze_commercial_case(commercial_case).to_dict()
    provider = llm_provider or build_llm_provider_from_env()
    return enrich_report_with_provider(case=case, report=report, llm_provider=provider)
