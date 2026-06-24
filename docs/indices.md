# Índices estratégicos (SPEC-01)

Documento de diseño y **evidencia** de los índices agregados a la base de datos,
adicionales a los que PostgreSQL crea por defecto.

## 1. Punto de partida: qué indexa PostgreSQL por defecto

PostgreSQL crea índices automáticamente **solo** para:

- **Claves primarias** (`PRIMARY KEY`).
- **Restricciones `UNIQUE`** (por eso `products.sku`, `clients.document_number`,
  `clients.email`, `users.email`, etc. **ya están indexadas**; no hay que volver a hacerlo).

> ⚠️ **PostgreSQL NO indexa las claves foráneas (FK) automáticamente.** Esto es clave:
> muchas consultas de la app filtran o hacen JOIN por columnas FK que, sin índice,
> obligan a un *Sequential Scan* (recorrer toda la tabla).

Los índices de esta spec atacan justamente esos huecos, guiados por las consultas
reales del punto de venta.

## 2. Índices diseñados

Declarados en los modelos SQLAlchemy con `Index()` en `__table_args__` y creados con
la migración Alembic `e142a1eddeff_indices_estrategicos_spec_01`.

| # | Índice | Tabla · Columnas | Tipo | Justificación |
|---|---|---|---|---|
| 1 | `ix_products_barcode` | `products(barcode)` | B-tree | Escaneo de código de barra: operación más frecuente del POS. `barcode` no es UNIQUE. |
| 2 | `ix_sale_details_sale` | `sale_details(sale_id)` | B-tree (FK) | Cargar los renglones de cada venta. FK sin índice. |
| 3 | `ix_sale_details_product` | `sale_details(product_id)` | B-tree (FK) | Historial / "más vendidos" por producto. FK sin índice. |
| 4 | `ix_sales_branch_created` | `sales(branch_id, created_at)` | Compuesto | Ventas de una sucursal por rango de fechas (reporte estrella). |
| 5 | `ix_sales_client` | `sales(client_id)` | B-tree (FK) | Historial / cuenta corriente de un cliente. FK sin índice. |
| 6 | `ix_inventory_movements_product_created` | `inventory_movements(product_id, created_at)` | Compuesto | Kardex: trazabilidad de stock de un producto en el tiempo. |
| 7 | `ix_branch_product_low_stock` | `branch_product(branch_id) WHERE stock <= alert_stock` | **Parcial** | Alerta de stock bajo por sucursal. Indexa solo las filas en alerta. |
| 8 | `ix_products_name_pattern` | `products(name) varchar_pattern_ops` | B-tree (opclass) | Autocompletado por nombre (`LIKE 'prefijo%'`). |

### Notas de diseño

- **Índice compuesto (4 y 6):** el orden de las columnas importa. `(branch_id, created_at)`
  permite filtrar primero por sucursal y luego acotar por fecha usando el mismo índice.
- **Índice parcial (7):** al incluir `WHERE stock <= alert_stock`, el índice solo contiene
  las filas que están en alerta → mucho más chico y rápido para la consulta de reposición.
- **Operator class (8):** `varchar_pattern_ops` es lo que permite que un `LIKE 'texto%'`
  use el índice (sin esa opclass, dependiendo del locale, el `LIKE` no lo aprovecharía).

## 3. Cómo reproducir el benchmark

```bash
docker compose up -d
alembic upgrade head
python scripts/seed_benchmark.py          # carga datos de volumen
python scripts/benchmark_indices.py       # EXPLAIN ANALYZE de las 8 consultas
```

Para comparar antes/después: correr el benchmark con la migración de índices
**deshecha** (`alembic downgrade -1`) y luego **aplicada** (`alembic upgrade head`).
Volumen sembrado: 10.000 productos, 2.000 clientes, 3 sucursales, 30.000 `branch_product`,
50.000 ventas, 150.000 detalles, 30.000 movimientos de inventario.

## 4. Resultados (EXPLAIN ANALYZE)

`Execution Time` reportado por PostgreSQL, mismo dataset, antes y después de los índices:

| # | Consulta | Antes | Después | Mejora | Plan antes → después |
|---|---|---:|---:|---:|---|
| RF-1 | `products.barcode = ?` | 1.46 ms | 0.06 ms | ~23× | Seq Scan → Index Scan |
| RF-2 | `sale_details.sale_id = ?` | 18.18 ms | 0.05 ms | ~350× | Seq Scan → Bitmap Index Scan |
| RF-3 | `sale_details.product_id = ?` | 16.26 ms | 0.12 ms | ~133× | Seq Scan → Bitmap Index Scan |
| RF-4 | `sales` sucursal + fecha | 8.66 ms | 1.69 ms | ~5× | Seq Scan → Bitmap Index Scan |
| RF-5 | `sales.client_id = ?` | 5.77 ms | 0.10 ms | ~56× | Seq Scan → Bitmap Index Scan |
| RF-6 | `inventory_movements` kardex | 4.62 ms | 0.04 ms | ~113× | Seq Scan → Index Scan |
| RF-7 | `branch_product` stock bajo | 6.68 ms | 0.75 ms | ~9× | Seq Scan → Bitmap Index Scan (parcial) |
| RF-8 | `products.name LIKE 'p%'` | 2.04 ms | 0.14 ms | ~14× | Seq Scan → Bitmap Index Scan |

Las salidas completas de `EXPLAIN ANALYZE` están en
[`docs/benchmark/explain_antes.txt`](benchmark/explain_antes.txt) y
[`docs/benchmark/explain_despues.txt`](benchmark/explain_despues.txt).

### Ejemplo (RF-2, el de mayor impacto)

**Antes** — recorre las 150.000 filas:
```
Seq Scan on sale_details  (cost=0.00..3875.00 rows=3 ...) (actual time=... rows=3)
  Filter: (sale_id = '...')
  Rows Removed by Filter: 149997
Execution Time: 18.183 ms
```

**Después** — va directo por el índice:
```
Bitmap Heap Scan on sale_details ...
  ->  Bitmap Index Scan on ix_sale_details_sale  (cost=0.00..4.44 rows=3 ...) (actual ... rows=3)
Execution Time: 0.052 ms
```

## 5. Trade-offs (para la defensa)

- Los índices **aceleran las lecturas** pero **penalizan las escrituras** (cada
  INSERT/UPDATE debe mantener también el índice) y **ocupan espacio en disco**.
- Por eso no se indexa "todo": se eligieron columnas con consultas frecuentes y
  selectivas. El índice **parcial** y los **compuestos** son ejemplos de indexar
  exactamente lo que la aplicación consulta, manteniendo el costo bajo.
- `EXPLAIN ANALYZE` permite **verificar** que el planner efectivamente usa el índice
  (Index Scan / Bitmap Index Scan) en lugar de un Seq Scan.
