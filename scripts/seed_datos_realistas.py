import os
import random
from dotenv import load_dotenv
import psycopg
from faker import Faker
import faker_commerce

load_dotenv()

fake = Faker('es_AR')
fake.add_provider(faker_commerce.Provider)

NRO_PRODUCTS = 50
NRO_CLIENTS = 100
NRO_SALES = 200

CATEGORIAS = [
    ("Alimentos", "Productos alimenticios y comestibles"),
    ("Bebidas", "Bebidas con y sin alcohol"),
    ("Limpieza", "Artículos de limpieza para el hogar"),
    ("Higiene Personal", "Productos de cuidado e higiene personal"),
    ("Lácteos", "Leche, quesos, yogures y derivados"),
    ("Panadería", "Pan, facturas y productos de panadería"),
    ("Carnes", "Cortes de carne vacuna, pollo y cerdo"),
    ("Frutas y Verduras", "Productos frescos de verdulería"),
    ("Snacks", "Galletitas, papas fritas y golosinas"),
    ("Congelados", "Productos congelados y precocidos"),
]

MARCAS = [
    ("La Serenísima", "Marca líder en lácteos"),
    ("Arcor", "Alimentos y golosinas"),
    ("Quilmes", "Cervecería y bebidas"),
    ("Molinos Río de la Plata", "Alimentos y aceites"),
    ("Marolio", "Productos alimenticios económicos"),
    ("Bagley", "Galletitas y snacks"),
    ("Sancor", "Lácteos y derivados"),
    ("Bimbo", "Panificados industriales"),
    ("Unilever", "Higiene y limpieza"),
    ("P&G", "Cuidado personal y del hogar"),
]

METODOS_PAGO = [
    ("Efectivo", 0),
    ("Tarjeta de Débito", 0),
    ("Tarjeta de Crédito", 8.5),
    ("Mercado Pago", 5.0),
    ("Transferencia", 0),
]

PRODUCTOS_POR_CATEGORIA = {
    "Alimentos": [
        "Arroz Largo Fino 1kg", "Fideos Tirabuzón 500g", "Aceite de Girasol 1.5L",
        "Harina 000 1kg", "Azúcar 1kg", "Sal Fina 500g",
    ],
    "Bebidas": [
        "Coca-Cola 2.25L", "Agua Mineral 1.5L", "Cerveza Lata 473ml",
        "Jugo de Naranja 1L", "Fernet 750ml", "Vino Tinto Malbec 750ml",
    ],
    "Limpieza": [
        "Lavandina 1L", "Detergente 750ml", "Desodorante de Piso 900ml",
        "Esponja Multiuso", "Bolsa de Residuos x10",
    ],
    "Higiene Personal": [
        "Shampoo 400ml", "Jabón de Tocador x3", "Pasta Dental 120g",
        "Desodorante Aerosol 150ml", "Papel Higiénico x4",
    ],
    "Lácteos": [
        "Leche Entera 1L", "Yogur Bebible 1L", "Queso Cremoso 1kg",
        "Manteca 200g", "Dulce de Leche 400g",
    ],
    "Panadería": [
        "Pan Lactal 500g", "Facturas Surtidas x6", "Medialunas x12",
        "Pan de Campo 400g", "Bizcochos de Grasa x6",
    ],
    "Carnes": [
        "Bife de Chorizo 1kg", "Pechuga de Pollo 1kg", "Carne Picada 1kg",
        "Costilla de Cerdo 1kg", "Milanesa de Ternera 1kg",
    ],
    "Frutas y Verduras": [
        "Banana 1kg", "Tomate Redondo 1kg", "Papa 1kg",
        "Lechuga Criolla", "Manzana Roja 1kg",
    ],
    "Snacks": [
        "Papas Fritas Clásicas 300g", "Galletitas de Agua x3",
        "Chocolatín x6", "Alfajor Triple", "Maní Salado 400g",
    ],
    "Congelados": [
        "Empanadas x12", "Milanesas de Soja x4", "Pizza Congelada",
        "Nuggets de Pollo x12", "Hamburguesas x4",
    ],
}


def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5438"),
        dbname=os.getenv("DB_NAME", "dba_final"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "admin1234"),
        autocommit=True,
    )


