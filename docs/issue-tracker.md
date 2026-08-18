# Seguimiento técnico mínimo de `prd-radar-comercial`

| Issue | Estado | Alcance técnico |
| --- | --- | --- |
| [PRD-4](https://lbia.youtrack.cloud/issue/PRD-4) | In Progress | Bootstrap local del repo nuevo, frontera técnica inicial y primer slice funcional demoable. |
| [PRD-6](https://lbia.youtrack.cloud/issue/PRD-6) | En progreso local | El flujo E2E ya cubre input mínimo -> análisis -> reporte Markdown/JSON o interfaz web -> próximos pasos. |
| [PRD-9](https://lbia.youtrack.cloud/issue/PRD-9) | En progreso local | El motor ya incorpora bandas `baja` / `media` / `alta` / `critica`, `confidence`, `score_total`, `score_breakdown`, `rationale` y reglas por `case_type`. |
| [PRD-12](https://lbia.youtrack.cloud/issue/PRD-12) | En progreso local | Contrato explícito del input comercial implementado en `radar_comercial.models.CommercialCase`, incluyendo `case_type`. |
| [PRD-13](https://lbia.youtrack.cloud/issue/PRD-13) | En progreso local | La salida visible ya existe como `RadarReport` + reporte Markdown/JSON + interfaz web navegable, publicada en Coolify, ahora con selector de deals reales Brevo y fuentes curadas demoables. |
| [PRD-14](https://lbia.youtrack.cloud/issue/PRD-14) | En progreso local | Entidades de dominio `CommercialCase` y `RadarReport` ya estructuran el corazón del MVP. |
| [PRD-15](https://lbia.youtrack.cloud/issue/PRD-15) | En progreso local | La superficie mínima actual incluye CLI local por `stdin` o `--input`, interfaz web en Coolify (`sslip.io`), selector de ejemplos, import CRM Brevo, fuentes curadas e historial reciente. |
| [PRD-16](https://lbia.youtrack.cloud/issue/PRD-16) | En progreso local | Tests unitarios + smoke local cubren el slice actual, incluyendo import real desde Brevo y carga demoable de resúmenes curados. |
