from __future__ import annotations

import json
from collections import Counter
from copy import deepcopy
from importlib import resources
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
REPO_DATASET_PATH = BASE_DIR / "examples" / "crm-demo-dataset.json"
PACKAGE_DATASET_RESOURCE = resources.files("radar_comercial") / "data" / "crm-demo-dataset.json"


def _dataset_text() -> tuple[str, str]:
    if REPO_DATASET_PATH.exists():
        return REPO_DATASET_PATH.read_text(encoding="utf-8"), str(REPO_DATASET_PATH)
    return PACKAGE_DATASET_RESOURCE.read_text(encoding="utf-8"), str(PACKAGE_DATASET_RESOURCE)


def _load_dataset() -> dict:
    content, _ = _dataset_text()
    return json.loads(content)


def _dataset_path() -> str:
    _, path = _dataset_text()
    return path


def _load_leads() -> list[dict]:
    return _load_dataset().get("leads", [])


def _load_sources() -> dict[str, list[dict]]:
    return _load_dataset().get("sources", {})


def _sorted_leads() -> list[dict]:
    return sorted(_load_leads(), key=lambda lead: lead["last_activity_at"], reverse=True)


def list_demo_leads() -> list[dict]:
    return [deepcopy(lead) for lead in _sorted_leads()]


def get_demo_lead(lead_id: str | None) -> dict | None:
    if not lead_id:
        return None
    for lead in _load_leads():
        if lead["id"] == lead_id:
            return deepcopy(lead)
    return None


def list_lead_sources(lead_id: str | None) -> list[dict]:
    return [deepcopy(source) for source in _load_sources().get(lead_id or "", [])]


def get_lead_source(lead_id: str | None, source_id: str | None) -> dict | None:
    if not lead_id or not source_id:
        return None
    for source in _load_sources().get(lead_id, []):
        if source["id"] == source_id:
            return deepcopy(source)
    return None


def list_demo_stages() -> list[str]:
    return sorted({lead["stage"] for lead in _load_leads()})


def list_demo_source_types() -> list[str]:
    kinds = {source["source_type"] for sources in _load_sources().values() for source in sources}
    return sorted(kinds)


def summarize_demo_dataset() -> dict:
    leads = _load_leads()
    sources = _load_sources()
    stage_counts = Counter(lead["stage"] for lead in leads)
    source_type_counts = Counter(source["source_type"] for lead_sources in sources.values() for source in lead_sources)
    return {
        "lead_count": len(leads),
        "source_count": sum(len(lead_sources) for lead_sources in sources.values()),
        "by_stage": dict(stage_counts),
        "by_source_type": dict(source_type_counts),
        "lead_ids": [lead["id"] for lead in _sorted_leads()],
        "dataset_path": _dataset_path(),
    }


def load_demo_case(lead_id: str | None, source_id: str | None = None) -> dict | None:
    lead = get_demo_lead(lead_id)
    if not lead:
        return None

    source = get_lead_source(lead_id, source_id)
    sources = list_lead_sources(lead_id)
    pain_points: list[str] = []
    signals: list[str] = []
    risks: list[str] = []

    if source:
        pain_points.extend(source.get("pain_points", []))
        signals.extend(source.get("signals", []))
        risks.extend(source.get("risks", []))
        source_label = f"CRM demo · {source.get('source_type', 'Fuente')} · {lead['company']}"
        objective = lead.get("objective", "")
    else:
        for item in sources:
            pain_points.extend(item.get("pain_points", []))
            signals.extend(item.get("signals", []))
            risks.extend(item.get("risks", []))
        source_label = f"CRM demo · {lead['company']}"
        objective = lead.get("objective", "")

    if lead.get("summary"):
        signals.insert(0, lead["summary"])

    return {
        "company": lead["company"],
        "objective": objective,
        "pain_points": pain_points,
        "signals": signals,
        "risks": risks,
        "case_type": lead.get("case_type", "generic"),
        "source_kind": "crm_demo",
        "source_label": source_label,
        "lead_id": lead["id"],
    }
