from __future__ import annotations

from copy import deepcopy

DEMO_LEADS = [
    {
        "id": "lead-apex",
        "name": "Paula Ibarra",
        "company": "Apex Analytics",
        "role": "Head of Sales",
        "source_channel": "Inbound + WhatsApp",
        "stage": "Discovery",
        "owner": "Lucas",
        "status": "activo",
        "last_activity_at": "2026-08-18",
        "objective": "ordenar pipeline y seguimiento comercial",
        "summary": "Operación trabada por seguimiento manual y baja visibilidad sobre oportunidades calientes.",
        "case_type": "inbound_hot",
    },
    {
        "id": "lead-nexa",
        "name": "Tomás Suárez",
        "company": "Nexa Studio",
        "role": "Founder",
        "source_channel": "Llamada",
        "stage": "Calificación",
        "owner": "Lucas",
        "status": "activo",
        "last_activity_at": "2026-08-17",
        "objective": "priorizar oportunidades y formalizar próximos pasos",
        "summary": "Equipo chico con crecimiento comercial desordenado y necesidad de lectura ejecutiva semanal.",
        "case_type": "outbound_warm",
    },
    {
        "id": "lead-orbit",
        "name": "Valentina Costa",
        "company": "Orbit Partners",
        "role": "Revenue Ops",
        "source_channel": "Meet",
        "stage": "Propuesta",
        "owner": "Lucas",
        "status": "seguimiento",
        "last_activity_at": "2026-08-16",
        "objective": "tener informes comerciales por cuenta y señales de riesgo",
        "summary": "Necesitan unificar insights de reuniones y seguimiento comercial en una sola capa de lectura.",
        "case_type": "outbound_warm",
    },
]

DEMO_SOURCES = {
    "lead-apex": [
        {
            "id": "src-apex-meet",
            "source_type": "Meet",
            "label": "Meet discovery",
            "summary": "Descubrieron cuellos de botella de seguimiento, falta de prioridad compartida y reporting disperso.",
            "pain_points": [
                "seguimiento manual en planillas",
                "no distinguen leads calientes de tibios",
                "la jefatura no ve bloqueos a tiempo",
            ],
            "signals": [
                "3 vendedores con pipeline activo",
                "quieren ordenar discovery y follow-up esta semana",
                "ven valor en una demo visible para dirección y operación",
            ],
            "risks": [
                "si no aterrizan próximos pasos rápido pierden momentum",
            ],
        },
        {
            "id": "src-apex-whatsapp",
            "source_type": "WhatsApp",
            "label": "WhatsApp follow-up",
            "summary": "Pidió propuesta aterrizada para 3 vendedores y una lectura ejecutiva simple para dirección.",
            "pain_points": [
                "las conversaciones quedan dispersas",
                "no documentan contexto entre interacciones",
            ],
            "signals": [
                "pidió propuesta aterrizada para 3 vendedores",
                "quieren comparar vista comercial y vista directiva",
            ],
            "risks": [
                "si la demo se ve muy técnica la dirección no compra el valor",
            ],
        },
    ],
    "lead-nexa": [
        {
            "id": "src-nexa-call",
            "source_type": "Llamada",
            "label": "Llamada de calificación",
            "summary": "Founder vende solo, tiene varias oportunidades abiertas y cero ritual de seguimiento.",
            "pain_points": [
                "seguimiento reactivo",
                "sin criterio claro de prioridad",
            ],
            "signals": [
                "quieren proceso simple, no otro CRM complejo",
                "valoran resúmenes accionables rápidos",
            ],
            "risks": [
                "capacidad operativa reducida para implementar cambios grandes",
            ],
        }
    ],
    "lead-orbit": [
        {
            "id": "src-orbit-meet",
            "source_type": "Meet",
            "label": "Meet de propuesta",
            "summary": "Revenue Ops quiere consolidar señales de cuenta para dar visibilidad al director comercial.",
            "pain_points": [
                "insights repartidos entre reuniones y notas",
                "sin lectura consolidada por cuenta",
            ],
            "signals": [
                "ya tienen operación comercial con disciplina básica",
                "necesitan vista ejecutiva por oportunidad",
            ],
            "risks": [
                "si no ven consolidación real puede parecer otra capa manual",
            ],
        }
    ],
}


def list_demo_leads() -> list[dict]:
    return [deepcopy(lead) for lead in DEMO_LEADS]


def get_demo_lead(lead_id: str | None) -> dict | None:
    if not lead_id:
        return None
    for lead in DEMO_LEADS:
        if lead["id"] == lead_id:
            return deepcopy(lead)
    return None


def list_lead_sources(lead_id: str | None) -> list[dict]:
    return [deepcopy(source) for source in DEMO_SOURCES.get(lead_id or "", [])]


def get_lead_source(lead_id: str | None, source_id: str | None) -> dict | None:
    if not lead_id or not source_id:
        return None
    for source in DEMO_SOURCES.get(lead_id, []):
        if source["id"] == source_id:
            return deepcopy(source)
    return None


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