def main():
    with get_connection() as c, c.cursor() as cur:

        print("Vaciando tablas...")
        cur.execute(
            "TRUNCATE sale_details, sales, inventory_movements, branch_product, "
            "products, clients, users, branches, taxes, categories, brands, payment_methods "
            "RESTART IDENTITY CASCADE;"
        )

        print("Creando impuestos...")
        impuestos = [
            ("IVA 21%", 21, True),
            ("IVA 10.5%", 10.5, False),
            ("Exento", 0, False),
        ]
        tax_ids = []
        for nombre, tasa, es_default in impuestos:
            cur.execute(
                "INSERT INTO taxes(id, name, rate, is_default, is_active, created_at, updated_at) "
                "VALUES (gen_random_uuid(), %s, %s, %s, true, now(), now()) RETURNING id;",
                (nombre, tasa, es_default),
            )
            tax_ids.append(cur.fetchone()[0])
        tax_iva_21 = tax_ids[0]

        print("Creando métodos de pago...")
        payment_method_ids = []
        for nombre, recargo in METODOS_PAGO:
            cur.execute(
                "INSERT INTO payment_methods(id, name, surcharge_percentage, is_active, created_at, updated_at) "
                "VALUES (gen_random_uuid(), %s, %s, true, now(), now()) RETURNING id;",
                (nombre, recargo),
            )
            payment_method_ids.append(cur.fetchone()[0])

        print("Creando categorías...")
        category_ids = {}
        for nombre, descripcion in CATEGORIAS:
            cur.execute(
                "INSERT INTO categories(id, name, description, is_active, created_at, updated_at) "
                "VALUES (gen_random_uuid(), %s, %s, true, now(), now()) RETURNING id;",
                (nombre, descripcion),
            )
            category_ids[nombre] = cur.fetchone()[0]

        print("Creando marcas...")
        brand_ids = []
        for nombre, descripcion in MARCAS:
            slug = nombre.lower().replace(" ", "-").replace("&", "y")
            cur.execute(
                "INSERT INTO brands(id, name, slug, description, is_active, created_at, updated_at) "
                "VALUES (gen_random_uuid(), %s, %s, %s, true, now(), now()) RETURNING id;",
                (nombre, slug, descripcion),
            )
            brand_ids.append(cur.fetchone()[0])

        print("Creando sucursales...")
        sucursales = ["Sucursal Centro", "Sucursal Norte", "Sucursal Sur"]
        branch_ids = []
        for nombre in sucursales:
            cur.execute(
                "INSERT INTO branches(id, name, is_active, created_at, updated_at) "
                "VALUES (gen_random_uuid(), %s, true, now(), now()) RETURNING id;",
                (nombre,),
            )
            branch_ids.append(cur.fetchone()[0])

        print("Creando usuarios...")
        user_ids = []
        # Admin Global
        cur.execute(
            "INSERT INTO users(id, name, email, password, pos_pin, branch_id, created_at, updated_at) "
            "VALUES (gen_random_uuid(), 'Administrador Principal', 'admin@example.com', '123', '0000', NULL, now(), now()) RETURNING id;"
        )
        user_ids.append(cur.fetchone()[0])
        
        # Cajeros (uno por sucursal)
        for i, b_id in enumerate(branch_ids):
            cur.execute(
                "INSERT INTO users(id, name, email, password, pos_pin, branch_id, created_at, updated_at) "
                "VALUES (gen_random_uuid(), %s, %s, '123', %s, %s, now(), now()) RETURNING id;",
                (f"Cajero {sucursales[i]}", f"cajero{i+1}@example.com", f"111{i+1}", b_id),
            )
            user_ids.append(cur.fetchone()[0])

        print("Creando productos con categorías y marcas...")
        product_ids = []
        product_prices = {}
        for cat_nombre, productos in PRODUCTOS_POR_CATEGORIA.items():
            cat_id = category_ids[cat_nombre]
            for prod_nombre in productos:
                precio = round(random.uniform(200.0, 15000.0), 2)
                costo = round(precio * random.uniform(0.45, 0.70), 2)
                brand_id = random.choice(brand_ids)

                cur.execute(
                    "INSERT INTO products(id, name, sku, barcode, sale_price, cost_price, "
                    "price_includes_tax, min_stock, max_stock, is_active, tax_id, "
                    "category_id, brand_id, created_at, updated_at) "
                    "VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, false, 5, 100, true, "
                    "%s, %s, %s, now(), now()) RETURNING id;",
                    (prod_nombre, fake.ean(length=8), fake.ean(length=13),
                     precio, costo, tax_iva_21, cat_id, brand_id),
                )
                pid = cur.fetchone()[0]
                product_ids.append(pid)
                product_prices[pid] = precio

        productos_extra = NRO_PRODUCTS - len(product_ids)
        if productos_extra > 0:
            cat_keys = list(category_ids.keys())
            for _ in range(productos_extra):
                nombre_prod = fake.ecommerce_name()
                precio = round(random.uniform(500.0, 15000.0), 2)
                costo = round(precio * random.uniform(0.45, 0.70), 2)
                cat_id = category_ids[random.choice(cat_keys)]
                brand_id = random.choice(brand_ids)

                cur.execute(
                    "INSERT INTO products(id, name, sku, barcode, sale_price, cost_price, "
                    "price_includes_tax, min_stock, max_stock, is_active, tax_id, "
                    "category_id, brand_id, created_at, updated_at) "
                    "VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, false, 5, 100, true, "
                    "%s, %s, %s, now(), now()) RETURNING id;",
                    (nombre_prod, fake.ean(length=8), fake.ean(length=13),
                     precio, costo, tax_iva_21, cat_id, brand_id),
                )
                pid = cur.fetchone()[0]
                product_ids.append(pid)
                product_prices[pid] = precio

        print(f"Creando {NRO_CLIENTS} clientes...")
        client_ids = []
        for _ in range(NRO_CLIENTS):
            doc_type = random.choice(["DNI", "CUIT", "PASAPORTE"])
            cur.execute(
                "INSERT INTO clients(id, name, document_type, document_number, "
                "is_active, created_at, updated_at) "
                "VALUES (gen_random_uuid(), %s, %s, %s, true, now(), now()) RETURNING id;",
                (fake.name(), doc_type, fake.numerify("########")),
            )
            client_ids.append(cur.fetchone()[0])

        print("Asignando stock a sucursales...")
        for b_id in branch_ids:
            for p_id in product_ids:
                cur.execute(
                    "INSERT INTO branch_product(branch_id, product_id, stock, alert_stock, "
                    "created_at, updated_at) VALUES (%s, %s, %s, 10, now(), now());",
                    (b_id, p_id, random.randint(20, 150)),
                )

        print(f"Generando {NRO_SALES} ventas con detalle y método de pago...")
        for _ in range(NRO_SALES):
            b_id = random.choice(branch_ids)
            c_id = random.choice(client_ids)
            pm_id = random.choice(payment_method_ids)
            fecha = fake.date_time_between(start_date="-6m", end_date="now")
            total = 0

            cur.execute(
                "INSERT INTO sales(id, branch_id, user_id, client_id, payment_method_id, "
                "total_amount, created_at, updated_at) "
                "VALUES (gen_random_uuid(), %s, %s, %s, %s, 0, %s, now()) RETURNING id;",
                (b_id, random.choice(user_ids), c_id, pm_id, fecha),
            )
            sale_id = cur.fetchone()[0]

            items_en_venta = random.randint(1, 6)
            productos_venta = random.sample(product_ids, min(items_en_venta, len(product_ids)))

            for p_id in productos_venta:
                cantidad = random.randint(1, 4)
                precio_unitario = product_prices[p_id]
                total += cantidad * precio_unitario

                cur.execute(
                    "INSERT INTO sale_details(id, sale_id, product_id, quantity, "
                    "unit_price, created_at, updated_at) "
                    "VALUES (gen_random_uuid(), %s, %s, %s, %s, now(), now());",
                    (sale_id, p_id, cantidad, precio_unitario),
                )

            cur.execute(
                "UPDATE sales SET total_amount = %s WHERE id = %s;",
                (round(total, 2), sale_id),
            )

        print("\nSeed completado con éxito.")
        print(f"  - {len(METODOS_PAGO)} métodos de pago")
        print(f"  - {len(CATEGORIAS)} categorías")
        print(f"  - {len(MARCAS)} marcas")
        print(f"  - {len(impuestos)} impuestos")
        print(f"  - {len(sucursales)} sucursales")
        print(f"  - {len(user_ids)} usuarios")
        print(f"  - {len(product_ids)} productos")
        print(f"  - {NRO_CLIENTS} clientes")
        print(f"  - {NRO_SALES} ventas con detalle")


if __name__ == "__main__":
    main()
