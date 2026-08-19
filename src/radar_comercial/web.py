from __future__ import annotations

import json
from html import escape
from pathlib import Path
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from radar_comercial.analysis import analyze_case
from radar_comercial.brevo_adapter import list_brevo_deal_summaries, load_brevo_case
from radar_comercial.crm_demo import get_demo_lead, get_lead_source, list_demo_leads, list_lead_sources, load_demo_case
from radar_comercial.curated_sources import list_curated_sources, load_curated_case
from radar_comercial.report_orchestration import build_view_models_for_lead, orchestrate_demo_lead_reports
from radar_comercial.run_store import DEFAULT_RUNS_PATH, append_run, load_runs

BASE_DIR = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = BASE_DIR / "examples"

HTML_TEMPLATE = """<!doctype html>
<html lang=\"es\">
<head>
  <meta charset=\"utf-8\">
  <title>Radar Comercial</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; background: #0f172a; color: #e2e8f0; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem; align-items: start; }}
    .card {{ background: #111827; padding: 1rem; border-radius: 12px; border: 1px solid #334155; }}
    textarea, input, select {{ width: 100%; margin-top: .35rem; margin-bottom: .75rem; padding: .65rem; border-radius: 8px; border: 1px solid #475569; background: #0f172a; color: #e2e8f0; }}
    button {{ background: #22c55e; color: #052e16; border: 0; padding: .75rem 1rem; border-radius: 8px; font-weight: bold; cursor: pointer; }}
    .secondary {{ background: #38bdf8; color: #082f49; }}
    .chip {{ display: inline-block; padding: .2rem .55rem; border-radius: 999px; background: #1e293b; border: 1px solid #475569; margin-right: .4rem; margin-bottom: .4rem; }}
    ul {{ padding-left: 1.2rem; }}
    code {{ background: #0f172a; padding: .1rem .35rem; border-radius: 6px; }}
    a {{ color: #7dd3fc; }}
    hr {{ border-color: #334155; margin: 1rem 0; }}
    .muted {{ color: #94a3b8; }}
    .link-list li {{ margin-bottom: .5rem; }}
  </style>
</head>
<body>
  <h1>Radar Comercial</h1>
  <p>Demo para convertir contexto comercial mínimo en una lectura accionable, incluyendo CRM demo interno, CRM real y resúmenes curados.</p>
  <div class=\"grid\">{content}</div>
</body>
</html>"""


