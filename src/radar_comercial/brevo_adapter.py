from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BREVO_API_BASE = "https://api.brevo.com/v3"


def _api_key() -> str | None:
    return os.getenv("BREVO_API_KEY") or None


def _fetch_json(path: str, params: dict[str, Any] | None = None) -> dict:
    api_key = _api_key()
    if not api_key:
        raise RuntimeError("BREVO_API_KEY no configurada")
    url = f"{BREVO_API_BASE}{path}"
    if params:
        url = f"{url}?{urlencode(params)}"
    request = Request(url, headers={"accept": "application/json", "api-key": api_key})
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def list_brevo_deal_summaries(limit: int = 10) -> list[dict]:
    try:
        payload = _fetch_json("/crm/deals", {"limit": limit, "sort": "desc"})
    except (RuntimeError, HTTPError, URLError, TimeoutError, ValueError):
        return []

    summaries: list[dict] = []
    for item in payload.get("items", []):
        attrs = item.get("attributes", {})
        deal_name = attrs.get("deal_name") or item.get("id", "sin nombre")
        activities = attrs.get("number_of_activities", 0)
        summaries.append(
            {
                "id": item.get("id", ""),
                "label": f"{deal_name} · actividades: {activities}",
                "stage": attrs.get("deal_stage", ""),
            }
        )
    return summaries


def get_brevo_deal(deal_id: str) -> dict:
    return _fetch_json(f"/crm/deals/{deal_id}")


def get_brevo_contact(contact_id: int) -> dict:
    return _fetch_json(f"/contacts/{contact_id}")


def _full_name(contact: dict) -> str:
    attrs = contact.get("attributes", {})
    first = (attrs.get("NOMBRE") or "").strip()
    last = (attrs.get("APELLIDOS") or "").strip()
    name = " ".join(part for part in (first, last) if part)
    return name or contact.get("email") or f"contacto {contact.get('id', 'sin-id')}"


def _infer_case_type(deal: dict) -> str:
    attrs = deal.get("attributes", {})
    activities = int(attrs.get("number_of_activities") or 0)
    if activities >= 4:
        return "inbound_hot"
    if activities >= 2:
        return "outbound_warm"
    return "outbound_cold"


def deal_to_case(deal: dict, contact: dict | None = None) -> dict:
    attrs = deal.get("attributes", {})
    deal_name = attrs.get("deal_name") or deal.get("id", "oportunidad Brevo")
    activities = int(attrs.get("number_of_activities") or 0)
    pipeline = attrs.get("pipeline", "pipeline no identificado")
    stage = attrs.get("deal_stage", "etapa no identificada")
    last_activity = attrs.get("last_activity_date") or attrs.get("last_updated_date") or attrs.get("created_at") or "sin actividad reciente"
    contact_name = _full_name(contact) if contact else "contacto no resuelto"
    contact_email = (contact or {}).get("email") or "email no disponible"

    pain_points = [
        "necesita contexto comercial consolidado desde el CRM",
        "seguimiento y priorización todavía dependen de lectura manual",
    ]
    signals = [
        f"{activities} actividades registradas en Brevo",
        f"etapa actual CRM: {stage}",
        f"pipeline asociado: {pipeline}",
        f"última actividad CRM: {last_activity}",
        f"contacto principal: {contact_name} <{contact_email}>",
    ]
    risks = ["sin resumen curado todavía"]
    if attrs.get("lost_reason"):
        risks.append(f"motivo de pérdida histórico: {attrs['lost_reason']}")

    return {
        "company": deal_name,
        "objective": "ordenar seguimiento comercial y priorizar la oportunidad desde CRM",
        "pain_points": pain_points,
        "signals": signals,
        "risks": risks,
        "case_type": _infer_case_type(deal),
        "source_kind": "brevo",
        "source_label": f"Brevo deal {deal.get('id', '')}",
    }


def load_brevo_case(deal_id: str) -> dict | None:
    if not deal_id:
        return None
    try:
        deal = get_brevo_deal(deal_id)
        linked_contacts = deal.get("linkedContactsIds") or []
        contact = get_brevo_contact(linked_contacts[0]) if linked_contacts else None
    except (RuntimeError, HTTPError, URLError, TimeoutError, ValueError):
        return None
    return deal_to_case(deal, contact)
