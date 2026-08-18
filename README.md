# Radar Comercial

Estado: `mvp`

Base técnica inicial del producto `Radar Comercial` para convertir contexto
comercial disperso en una lectura accionable con prioridades, riesgos y próximos
pasos visibles.

## Stack inicial

- Python 3.12.
- Paquete local `src/radar_comercial`.
- Validación mínima con `unittest`.
- Documentación técnica local en `docs/`.

## Documentación

- `docs/architecture.md`: frontera técnica inicial del MVP.
- `docs/issue-tracker.md`: trazabilidad técnica mínima del repo.

La documentación de negocio vive en YouTrack KB: `PRD / Productos / Radar
Comercial`.

## Slice funcional actual

El repo ya incluye un primer slice funcional del MVP:

- `radar_comercial.models.CommercialCase`: contrato explícito del input comercial.
- `radar_comercial.models.RadarReport`: contrato explícito del output del radar.
- `radar_comercial.analysis.analyze_commercial_case`: motor principal sobre el
  modelo de dominio.
- `radar_comercial.analysis.analyze_case`: wrapper compatible con dicts para el
  slice inicial.
- `radar_comercial.presenter.render_radar_report_markdown`: presentación del
  output tipado.
- `radar_comercial.web.app`: mini interfaz web local con formulario, carga de
  ejemplos, export JSON y resultado.
- `radar_comercial.web_cli`: servidor local para demo navegable.
- persistencia local de corridas en `data/runs.jsonl` vía
  `radar_comercial.run_store`.
- scoring explicable con `confidence`, `score_total`, `score_breakdown`,
  `rationale` y bandas `baja` / `media` / `alta` / `critica`.
- `python -m radar_comercial.demo_cli`: recibe un caso JSON por `stdin` o
  `--input`, puede persistir historial y emitir Markdown o JSON.
- deploy activo en Coolify (Products / production):
  `http://yksccckkgksckggkw0cggg88.76.13.170.240.sslip.io`.

## Requisitos locales

- Python 3.12 o superior.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Validación inicial

```bash
python -m compileall src
python -m unittest discover -s tests
```

## Smoke demoable

```bash
cat example.json | PYTHONPATH=src python3 -m radar_comercial.demo_cli
PYTHONPATH=src python3 -m radar_comercial.demo_cli --input examples/high-intent-case.json
PYTHONPATH=src python3 -m radar_comercial.demo_cli --input examples/outbound-cold-case.json --format json
PYTHONPATH=src python3 -m radar_comercial.demo_cli --input examples/enterprise-urgent-case.json --format json
PYTHONPATH=src python3 -m radar_comercial.web_cli --host 127.0.0.1 --port 8008
```

## Casos demo incluidos

- `examples/high-intent-case.json`: inbound caliente con score alto.
- `examples/outbound-cold-case.json`: outbound frío con prioridad media.
- `examples/enterprise-urgent-case.json`: inbound urgente con prioridad crítica.

## Límites del MVP actual

- No incluye integración obligatoria con `Aira`.
- No usa infraestructura compartida de otros productos.
- La persistencia productiva sigue siendo básica (`runs.jsonl`) y no está endurecida.
- No reemplaza el proceso comercial de `SP`.
