# Justificación: NoSQL combinado con BD Relacional

## Decisión técnica

Se incorporó **MongoDB** como store documental para el registro de eventos de
auditoría del sistema de ventas, manteniendo **PostgreSQL** como base de datos
transaccional principal.

## Por qué NoSQL para eventos de auditoría

| Característica | Problema en SQL | Ventaja en MongoDB |
|---|---|---|
| Esquema flexible | Los eventos tienen forma variable (venta, ajuste de stock, apertura de caja). Modelarlos en tablas rígidas exige tablas separadas o columnas genéricas. | Un documento con `type`+`payload` admite cualquier estructura sin migraciones. |
| Volumen de escritura | Cada venta genera múltiples eventos. Insertar en tablas normalizadas con claves foráneas es más costoso. | Inserción directa en una colección, sin JOINs ni restricciones referenciales. |
| Consultas de auditoría | Las consultas históricas suelen recorrer muchas tablas. | Búsqueda sencilla por tipo, rango de fechas o contenido del payload. |

## Por qué combinado (Poliglot Persistence)

- **PostgreSQL** sigue siendo la fuente de verdad transaccional (ACID). Las ventas,
  stocks y relaciones deben ser atómicas, consistentes y duraderas.
- **MongoDB** actúa como bitácora desacoplada. Los eventos no forman parte de la
  lógica de negocio crítica; son datos históricos/analíticos.
- Se evita acoplar la atomicidad de la venta a la disponibilidad de Mongo: el log
  es **best-effort** y se ejecuta **después** del commit relacional.

## Diferencias clave: Documental vs Relacional

| Aspecto | Relacional (Postgres) | Documental (Mongo) |
|---|---|---|
| Esquema | Fijo, definido por tablas y tipos | Flexible, cada documento define su forma |
| Relaciones | JOINs entre tablas | Datos embebidos o referencias manuales |
| Consistencia | Fuerte (ACID) | Eventual (configurable) |
| Escalabilidad | Vertical (o read-replicas) | Horizontal nativa (sharding) |
| Caso de uso | Transacciones, datos estructurados | Logs, catálogos, sesiones, analítica |

## Conclusión

La combinación de ambos motores cubre el espectro completo del sistema:
PostgreSQL garantiza la integridad transaccional del negocio, mientras que MongoDB
absorbe la carga de escritura de eventos con flexibilidad de esquema y
simplicidad operativa.
