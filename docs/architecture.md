# Arquitectura inicial de Radar Comercial

## Propósito

Definir la frontera técnica inicial del repo `prd-radar-comercial` para que el
producto tenga una base propia y no dependa de infraestructura compartida ni de
otros repositorios para arrancar.

## Objetivo del MVP

El MVP técnico debe poder recibir contexto comercial mínimo y producir una
lectura accionable con:

- resumen del caso;
- señales relevantes;
- prioridad o foco sugerido;
- próximos pasos.

## Fronteras

### Vive en este repo

- implementación técnica del producto;
- documentación técnica;
- validaciones locales;
- futura lógica de procesamiento del radar;
- futuras interfaces demoables del producto.

### No vive en este repo

- reglas de negocio estables del producto, que viven en `PRD`;
- proceso comercial de uso y venta, que vive en `SP`;
- infraestructura compartida de otros productos;
- backlog operativo en forma de documentación técnica estable.

## Componentes iniciales

- `src/radar_comercial/analysis.py`: núcleo de lectura comercial del caso.
- `src/radar_comercial/presenter.py`: presentación Markdown del radar.
- `src/radar_comercial/demo_cli.py`: entrada CLI para smoke/demo local y persistencia opcional.
- `src/radar_comercial/web.py`: app WSGI local con CRM demo interno (leads,
  ficha de lead, informes general/por fuente y navegación hacia el radar),
  formulario, ejemplos, import de deals reales desde Brevo, fuentes curadas
  simuladas y export JSON.
- `src/radar_comercial/crm_demo.py`: carga y helpers del mini CRM demo
  interno para leads y fuentes curadas por lead.
- `examples/crm-demo-dataset.json`: dataset versionado del CRM demo interno.
- `src/radar_comercial/llm_provider.py`: providers configurables para
  enriquecer `summary`/`rationale` con fallback seguro.
- `src/radar_comercial/report_orchestration.py`: orquestación de informes por
  fuente y consolidación general, con backend evolutivo hacia LangGraph.
- `src/radar_comercial/run_store.py`: persistencia local de corridas en JSONL.
- `examples/`: casos de ejemplo repetibles para demo y validación manual.
- `data/runs.jsonl`: historial local de corridas del radar.
- `--format json`: salida estructurada para inspección técnica/demo más operable.
- `tests/`: validaciones del scaffold y del slice funcional inicial.
- `docs/`: verdad técnica inicial del repo.

## Estado funcional actual

El repo ya tiene una primera cadena completa local:

1. `CommercialCase.from_dict(...)` normaliza el input comercial mínimo.
2. `analyze_commercial_case(...)` produce un `RadarReport` tipado.
3. El motor agrega `priority`, `confidence`, `score_total`, `score_breakdown`,
   `rationale` y bandas `baja` / `media` / `alta` / `critica`.
4. `render_radar_report_markdown(...)` transforma el reporte en un artefacto
   visible para demo.
5. `demo_cli` permite analizar casos por `stdin`/`--input` y persiste corridas
   locales en `data/runs.jsonl`.
6. `web.py` expone una interfaz con CRM demo interno, selector de ejemplos,
   import de deals reales desde Brevo, fuentes curadas para Meet / WhatsApp /
   llamadas, export JSON, historial reciente e informes navegables por lead o
   por fuente (`view=report`).
7. `llm_provider.py` permite enriquecer `summary` y `rationale` con providers
   OpenAI-compatible configurados por entorno, con fallback silencioso al motor
   rule-based cuando falta config o la llamada falla.
8. `report_orchestration.py` ejecuta el paso fuente por fuente y luego la
   consolidación general del lead, dejando un backend actual `linear` listo para
   evolucionar a LangGraph cuando se incorpore la dependencia real.

## Evolución esperada

Las siguientes capas podrán agregarse de forma progresiva:

- enriquecimiento del modelo de inputs del radar;
- scoring comercial más fino y explicable;
- generación de outputs demoables más ricos;
- persistencia propia si el producto la requiere;
- superficies de uso y runtime propios.
- CRM demo interno con leads y fuentes propias de la app.
- integración CRM visible con lectura/import de deals reales.
- ingesta futura desde fuentes conversacionales reales (Meet, WhatsApp, llamadas).

## Restricciones

- no depender de bases funcionales de LBIA;
- no mezclar la demo con infraestructura compartida;
- no acoplar el MVP a `Aira` en esta etapa;
- no duplicar en el repo reglas de negocio que pertenecen a la KB.
