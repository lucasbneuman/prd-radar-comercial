from __future__ import annotations

import json
from html import escape
from pathlib import Path
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from radar_comercial.analysis import analyze_case
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
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }}
    .card {{ background: #111827; padding: 1rem; border-radius: 12px; border: 1px solid #334155; }}
    textarea, input, select {{ width: 100%; margin-top: .35rem; margin-bottom: .75rem; padding: .65rem; border-radius: 8px; border: 1px solid #475569; background: #0f172a; color: #e2e8f0; }}
    button {{ background: #22c55e; color: #052e16; border: 0; padding: .75rem 1rem; border-radius: 8px; font-weight: bold; cursor: pointer; }}
    .secondary {{ background: #38bdf8; color: #082f49; }}
    ul {{ padding-left: 1.2rem; }}
    code {{ background: #0f172a; padding: .1rem .35rem; border-radius: 6px; }}
    a {{ color: #7dd3fc; }}
  </style>
</head>
<body>
  <h1>Radar Comercial</h1>
  <p>Demo local para convertir contexto comercial mínimo en una lectura accionable.</p>
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
    return json.loads(path.read_text(encoding="utf-8"))


def _build_case(form: dict[str, list[str]]) -> dict:
    return {
        "company": form.get("company", [""])[0].strip(),
        "objective": form.get("objective", [""])[0].strip(),
        "pain_points": _split_lines(form.get("pain_points", [""])[0]),
        "signals": _split_lines(form.get("signals", [""])[0]),
        "risks": _split_lines(form.get("risks", [""])[0]),
        "case_type": form.get("case_type", ["generic"])[0].strip() or "generic",
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


def _render_form(case: dict | None = None, *, selected_example: str | None = None) -> str:
    case = case or {"company": "", "objective": "", "pain_points": [], "signals": [], "risks": [], "case_type": "generic"}
    return f"""
    <section class=\"card\">
      <h2>Input comercial</h2>
      <form method=\"get\">
        <label>Ejemplo
          <select name=\"example\">{''.join(_render_example_options(selected_example))}</select>
        </label>
        <button class=\"secondary\" type=\"submit\">Cargar ejemplo</button>
      </form>
      <hr>
      <form method=\"post\">
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


def _render_report(report: dict | None, case: dict | None = None) -> str:
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

    return f"""
    <section class=\"card\">
      <h2>Resultado</h2>
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
    case = _load_example_case(selected_example)
    report = None

    if method == "POST":
        length = int(environ.get("CONTENT_LENGTH") or 0)
        body = environ["wsgi.input"].read(length).decode("utf-8")
        form = parse_qs(body)
        case = _build_case(form)
        report = analyze_case(case)
        append_run(DEFAULT_RUNS_PATH, case=case, report=report, source="web")
        response_format = form.get("response_format", ["html"])[0]
        if response_format == "json":
            payload = json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8")
            start_response("200 OK", [("Content-Type", "application/json; charset=utf-8"), ("Content-Length", str(len(payload)))])
            return [payload]

    html = HTML_TEMPLATE.format(content=_render_form(case, selected_example=selected_example) + _render_report(report, case))
    payload = html.encode("utf-8")
    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(payload)))])
    return [payload]


def serve(host: str = "127.0.0.1", port: int = 8008):
    with make_server(host, port, app) as httpd:
        print(f"Radar Comercial web disponible en http://{host}:{port}")
        httpd.serve_forever()
