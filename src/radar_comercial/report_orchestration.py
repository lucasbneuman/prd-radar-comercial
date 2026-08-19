from __future__ import annotations

from typing import Any

from radar_comercial.analysis import analyze_case
from radar_comercial.crm_demo import get_demo_lead, list_lead_sources, load_demo_case


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


def build_view_models_for_lead(lead_id: str, *, llm_provider: Any = None) -> dict | None:
    orchestration = orchestrate_demo_lead_reports(lead_id, llm_provider=llm_provider)
    if not orchestration:
        return None

    lead = orchestration["lead"]
    consolidated = orchestration["consolidated_report"]
    source_reports = orchestration["source_reports"]

    commercial = {
        "audience": "commercial",
        "title": "Vista Comercial",
        "priority": consolidated["priority"],
        "focus": consolidated["summary"],
        "next_steps": consolidated["next_steps"],
        "source_priorities": [
            {
                "label": item["source"]["label"],
                "source_type": item["source"]["source_type"],
                "priority": item["report"]["priority"],
            }
            for item in source_reports
        ],
    }

    executive = {
        "audience": "executive",
        "title": "Vista Directiva",
        "headline": f"{lead['company']} requiere atención {consolidated['priority']}",
        "decision_note": consolidated["rationale"],
        "source_overview": [
            {
                "label": item["source"]["label"],
                "source_type": item["source"]["source_type"],
                "summary": item["report"]["summary"],
            }
            for item in source_reports
        ],
    }

    return {
        "lead_id": lead_id,
        "orchestration": orchestration,
        "views": {
            "commercial": commercial,
            "executive": executive,
        },
    }
