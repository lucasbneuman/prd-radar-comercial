from __future__ import annotations

CURATED_CASES = {
    "meet_discovery": {
        "company": "Discovery Meet",
        "objective": "convertir resumen de reunión en oportunidad priorizable",
        "pain_points": [
            "la reunión deja insights útiles pero no baja estructurada al pipeline",
            "el equipo comercial pierde tiempo releyendo notas manuales",
        ],
        "signals": [
            "resumen curado de reunión con pedido de propuesta",
            "mencionaron urgencia de ordenar seguimiento post-demo",
        ],
        "risks": ["todavía depende de una fuente curada y no del runtime real de Meet"],
        "case_type": "inbound_hot",
        "source_kind": "curated_meet",
        "source_label": "Resumen curado · Meet discovery",
    },
    "whatsapp_followup": {
        "company": "WhatsApp Follow-up",
        "objective": "capturar señales de compra desde conversaciones de WhatsApp",
        "pain_points": [
            "los follow-ups quedan dispersos en chat",
            "no hay priorización automática de intención comercial",
        ],
        "signals": [
            "resumen curado de WhatsApp con consulta por demo",
            "respondió rápido y pidió próximos pasos",
        ],
        "risks": ["el origen todavía es curado y no una integración productiva real"],
        "case_type": "outbound_warm",
        "source_kind": "curated_whatsapp",
        "source_label": "Resumen curado · WhatsApp",
    },
    "phone_call_recap": {
        "company": "Phone Call Recap",
        "objective": "detectar urgencia comercial desde una llamada resumida",
        "pain_points": [
            "la llamada telefónica se resume fuera del CRM",
            "el contexto de cierre no llega ordenado al equipo",
        ],
        "signals": [
            "resumen curado de llamada con urgencia de cierre",
            "solicitó propuesta dentro de la semana",
            "urgencia de cierre",
        ],
        "risks": ["falta ingestión real desde proveedor telefónico"],
        "case_type": "inbound_hot",
        "source_kind": "curated_phone",
        "source_label": "Resumen curado · Llamada telefónica",
    },
}


def list_curated_sources() -> list[dict]:
    options = []
    for source_id, case in CURATED_CASES.items():
        options.append({"id": source_id, "label": case["source_label"]})
    return options


def load_curated_case(source_id: str) -> dict | None:
    case = CURATED_CASES.get(source_id)
    if not case:
        return None
    return {
        **case,
        "source_id": source_id,
    }
