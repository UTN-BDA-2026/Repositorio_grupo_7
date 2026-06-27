import os
import random
from dotenv import load_dotenv
import psycopg
from faker import Faker
import faker_commerce

load_dotenv()

fake = Faker('es_AR')
fake.add_provider(faker_commerce.Provider)

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
    NRO_PRODUCTS = 50
    NRO_CLIENTS = 100
    NRO_SALES = 200

    with conn() as c, c.cursor() as cur:
        print("Vaciando las tablas para cargar datos de  UI...")
        cur.execute(
            "TRUNCATE sale_details, sales, inventory_movements, branch_product, "
            "products, clients, branches, taxes RESTART IDENTITY CASCADE;"            
        )   

        print("Creando impuesto IVA...")
        cur.execute(
            "INSERT INTO taxes(id, name, rate, is_default, is_active, created_at, updated_at) "
            "VALUES (gen_random_uuid(), 'IVA 21%', 21, true, true, now(), now()) RETURNING id;"
        )
        tax_id = cur.fetchone()[0]

        print("Creando sucursales...")
        sucursales = ['Sucursal Centro', 'Sucursal Norte', 'Sucursal Sur']
        branch_ids = []
        for nombre in sucursales:
            cur.execute(
                "INSERT INTO branches(id, name, is_active, created_at, updated_at) "
                "VALUES (gen_random_uuid(), %s, true, now(), now()) RETURNING id;",
                (nombre, )
            )
            branch_ids.append(cur.fetchone()[0])

        print(f"Creando {NRO_PRODUCTS} de productos realistas...")
        product_ids = []
        for _ in range(NRO_PRODUCTS):
            nombre_prod = fake.ecommerce_name()
            precio = round(random.uniform(500.0, 15000.0), 2)
            costo = round(precio * 0.6, 2)

            cur.execute(
                "INSERT INTO products(id, name, sku, barcode, sale_price, cost_price, "
                "price_includes_tax, min_stock, max_stock, is_active, tax_id, created_at, updated_at) "
                "VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, false, 5, 100, true, %s, now(), now()) RETURNING id;",
                (nombre_prod, fake.ean(length=8), fake.ean(length=13), precio, costo, tax_id)
            )
            product_ids.append(cur.fetchone()[0])
            
        print(f"Creando {NRO_CLIENTS} Clientes...")
        client_ids = []
        for _ in range(NRO_CLIENTS):
            cur.execute(
                "INSERT INTO clients (id, name, document_type, document_number, is_active, created_at, updated_at) "
                "VALUES (gen_random_uuid(), %s, 'DNI', %s, true, now(), now()) RETURNING id;",
                (fake.name(), fake.numerify('#######'))
            )
            client_ids.append(cur.fetchone()[0])

        print("Asignando stock a las sucursales...")
        for b_id in branch_ids:
            for p_id in product_ids:
                cur.execute(
                    "INSERT INTO branch_product (branch_id, product_id, stock, alert_stock, created_at, updated_at) "
                    "VALUES (%s, %s, %s, 10, now(), now());",
                    (b_id, p_id, random.randint(15, 100))
                )

        print(f"Generando {NRO_SALES} Ventas con sus detalles..")
        for _ in range(NRO_SALES):
            b_id = random.choice(branch_ids)
            c_id = random.choice(client_ids)
            total = 0

            cur.execute(
                "INSERT INTO sales(id, branch_id, client_id, total_amount, created_at, updated_at) "
                "VALUES (gen_random_uuid(), %s, %s, 0, %s, now()) RETURNING id;",
                (b_id, c_id, fake.date_time_between(start_date='-6m', end_date='now'))
            )
            sale_id = cur.fetchone()[0]
            
            for _ in range(random.randint(1, 5)):
                p_id = random.choice(product_ids)
                cantidad = random.randint(1, 3)
                precio_unitario = round(random.uniform(500.0, 15000.0), 2)
                total += (cantidad * precio_unitario)

                cur.execute(
                    "INSERT INTO sale_details(id, sale_id, product_id, quantity, unit_price, created_at, updated_at) "
                    "VALUES (gen_random_uuid(), %s, %s, %s, %s, now(), now());",
                    (sale_id, p_id, cantidad, precio_unitario)
                )

            cur.execute("UPDATE sales SET total_amount = %s WHERE id = %s", (total, sale_id))
            
    print("\n; Seed completado con éxito. Ya tenemos datos reales en la  base")

if __name__ == "__main__":
    main()





        

