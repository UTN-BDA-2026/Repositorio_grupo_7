# SPEC-04 — NoSQL (log de eventos combinado con la BD relacional)

| Campo | Valor |
|---|---|
| **Owner** | Federico Sosa |
| **Rama** | `feat/nosql-logging` |
| **Estado** | Borrador |
| **Tema de la consigna** | NoSQL (combinando con BD relacional; explicar la decisión) |
| **Dependencias** | **Ninguna** (datastore aparte; no toca el esquema Postgres ni los servicios existentes) |
| **Fecha** | 2026-06-24 |

---

## 1. Contexto

La consigna permite combinar NoSQL con la base relacional, justificando la decisión.
El sistema de ventas genera **eventos** (venta confirmada, ajuste de stock, apertura/cierre
de caja) que tienen forma variable y de los que conviene tener un **registro histórico
de auditoría**. Forzar estos eventos al modelo relacional rígido es incómodo; un store
documental encaja naturalmente.

## 2. Objetivo

Integrar una base **NoSQL documental (MongoDB)** que conviva con PostgreSQL, usada como
**bitácora de eventos / auditoría** del sistema, y dejar **documentada la justificación**
de por qué NoSQL para este caso y no la relacional.

## 3. Alcance (in scope)

- Servicio de **MongoDB** agregado a `docker-compose.yml` (contenedor aparte).
- Módulo `nosql/` con conexión vía `pymongo`, leyendo config desde `.env`.
- Función para **registrar un evento** (documento con tipo, payload, timestamp).
- Un punto de integración: registrar un evento al confirmar una venta (llamada desde
  `database/transactions.py`, **sin romper** la transacción relacional si Mongo falla).
- Documento `docs/nosql.md` con la justificación de la decisión.

## 4. Fuera de alcance (out of scope)

- Migrar tablas relacionales a NoSQL.
- Reportes/analytics sobre Mongo (solo escritura de eventos + una lectura de ejemplo).
- Réplicas/sharding.

## 5. Requisitos funcionales

| RF | Descripción |
|---|---|
| RF-1 | `docker-compose.yml` levanta un servicio `mongo` con puerto y credenciales desde `.env`. |
| RF-2 | `nosql/client.py` provee la conexión a Mongo leyendo `MONGO_URI`/`MONGO_DB` del `.env`. |
| RF-3 | `nosql/events.py` expone `log_event(event_type: str, payload: dict)` que inserta un documento `{type, payload, created_at}`. |
| RF-4 | Al confirmar una venta, se registra un evento `sale_confirmed` con el `sale_id` y el total. |
| RF-5 | Si Mongo no está disponible, la venta **no se rompe** (el log es best-effort, se captura el error). |
| RF-6 | `.env.example` documenta las variables de Mongo. |

## 6. Diseño técnico

### 6.1 Docker

Agregar al `docker-compose.yml` un servicio `mongo` (imagen `mongo:7`), con volumen
propio y puerto mapeado (p. ej. `27018:27017`), credenciales desde `.env`.

### 6.2 Módulo NoSQL (forma de referencia, adaptar)

```python
# nosql/client.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()
_client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27018"))
db = _client[os.getenv("MONGO_DB", "dba_final_logs")]

# nosql/events.py
from datetime import datetime, timezone
from nosql.client import db
def log_event(event_type: str, payload: dict) -> None:
    db.events.insert_one({"type": event_type, "payload": payload,
                          "created_at": datetime.now(timezone.utc)})
```

### 6.3 Integración best-effort

En `process_sale_transaction` (en `transactions.py`), tras el commit exitoso:

```python
try:
    log_event("sale_confirmed", {"sale_id": str(sale_id), "total": str(sale_data["total_amount"])})
except Exception as e:
    print(f"[warn] no se pudo registrar evento NoSQL: {e}")  # no interrumpe la venta
```

> Importante: el log NoSQL va **después** del commit relacional y **no** dentro de la
> transacción SQL, para no acoplar la atomicidad de la venta a Mongo.

### 6.4 Dependencia nueva

Agregar a `requirements.txt`: `pymongo` (fijar versión).

## 7. Entregables

- `docker-compose.yml` con servicio `mongo`.
- `nosql/__init__.py`, `nosql/client.py`, `nosql/events.py`.
- Hook de `log_event` en `database/transactions.py`.
- `.env.example` + `requirements.txt` actualizados.
- `docs/nosql.md` con la **justificación de la decisión**.

## 8. Criterios de aceptación (Definition of Done)

- [ ] `docker compose up -d` levanta Postgres **y** Mongo.
- [ ] Confirmar una venta inserta un documento en la colección `events` de Mongo (verificable con `mongosh`).
- [ ] Si Mongo está caído, la venta igual se confirma (no se rompe).
- [ ] `docs/nosql.md` justifica por qué NoSQL para eventos y por qué se combina con la relacional. PR aprobado.

## 9. Plan de verificación

1. `docker compose up -d` (Postgres + Mongo).
2. Ejecutar una venta de prueba (script o desde la app).
3. `mongosh` → `db.events.find()` muestra el evento.
4. Detener Mongo y repetir la venta → la venta se confirma igual.

## 10. Plan de commits / PR

```
feat: agregar servicio mongo a docker-compose
feat: cliente y modulo de eventos NoSQL con pymongo
feat: registrar evento de venta confirmada (best-effort)
docs: justificar la decision de usar NoSQL combinado con relacional
```
PR: **"feat: NoSQL — log de eventos"** → base `main`.

## 11. Notas para la defensa

- **Por qué NoSQL acá**: eventos de esquema flexible, alto volumen de escritura, sin JOINs,
  ideal para un store documental; vs. el costo de modelarlos en tablas rígidas.
- **Por qué combinado** (poliglot persistence): la fuente de verdad transaccional sigue
  siendo PostgreSQL (ACID); Mongo es la bitácora/analítica, desacoplada.
- Por qué el log es **best-effort** y va fuera de la transacción SQL (no comprometer la atomicidad de la venta).
- Diferencias documental vs relacional (esquema flexible, sin joins, consistencia eventual).
