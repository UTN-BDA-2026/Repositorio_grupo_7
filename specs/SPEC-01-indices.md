# SPEC-01 — Índices estratégicos

| Campo | Valor |
|---|---|
| **Owner** | Branko Almeira |
| **Rama** | `feat/indexes` |
| **Estado** | Borrador |
| **Tema de la consigna** | Índices (diseñados, distintos a los creados por defecto) |
| **Dependencias** | **Ninguna** (es la única spec que modifica el esquema) |
| **Fecha** | 2026-06-24 |

---

## 1. Contexto

El esquema actual (`docs/bd_struct.sql`) solo tiene los índices que PostgreSQL crea
**automáticamente**: los de las claves primarias (`PRIMARY KEY`) y los de las
restricciones `UNIQUE`. Dos hechos importantes:

- **Ya están indexadas por `UNIQUE`** (no hay que volver a indexarlas):
  `products.sku`, `clients.document_number` (el "DNI"), `clients.email`,
  `users.email`, `branch_product (branch_id, product_id)`, etc.
- **PostgreSQL NO indexa las claves foráneas automáticamente.** Solo indexa PK y
  UNIQUE. Por eso decenas de FK de este esquema (`sale_details.sale_id`,
  `sales.client_id`, etc.) hoy provocan *Sequential Scans* en los JOINs.

Esta spec diseña índices **adicionales**, justificados por las consultas reales de
la aplicación, y **mide su impacto** con `EXPLAIN ANALYZE`.

## 2. Objetivo

Diseñar, implementar (vía SQLAlchemy + Alembic) y **demostrar con evidencia** un
conjunto de índices no triviales que mejoren las consultas frecuentes del punto de
venta, dejando documentada la justificación de cada uno.

## 3. Alcance (in scope)

- Declarar los índices en los modelos SQLAlchemy con `Index()` dentro de `__table_args__`.
- Generar **una** migración Alembic (`alembic revision --autogenerate`).
- Un script auto-contenido que **genera datos de volumen** para poder medir
  (así esta spec no depende de ninguna otra).
- Capturar `EXPLAIN ANALYZE` **antes y después** de cada índice.
- Documentar todo en `docs/indices.md`.

## 4. Fuera de alcance (out of scope)

- Particionado de tablas (tema aparte).
- Tuning de configuración del motor (`work_mem`, etc.).
- Re-indexar columnas que ya tienen índice por PK/UNIQUE.

## 5. Requisitos funcionales

Implementar los **8 índices** siguientes. Cada uno con su justificación:

| RF | Tabla · Columna(s) | Tipo | Justificación (caso de uso) |
|---|---|---|---|
| RF-1 | `products (barcode)` | B-tree | Escaneo de código de barra: operación más frecuente del POS. `barcode` **no** es UNIQUE → hoy hace seq scan. |
| RF-2 | `sale_details (sale_id)` | B-tree (FK) | Cargar los renglones de cada venta (JOIN por ticket). FK sin índice. |
| RF-3 | `sale_details (product_id)` | B-tree (FK) | Historial de ventas y "más vendidos" por producto. FK sin índice. |
| RF-4 | `sales (branch_id, created_at)` | Compuesto | Reporte estrella: ventas de una sucursal por rango de fechas. |
| RF-5 | `sales (client_id)` | B-tree (FK) | Historial / cuenta corriente de un cliente. FK sin índice. |
| RF-6 | `inventory_movements (product_id, created_at)` | Compuesto | Kardex / trazabilidad de stock de un producto en el tiempo. |
| RF-7 | `branch_product (branch_id) WHERE stock <= alert_stock` | **Parcial** | Alerta de stock bajo por sucursal. Índice chico, solo filas en alerta. |
| RF-8 | `products (name varchar_pattern_ops)` | B-tree | Autocompletado por nombre en la UI (`name LIKE 'texto%'`). Sin extensiones. |

## 6. Diseño técnico

### 6.1 Declaración en modelos

Agregar `__table_args__` con `Index(...)` en cada modelo afectado. Ejemplo de forma
(NO copiar literal, adaptar nombres):

