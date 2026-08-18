# AGENTS.md

## Proposito

Este repositorio contiene la verdad tecnica de `Radar Comercial`, producto de
`PRD` para transformar contexto comercial disperso en una lectura accionable,
visible y reusable para discovery, priorizacion y siguientes pasos.

La documentacion de negocio vive en YouTrack KB bajo `PRD / Productos / Radar
Comercial`. Este repositorio no debe depender de rutas locales de `LBIA_YT`.

## Punto de entrada

Antes de modificar codigo o documentacion tecnica:

1. Leer `README.md`.
2. Leer `docs/architecture.md`.
3. Leer el documento tecnico especifico de la tarea cuando exista.
4. Consultar YouTrack KB empezando por `LBO` y luego `PRD` si falta contexto de
   negocio.

## Reglas tecnicas

- No mezclar la base funcional del producto con infraestructura compartida de
  otros productos.
- Si el producto necesita persistencia o runtime, deben ser propios del
  producto.
- Mantener separadas verdad tecnica del repo y reglas de negocio de la KB.
- No prometer integracion obligatoria con `Aira` mientras siga documentada como
  capacidad futura.
- La demo inicial debe poder ejecutarse y entenderse sin depender del proceso
  comercial completo de `SP`.

## Acciones restringidas

Requieren aprobacion explicita:

- Push directo a `main`.
- Merge a `main`.
- Deploy productivo.
- Uso de datos sensibles reales.
- Cambios de promesa comercial fuera de la KB del producto.