def _split_lines(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def _available_examples() -> list[str]:
    if not EXAMPLES_DIR.exists():
        return []
    return sorted(path.name for path in EXAMPLES_DIR.glob("*.json"))


def _load_example_case(name: str | None) -> dict | None:
    if not name:
        return None
    path = EXAMPLES_DIR / name
    if not path.exists() or path.parent != EXAMPLES_DIR:
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload.setdefault("source_kind", "example")
    payload.setdefault("source_label", f"Ejemplo local · {name}")
    return payload


def _blank_case() -> dict:
    return {
        "company": "",
        "objective": "",
        "pain_points": [],
        "signals": [],
        "risks": [],
        "case_type": "generic",
        "source_kind": "manual",
        "source_label": "Carga manual",
    }


def _build_case(form: dict[str, list[str]]) -> dict:
    return {
        "company": form.get("company", [""])[0].strip(),
        "objective": form.get("objective", [""])[0].strip(),
        "pain_points": _split_lines(form.get("pain_points", [""])[0]),
        "signals": _split_lines(form.get("signals", [""])[0]),
        "risks": _split_lines(form.get("risks", [""])[0]),
        "case_type": form.get("case_type", ["generic"])[0].strip() or "generic",
        "source_kind": form.get("source_kind", ["manual"])[0].strip() or "manual",
        "source_label": form.get("source_label", ["Carga manual"])[0].strip() or "Carga manual",
    }


def _render_case_type_options(selected: str) -> list[str]:
    options = ["generic", "inbound_hot", "outbound_warm", "outbound_cold"]
    rendered = []
    for option in options:
        flag = " selected" if option == selected else ""
        rendered.append(f'<option value="{option}"{flag}>{option}</option>')
    return rendered


def _render_example_options(selected: str | None) -> list[str]:
    rendered = ['<option value="">manual</option>']
    for option in _available_examples():
        flag = " selected" if option == selected else ""
        rendered.append(f'<option value="{option}"{flag}>{option}</option>')
    return rendered


def _render_brevo_options(selected: str | None) -> list[str]:
    rendered = ['<option value="">seleccionar deal real</option>']
    for item in list_brevo_deal_summaries(limit=10):
        deal_id = item.get("id", "")
        label = item.get("label", deal_id)
        flag = " selected" if deal_id == selected else ""
        rendered.append(f'<option value="{escape(deal_id)}"{flag}>{escape(label)}</option>')
    return rendered


def _render_curated_source_options(selected: str | None) -> list[str]:
    rendered = ['<option value="">seleccionar resumen curado</option>']
    for item in list_curated_sources():
        source_id = item.get("id", "")
        label = item.get("label", source_id)
        flag = " selected" if source_id == selected else ""
        rendered.append(f'<option value="{escape(source_id)}"{flag}>{escape(label)}</option>')
    return rendered


def _render_crm_demo(selected_lead_id: str | None = None, selected_source_id: str | None = None, selected_view: str | None = None) -> str:
    selected_lead = get_demo_lead(selected_lead_id)
    selected_source = get_lead_source(selected_lead_id, selected_source_id)
    source_items = list_lead_sources(selected_lead_id)
    lead_links = []
    for lead in list_demo_leads():
        lead_links.append(
            "<li>"
            f"<a href='/?lead_id={escape(lead['id'])}'><strong>{escape(lead['company'])}</strong></a>"
            f" · {escape(lead['stage'])} · {escape(lead.get('source_channel') or lead.get('primary_channel') or 'Canal no definido')}"
            f"<br><span class='muted'>{escape(lead['summary'])}</span>"
            "</li>"
        )

    detail = "<p class='muted'>Elegí un lead para abrir la ficha y llevarlo al radar.</p>"
    if selected_lead:
        chips = "".join(
            [
                f"<span class='chip'>{escape(selected_lead['role'])}</span>",
                f"<span class='chip'>{escape(selected_lead['stage'])}</span>",
                f"<span class='chip'>{escape(selected_lead['status'])}</span>",
            ]
        )
        source_links = []
        for source in source_items:
            source_links.append(
                "<li>"
                f"<a href='/?lead_id={escape(selected_lead['id'])}&source_id={escape(source['id'])}&view=report'>"
                f"{escape(source['source_type'])} · {escape(source['label'])}</a>"
                f"<br><span class='muted'>{escape(source['summary'])}</span>"
                "</li>"
            )
        detail = f"""
        <h3>Ficha del lead</h3>
        <p><strong>{escape(selected_lead['company'])}</strong> · {escape(selected_lead['name'])}</p>
        <p class='muted'>{escape(selected_lead['summary'])}</p>
        <p>{chips}</p>
        <p><strong>Última actividad:</strong> {escape(selected_lead['last_activity_at'])}</p>
        <p><strong>Objetivo:</strong> {escape(selected_lead['objective'])}</p>
        <h4>Fuentes disponibles</h4>
        <ul class='link-list'>{''.join(source_links)}</ul>
        <p><a href='/?lead_id={escape(selected_lead['id'])}&view=report'>Ver informe general</a></p>
        """
        if selected_source:
            detail += f"""
            <hr>
            <h4>Fuente enfocada: {escape(selected_source['source_type'])}</h4>
            <p>{escape(selected_source['summary'])}</p>
            """
        if selected_view == "report":
            detail += f"""
            <hr>
            <p class='muted'>{'Informe por fuente' if selected_source else 'Informe general del lead'}</p>
            """

    return f"""
    <section class=\"card\">
      <h2>CRM demo interno</h2>
      <p class=\"muted\">Leads demo propios de Radar para una narrativa controlada y repetible.</p>
      <h3>Leads demo</h3>
      <ul class=\"link-list\">{''.join(lead_links)}</ul>
      <hr>
      {detail}
    </section>
    """


def _render_form(case: dict | None = None, *, selected_example: str | None = None, selected_brevo_deal: str | None = None, selected_curated_source: str | None = None) -> str:
    case = case or _blank_case()
    source_label = escape(case.get("source_label", "Carga manual"))
    source_kind = escape(case.get("source_kind", "manual"))
    return f"""
    <section class=\"card\">
      <h2>Input comercial</h2>
      <p class=\"muted\">Origen actual: <strong>{source_label}</strong></p>
      <form method=\"get\">
        <label>Ejemplo local
          <select name=\"example\">{''.join(_render_example_options(selected_example))}</select>
        </label>
        <button class=\"secondary\" type=\"submit\">Cargar ejemplo</button>
      </form>
      <hr>
      <form method=\"get\">
        <h3>CRM demo</h3>
        <label>Lead demo
          <input name=\"lead_id\" value=\"{escape(case.get('lead_id', ''))}\" placeholder=\"lead-apex\">
        </label>
        <button class=\"secondary\" type=\"submit\">Abrir lead</button>
      </form>
      <hr>
      <form method=\"get\">
        <h3>Cargar desde Brevo</h3>
        <label>Deal real CRM
          <select name=\"brevo_deal\">{''.join(_render_brevo_options(selected_brevo_deal))}</select>
        </label>
        <button class=\"secondary\" type=\"submit\">Importar deal</button>
      </form>
      <hr>
      <form method=\"get\">
        <h3>Resumen curado</h3>
        <label>Fuente simulada
          <select name=\"curated_source\">{''.join(_render_curated_source_options(selected_curated_source))}</select>
        </label>
        <button class=\"secondary\" type=\"submit\">Cargar resumen curado</button>
      </form>
      <hr>
      <form method=\"post\">
        <input type=\"hidden\" name=\"source_kind\" value=\"{source_kind}\">
        <input type=\"hidden\" name=\"source_label\" value=\"{source_label}\">
        <label>Empresa<input name=\"company\" value=\"{escape(case['company'])}\" required></label>
        <label>Objetivo<input name=\"objective\" value=\"{escape(case['objective'])}\" required></label>
        <label>Pain points<textarea name=\"pain_points\" rows=\"5\">{escape(chr(10).join(case['pain_points']))}</textarea></label>
        <label>Señales<textarea name=\"signals\" rows=\"5\">{escape(chr(10).join(case['signals']))}</textarea></label>
        <label>Riesgos<textarea name=\"risks\" rows=\"4\">{escape(chr(10).join(case['risks']))}</textarea></label>
        <label>Tipo de caso
          <select name=\"case_type\">{''.join(_render_case_type_options(case['case_type']))}</select>
        </label>
        <label>Formato de respuesta
          <select name=\"response_format\">
            <option value=\"html\" selected>html</option>
            <option value=\"json\">json</option>
          </select>
        </label>
        <button type=\"submit\">Analizar caso</button>
      </form>
    </section>
    """


def _render_recent_runs() -> str:
    runs = load_runs(DEFAULT_RUNS_PATH)[-5:]
    if not runs:
        return "<p>Sin corridas persistidas todavía.</p>"
    items = []
    for run in reversed(runs):
        company = escape(run['case'].get('company', 'sin empresa'))
        priority = escape(run['report'].get('priority', 'n/a'))
        source = escape(run.get('source', 'unknown'))
        created_at = escape(run.get('created_at', ''))
        items.append(f"<li><strong>{company}</strong> · prioridad {priority} · {source} · <code>{created_at}</code></li>")
    return "<ul>" + "".join(items) + "</ul>"


def _render_report(report: dict | None, case: dict | None = None, report_title: str | None = None, orchestration: dict | None = None, audience: str = "commercial", views: dict | None = None) -> str:
    if not report:
        return f"""
        <section class=\"card\">
          <h2>Resultado</h2>
          <p>Completá el formulario para generar una lectura accionable del caso.</p>
          <h3>Últimas corridas</h3>
          {_render_recent_runs()}
        </section>
        """

    positives = "".join(f"<li>{escape(item)}</li>" for item in report["signals_positive"])
    risks = "".join(f"<li>{escape(item)}</li>" for item in report["signals_risk"])
    steps = "".join(f"<li>{escape(item)}</li>" for item in report["next_steps"])
    breakdown = "".join(f"<li>{escape(item)}</li>" for item in report["score_breakdown"])
    export_json = escape(json.dumps(report, ensure_ascii=False, indent=2))
    source_label = escape(report.get("source_label", case.get("source_label", "Carga manual") if case else "Carga manual"))
    llm_html = ""
    if report.get("llm_provider"):
        model = escape(report.get("llm_model", ""))
        provider = escape(report.get("llm_provider", ""))
        llm_html = f"<p><strong>Narrativa LLM:</strong> {provider} · <code>{model}</code></p>"

    title_html = f'<p class="muted">{escape(report_title)}</p>' if report_title else ''
    selected_view = (views or {}).get(audience, {})
    audience_switch_html = ""
    audience_panel_html = ""
    if report_title == "Informe general del lead" and views:
        audience_switch_html = (
            "<p>"
            "<span class='chip'>Vista Comercial</span> "
            "<span class='chip'>Vista Directiva</span>"
            "</p>"
        )
        if audience == "executive":
            source_items = "".join(
                f"<li><strong>{escape(item['source_type'])} · {escape(item['label'])}</strong><br><span class='muted'>{escape(item['summary'])}</span></li>"
                for item in selected_view.get("source_overview", [])
            )
            audience_panel_html = (
                f"<h3>{escape(selected_view.get('title', 'Vista Directiva'))}</h3>"
                f"<p><strong>Resumen ejecutivo:</strong> {escape(selected_view.get('headline', ''))}</p>"
                f"<p><strong>Decisión sugerida:</strong> {escape(selected_view.get('decision_note', ''))}</p>"
                f"<h4>Señales consolidadas</h4><ul>{source_items}</ul>"
            )
        else:
            step_items = "".join(f"<li>{escape(item)}</li>" for item in selected_view.get("next_steps", []))
            priority_items = "".join(
                f"<li><strong>{escape(item['source_type'])} · {escape(item['label'])}</strong> · prioridad {escape(item['priority'])}</li>"
                for item in selected_view.get("source_priorities", [])
            )
            audience_panel_html = (
                f"<h3>{escape(selected_view.get('title', 'Vista Comercial'))}</h3>"
                f"<p><strong>Foco operativo:</strong> {escape(selected_view.get('focus', ''))}</p>"
                f"<h4>Prioridades por fuente</h4><ul>{priority_items}</ul>"
                f"<h4>Próximos pasos operativos</h4><ul>{step_items}</ul>"
            )

    orchestration_html = ""
    if orchestration:
        items = []
        for item in orchestration.get("source_reports", []):
            source = item["source"]
            source_report = item["report"]
            items.append(
                f"<li><strong>{escape(source['source_type'])} · {escape(source['label'])}</strong>"
                f" · prioridad {escape(source_report['priority'])}"
                f"<br><span class='muted'>{escape(source_report['summary'])}</span></li>"
            )
        backend = escape(orchestration.get("orchestration_backend", "linear"))
        orchestration_html = (
            f"<h3>Orquestación de fuentes</h3><p class='muted'>backend: <code>{backend}</code></p>"
            + ("<ul>" + "".join(items) + "</ul>" if items else "<p class='muted'>Sin fuentes disponibles.</p>")
        )

    return f"""
    <section class=\"card\">
      <h2>Resultado</h2>
      {title_html}
      {audience_switch_html}
      <p><strong>Origen:</strong> {source_label}</p>
      {llm_html}
      <p><strong>Resumen:</strong> {escape(report['summary'])}</p>
      <p><strong>Prioridad:</strong> {escape(report['priority'])}</p>
      <p><strong>Tipo de caso:</strong> <code>{escape(report['case_type'])}</code></p>
      <p><strong>Confianza:</strong> {escape(report['confidence'])}</p>
      <p><strong>Score total:</strong> {report['score_total']}</p>
      <p><strong>Rationale:</strong> {escape(report['rationale'])}</p>
      <h3>Breakdown</h3>
      <ul>{breakdown}</ul>
      <h3>Señales positivas</h3>
      <ul>{positives}</ul>
      <h3>Riesgos</h3>
      <ul>{risks}</ul>
      <h3>Próximos pasos</h3>
      <ul>{steps}</ul>
      <h3>Export JSON</h3>
      <pre>{export_json}</pre>
      {audience_panel_html}
      {orchestration_html}
      <h3>Últimas corridas</h3>
      {_render_recent_runs()}
    </section>
    """


def app(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET").upper()
    path = environ.get("PATH_INFO", "/")
    if path == "/health":
        payload = b'{"status":"ok"}'
        start_response("200 OK", [("Content-Type", "application/json; charset=utf-8"), ("Content-Length", str(len(payload)))])
        return [payload]

    query = parse_qs(environ.get("QUERY_STRING", ""))
    selected_example = query.get("example", [None])[0]
    selected_brevo_deal = query.get("brevo_deal", [None])[0]
    selected_curated_source = query.get("curated_source", [None])[0]
    selected_lead_id = query.get("lead_id", [None])[0]
    selected_source_id = query.get("source_id", [None])[0]
    selected_view = query.get("view", [None])[0]
    selected_audience = query.get("audience", ["commercial"])[0] or "commercial"

    case = _load_example_case(selected_example)
    if selected_lead_id:
        case = load_demo_case(selected_lead_id, selected_source_id) or case
    if selected_brevo_deal:
        case = load_brevo_case(selected_brevo_deal) or case
    if selected_curated_source:
        case = load_curated_case(selected_curated_source) or case
    report = None
    report_title = None
    orchestration = None
    report_views = None

    if method == "GET" and selected_view == "report" and case:
        if selected_lead_id and not selected_source_id:
            report_views = build_view_models_for_lead(selected_lead_id)
            orchestration = report_views["orchestration"] if report_views else orchestrate_demo_lead_reports(selected_lead_id)
            if orchestration:
                case = orchestration["consolidated_case"]
                report = orchestration["consolidated_report"]
            else:
                report = analyze_case(case)
        else:
            report = analyze_case(case)
        report["source_kind"] = case.get("source_kind", "manual")
        report["source_label"] = case.get("source_label", "Carga manual")
        report_title = "Informe por fuente" if selected_source_id else "Informe general del lead"

    if method == "POST":
        length = int(environ.get("CONTENT_LENGTH") or 0)
        body = environ["wsgi.input"].read(length).decode("utf-8")
        form = parse_qs(body)
        case = _build_case(form)
        report = analyze_case(case)
        report["source_kind"] = case.get("source_kind", "manual")
        report["source_label"] = case.get("source_label", "Carga manual")
        source = case.get("source_label") or case.get("source_kind") or "web"
        append_run(DEFAULT_RUNS_PATH, case=case, report=report, source=source)
        response_format = form.get("response_format", ["html"])[0]
        if response_format == "json":
            payload = json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8")
            start_response("200 OK", [("Content-Type", "application/json; charset=utf-8"), ("Content-Length", str(len(payload)))])
            return [payload]

    html = HTML_TEMPLATE.format(
        content=_render_crm_demo(selected_lead_id, selected_source_id, selected_view)
        + _render_form(
            case,
            selected_example=selected_example,
            selected_brevo_deal=selected_brevo_deal,
            selected_curated_source=selected_curated_source,
        )
        + _render_report(report, case, report_title, orchestration, selected_audience, report_views["views"] if report_views else None)
    )
    payload = html.encode("utf-8")
    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(payload)))])
    return [payload]


def serve(host: str = "127.0.0.1", port: int = 8008):
    with make_server(host, port, app) as httpd:
        print(f"Radar Comercial web disponible en http://{host}:{port}")
        httpd.serve_forever()