```python
from sqlalchemy import Index
# en Product:
__table_args__ = (
    Index("ix_products_barcode", "barcode"),
    Index("ix_products_name_pattern", "name", postgresql_ops={"name": "varchar_pattern_ops"}),
)
# en Sale:
__table_args__ = (
    Index("ix_sales_branch_created", "branch_id", "created_at"),
    Index("ix_sales_client", "client_id"),
)
# parcial en BranchProduct:
__table_args__ = (
    ...,  # conservar el UNIQUE existente
    Index("ix_branch_product_low_stock", "branch_id", postgresql_where=text("stock <= alert_stock")),
)
```

> ⚠️ `CashRegisterSession` ya tiene un `__table_args__` con un `CheckConstraint`:
> **no lo pises**, si agregás índices ahí, sumalos a la tupla existente.

### 6.2 Migración

```bash
alembic revision --autogenerate -m "feat: indices estrategicos"
# revisar el archivo generado en alembic/versions/ (deben aparecer create_index)
alembic upgrade head
```

### 6.3 Convención de nombres

`ix_<tabla>_<columnas>` (snake_case). Coherente y explícito para la defensa.

## 7. Entregables

- Modelos modificados en `database/models/` (Product, Sale, SaleDetail, InventoryMovement, BranchProduct).
- Migración nueva en `alembic/versions/`.
- `scripts/seed_benchmark.py` — genera datos de volumen (p. ej. 10k productos,
  50k ventas, 200k detalles) usando SQL/ORM. Auto-contenido.
- `docs/indices.md` — diseño + tabla de justificación + resultados `EXPLAIN ANALYZE`.

## 8. Criterios de aceptación (Definition of Done)

- [ ] Los 8 índices (RF-1..RF-8) creados y visibles en la BD (`\di` en psql).
- [ ] `alembic upgrade head` y `alembic downgrade -1` funcionan sin error.
- [ ] No se duplican índices ya existentes por PK/UNIQUE.
- [ ] `docs/indices.md` incluye, por cada consulta de prueba, el `EXPLAIN ANALYZE`
      **antes** (Seq Scan) y **después** (Index Scan / Bitmap Index Scan) con tiempos.
- [ ] PR abierto contra `main` y aprobado por el revisor.

## 9. Plan de verificación

1. Levantar BD: `docker compose up -d` y `alembic upgrade head`.
2. Correr `scripts/seed_benchmark.py` para cargar volumen.
3. Tomar `EXPLAIN ANALYZE` de cada consulta **antes** de aplicar la migración de índices.
4. Aplicar la migración de índices (`alembic upgrade head`).
5. Repetir los `EXPLAIN ANALYZE` y comparar. Guardar salidas en `docs/indices.md`.

Consultas de prueba sugeridas (una por índice), p. ej.:
```sql
EXPLAIN ANALYZE SELECT * FROM products WHERE barcode = '7791234567890';
EXPLAIN ANALYZE SELECT * FROM sales WHERE branch_id = '...' AND created_at >= '2026-01-01';
EXPLAIN ANALYZE SELECT * FROM branch_product WHERE branch_id='...' AND stock <= alert_stock;
EXPLAIN ANALYZE SELECT * FROM products WHERE name LIKE 'Coca%';
```

## 10. Plan de commits / PR

```
feat: agregar indices estrategicos en modelos SQLAlchemy
feat: migracion alembic para indices
chore: script de seed para benchmark de indices
docs: documentar diseño y benchmark de indices (EXPLAIN ANALYZE)
```
PR: **"feat: índices estratégicos"** → base `main`.

## 11. Notas para la defensa

Tenés que poder explicar:

- **Qué indexa Postgres por defecto** (PK, UNIQUE) y **qué NO** (las FK).
- Por qué un **índice compuesto** `(branch_id, created_at)` sirve para el filtro por
  sucursal + rango de fechas, y por qué **el orden de las columnas importa**.
- Qué es un **índice parcial** y por qué es ideal para "stock bajo" (indexa solo las
  filas que cumplen la condición → más chico y rápido).
- Por qué `varchar_pattern_ops` permite usar el índice en `LIKE 'prefijo%'`.
- Leer un `EXPLAIN ANALYZE`: diferenciar **Seq Scan** vs **Index Scan** y el costo/tiempo.
- El **trade-off**: los índices aceleran lecturas pero **penalizan escrituras** y ocupan espacio.
