from __future__ import annotations

from typing import Any

from radar_comercial.analysis import analyze_case
from radar_comercial.crm_demo import get_demo_lead, get_lead_source, list_lead_sources, load_demo_case


LANGGRAPH_AVAILABLE = False
try:
    import langgraph  # type: ignore  # noqa: F401
except Exception:
    LANGGRAPH_AVAILABLE = False
else:
    LANGGRAPH_AVAILABLE = True


def orchestration_backend_name() -> str:
    return "langgraph" if LANGGRAPH_AVAILABLE else "linear"


def orchestrate_demo_lead_reports(lead_id: str, *, llm_provider: Any = None) -> dict | None:
    lead = get_demo_lead(lead_id)
    if not lead:
        return None

    source_reports = []
    for source in list_lead_sources(lead_id):
        case = load_demo_case(lead_id, source["id"])
        if not case:
            continue
        report = analyze_case(case, llm_provider=llm_provider)
        report["source_kind"] = case.get("source_kind", "crm_demo")
        report["source_label"] = case.get("source_label", report.get("source_label", "CRM demo"))
        source_reports.append({"source": source, "case": case, "report": report})

    consolidated_case = load_demo_case(lead_id)
    if not consolidated_case:
        return None
    consolidated_report = analyze_case(consolidated_case, llm_provider=llm_provider)
    consolidated_report["source_kind"] = consolidated_case.get("source_kind", "crm_demo")
    consolidated_report["source_label"] = consolidated_case.get("source_label", consolidated_report.get("source_label", "CRM demo"))

    return {
        "lead_id": lead_id,
        "lead": lead,
        "source_count": len(source_reports),
        "source_reports": source_reports,
        "consolidated_case": consolidated_case,
        "consolidated_report": consolidated_report,
        "orchestration_backend": orchestration_backend_name(),
    }
