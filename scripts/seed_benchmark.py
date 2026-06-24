"""
Seed de datos de volumen para el benchmark de índices (SPEC-01).

Inserta datos sintéticos suficientes para que las consultas de prueba muestren
diferencias reales entre Seq Scan e Index Scan en `EXPLAIN ANALYZE`.

Es auto-contenido: lee la conexión desde `.env` y usa SQL masivo
(`generate_series`) para sembrar rápido. Re-ejecutable: vacía (TRUNCATE) las
tablas que siembra antes de cargar.

Uso:
    python scripts/seed_benchmark.py
"""
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

# Volúmenes (ajustables)
N_PRODUCTS = 10_000
N_CLIENTS = 2_000
N_BRANCHES = 3
N_SALES = 50_000
N_SALE_DETAILS = 150_000
N_INV_MOVEMENTS = 30_000


def conn():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5438"),
        dbname=os.getenv("DB_NAME", "dba_final"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "admin1234"),
        autocommit=True,
    )


def main():
    with conn() as c, c.cursor() as cur:
        print("Vaciando tablas sembradas...")
        cur.execute(
            "TRUNCATE sale_details, sales, inventory_movements, branch_product, "
            "products, clients, branches, taxes RESTART IDENTITY CASCADE;"
        )

        print("Impuesto base...")
        cur.execute(
            "INSERT INTO taxes (id, name, rate, is_default, is_active, created_at, updated_at) "
            "VALUES (gen_random_uuid(), 'IVA 21', 21, true, true, now(), now());"
        )

        print(f"{N_BRANCHES} sucursales...")
        cur.execute(
            "INSERT INTO branches (id, name, is_active, created_at, updated_at) "
            "SELECT gen_random_uuid(), 'Sucursal ' || g, true, now(), now() "
            "FROM generate_series(1, %s) g;",
            (N_BRANCHES,),
        )

        print(f"{N_PRODUCTS} productos...")
        cur.execute(
            "INSERT INTO products (id, name, sku, barcode, sale_price, cost_price, "
            "price_includes_tax, min_stock, max_stock, is_active, tax_id, created_at, updated_at) "
            "SELECT gen_random_uuid(), 'Producto ' || g, 'SKU-' || g, "
            "'779' || lpad(g::text, 10, '0'), (random()*1000)::numeric(12,2), "
            "(random()*500)::numeric(12,2), false, 0, 100, true, "
            "(SELECT id FROM taxes LIMIT 1), now(), now() "
            "FROM generate_series(1, %s) g;",
            (N_PRODUCTS,),
        )

        print(f"{N_CLIENTS} clientes...")
        cur.execute(
            "INSERT INTO clients (id, name, document_type, document_number, is_active, created_at, updated_at) "
            "SELECT gen_random_uuid(), 'Cliente ' || g, 'DNI', (20000000 + g)::text, true, now(), now() "
            "FROM generate_series(1, %s) g;",
            (N_CLIENTS,),
        )

        print("branch_product (una fila por producto y sucursal)...")
        cur.execute(
            "INSERT INTO branch_product (branch_id, product_id, stock, alert_stock, created_at, updated_at) "
            "SELECT b.id, p.id, (random()*50)::numeric(12,3), 5, now(), now() "
            "FROM products p CROSS JOIN branches b;"
        )

        # NOTA de rendimiento: el reparto de FK se hace con JOINs sobre
        # row_number() + módulo (set-based), NO con subconsultas por fila.
        # Una subconsulta con random() no correlacionada la evalúa PostgreSQL una
        # sola vez (InitPlan) -> todas las filas iguales; y una correlacionada por
        # fila sobre arrays grandes es lentísima. El JOIN reparte uniforme y rápido.
        print(f"{N_SALES} ventas (último año, sucursal y cliente repartidos)...")
        cur.execute(
            "WITH br AS (SELECT id, (row_number() OVER (ORDER BY name))-1 AS rn FROM branches), "
            "     cl AS (SELECT id, (row_number() OVER ())-1 AS rn FROM clients) "
            "INSERT INTO sales (id, branch_id, client_id, total_amount, created_at, updated_at) "
            "SELECT gen_random_uuid(), br.id, cl.id, (random()*5000)::numeric(12,2), "
            "  now() - (random()*365)::int * interval '1 day', now() "
            "FROM generate_series(1, %s) g "
            "JOIN br ON br.rn = g %% (SELECT count(*) FROM branches) "
            "JOIN cl ON cl.rn = g %% (SELECT count(*) FROM clients);",
            (N_SALES,),
        )

        print(f"{N_SALE_DETAILS} detalles de venta...")
        cur.execute(
            "WITH ss AS (SELECT id, (row_number() OVER ())-1 AS rn FROM sales), "
            "     pp AS (SELECT id, (row_number() OVER ())-1 AS rn FROM products) "
            "INSERT INTO sale_details (id, sale_id, product_id, quantity, unit_price, created_at, updated_at) "
            "SELECT gen_random_uuid(), ss.id, pp.id, "
            "  (1+random()*5)::numeric(12,3), (random()*1000)::numeric(12,2), now(), now() "
            "FROM generate_series(1, %s) g "
            "JOIN ss ON ss.rn = g %% (SELECT count(*) FROM sales) "
            "JOIN pp ON pp.rn = (g*7) %% (SELECT count(*) FROM products);",
            (N_SALE_DETAILS,),
        )

        print(f"{N_INV_MOVEMENTS} movimientos de inventario...")
        cur.execute(
            "WITH pp AS (SELECT id, (row_number() OVER ())-1 AS rn FROM products), "
            "     br AS (SELECT id, (row_number() OVER (ORDER BY name))-1 AS rn FROM branches) "
            "INSERT INTO inventory_movements (id, product_id, branch_id, type, quantity, reason, created_at, updated_at) "
            "SELECT gen_random_uuid(), pp.id, br.id, 'adjustment', (random()*100)::int, 'seed', "
            "  now() - (random()*365)::int * interval '1 day', now() "
            "FROM generate_series(1, %s) g "
            "JOIN pp ON pp.rn = (g*7) %% (SELECT count(*) FROM products) "
            "JOIN br ON br.rn = g %% (SELECT count(*) FROM branches);",
            (N_INV_MOVEMENTS,),
        )

        print("ANALYZE (actualiza estadísticas del planner)...")
        cur.execute("ANALYZE;")

        print("\nConteos finales:")
        for t in ["products", "clients", "branches", "branch_product",
                  "sales", "sale_details", "inventory_movements"]:
            cur.execute(f"SELECT count(*) FROM {t};")
            print(f"  {t:22} {cur.fetchone()[0]:>9}")
    print("\nSeed completo.")


if __name__ == "__main__":
    main()
