"""
Benchmark de índices (SPEC-01): corre EXPLAIN ANALYZE sobre las 8 consultas que
los índices buscan optimizar. Se ejecuta DOS veces:

  1. ANTES de aplicar la migración de índices  -> debería mostrar Seq Scan
  2. DESPUÉS de `alembic upgrade head`          -> debería mostrar Index Scan

Uso:
    python scripts/benchmark_indices.py
    python scripts/benchmark_indices.py > docs/_bench_antes.txt
"""
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


def conn():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5438"),
        dbname=os.getenv("DB_NAME", "dba_final"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "admin1234"),
        autocommit=True,
    )


def explain(cur, titulo, sql, params):
    print("\n" + "=" * 78)
    print(f"# {titulo}")
    print("-" * 78)
    print(sql.strip())
    cur.execute("EXPLAIN (ANALYZE, BUFFERS) " + sql, params)
    for row in cur.fetchall():
        print("   " + row[0])


def main():
    with conn() as c, c.cursor() as cur:
        # Valores de muestra reales tomados de los datos sembrados
        cur.execute("SELECT id FROM branches ORDER BY name LIMIT 1;")
        branch_id = cur.fetchone()[0]
        cur.execute("SELECT id FROM clients LIMIT 1;")
        client_id = cur.fetchone()[0]
        cur.execute("SELECT id FROM products LIMIT 1;")
        product_id = cur.fetchone()[0]
        cur.execute("SELECT sale_id FROM sale_details LIMIT 1;")
        sale_id = cur.fetchone()[0]
        # producto con un movimiento de inventario reciente (para que RF-6 no dé 0)
        cur.execute("SELECT product_id FROM inventory_movements ORDER BY created_at DESC LIMIT 1;")
        inv_product_id = cur.fetchone()[0]
        barcode = "779" + str(5000).rjust(10, "0")  # producto g=5000
        fecha = "2026-04-01"  # rango de los últimos ~3 meses

        explain(cur, "RF-1  products.barcode (escaneo de código de barra)",
                "SELECT * FROM products WHERE barcode = %s;", (barcode,))

        explain(cur, "RF-2  sale_details.sale_id (renglones de una venta)",
                "SELECT * FROM sale_details WHERE sale_id = %s;", (sale_id,))

        explain(cur, "RF-3  sale_details.product_id (ventas de un producto)",
                "SELECT * FROM sale_details WHERE product_id = %s;", (product_id,))

        explain(cur, "RF-4  sales(branch_id, created_at) (ventas de sucursal por fecha)",
                "SELECT * FROM sales WHERE branch_id = %s AND created_at >= %s;",
                (branch_id, fecha))

        explain(cur, "RF-5  sales.client_id (historial de un cliente)",
                "SELECT * FROM sales WHERE client_id = %s;", (client_id,))

        explain(cur, "RF-6  inventory_movements(product_id, created_at) (kardex)",
                "SELECT * FROM inventory_movements WHERE product_id = %s AND created_at >= %s;",
                (inv_product_id, fecha))

        explain(cur, "RF-7  branch_product low-stock (índice parcial)",
                "SELECT * FROM branch_product WHERE branch_id = %s AND stock <= alert_stock;",
                (branch_id,))

        explain(cur, "RF-8  products.name LIKE 'prefijo%' (autocompletado)",
                "SELECT * FROM products WHERE name LIKE %s;", ("Producto 999%",))

        print("\n" + "=" * 78)
        print("# Índices presentes en las tablas relevantes")
        print("-" * 78)
        cur.execute(
            "SELECT tablename, indexname FROM pg_indexes "
            "WHERE schemaname='public' AND tablename IN "
            "('products','sales','sale_details','inventory_movements','branch_product') "
            "ORDER BY tablename, indexname;"
        )
        for t, i in cur.fetchall():
            print(f"   {t:22} {i}")


if __name__ == "__main__":
    main()
