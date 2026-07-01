import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

def get_native_connection():
    """Crea y devuelve una conexión de psycopg3 usando variables de entorno"""
    return psycopg.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5438"),
            dbname=os.getenv("DB_NAME", "dba_final"),
            user=os.getenv("DB_USER", "admin"),
            password=os.getenv("DB_PASSWORD", "admin1234"),
            row_factory=dict_row
    )


def process_sale_transaction(sale_data: dict, details_data: list[dict])->dict:
    """Procesa una venta completa en forma atómica"""
    conn = get_native_connection()

    try:
        with conn.transaction():
            with conn.cursor() as cur:

                cur.execute(
                        """
                        INSERT INTO sales(
                            id, branch_id, user_id, client_id, session_id,
                            payment_method_id, total_amount, created_at, updated_at
                            )
                        VALUES(
                            gen_random_uuid(), %(branch_id)s, %(user_id)s, %(client_id)s,
                            %(session_id)s, %(payment_method_id)s, %(total_amount)s,
                            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                            ) RETURNING id;

                        """,
                        sale_data

                )
                sale_id = cur.fetchone()['id']

                for detail in details_data:
                    detail['sale_id'] = sale_id
                    detail['branch_id'] = sale_data['branch_id']

                    cur.execute(
                            """
                            INSERT INTO sale_details(
                                id, sale_id, product_id, quantity, unit_price,
                                created_at, updated_at
                            )VALUES(
                                gen_random_uuid(), %(sale_id)s, %(product_id)s,
                                %(quantity)s, %(unit_price)s,
                                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                            );
                            """,
                            detail
                    )

                    cur.execute(
                            """
                            UPDATE branch_product
                            SET stock = stock - %(quantity)s,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE branch_id = %(branch_id)s AND product_id = %(product_id)s
                            RETURNING stock;
                            """,
                            detail
                    )

                    resultado_stock = cur.fetchone()
                    if resultado_stock is None:
                        raise ValueError(f"Producto {detail['product_id']} no hallado en la sucursal.")

                    if resultado_stock['stock'] < 0:
                        raise ValueError(f"Stock insuficiente para el producto {detail['product_id']}.")

        try:
            from nosql.events import log_event
            log_event("sale_confirmed", {
                "sale_id": str(sale_id),
                "total": float(sale_data["total_amount"]),
                "branch_id": str(sale_data.get("branch_id", "")),
                "user_id": str(sale_data.get("user_id", "")),
                "client_id": str(sale_data.get("client_id", "")),
                "items_count": sum(d.get("quantity", 1) for d in details_data)
            })
        except Exception as e:
            print(f"[warn] no se pudo registrar evento NoSQL: {e}")

        return {"status" : "success", "sale_id": sale_id}
    except Exception as e:
        print(f"Error en venta (Rollback automático): {e}")
        raise e
    finally:
        conn.close()


def process_purchase_transaction(purchase_data: dict, details_data: list[dict]) -> dict:
    """Procesa una compra completa en forma atómica (incrementando el stock)"""
    conn = get_native_connection()

    try:
        with conn.transaction():
            with conn.cursor() as cur:

                cur.execute(
                    """
                    INSERT INTO purchases(
                        id, branch_id, user_id, supplier_id, total_amount, 
                        status, created_at, updated_at
                    )
                    VALUES(
                        gen_random_uuid(), %(branch_id)s, %(user_id)s, %(supplier_id)s,
                        %(total_amount)s, 'completed', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    ) RETURNING id;
                    """,
                    purchase_data
                )
                purchase_id = cur.fetchone()['id']

                for detail in details_data:
                    detail['purchase_id'] = purchase_id
                    detail['branch_id'] = purchase_data['branch_id']

                    cur.execute(
                        """
                        INSERT INTO purchase_details(
                            id, purchase_id, product_id, quantity, unit_cost,
                            created_at, updated_at
                        ) VALUES (
                            gen_random_uuid(), %(purchase_id)s, %(product_id)s,
                            %(quantity)s, %(unit_cost)s,
                            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                        );
                        """,
                        detail
                    )

                    cur.execute(
                        """
                        INSERT INTO branch_product (branch_id, product_id, stock, alert_stock, created_at, updated_at)
                        VALUES (%(branch_id)s, %(product_id)s, %(quantity)s, 5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        ON CONFLICT (branch_id, product_id) DO UPDATE
                        SET stock = branch_product.stock + EXCLUDED.stock,
                            updated_at = CURRENT_TIMESTAMP;
                        """,
                        detail
                    )

        try:
            from nosql.events import log_event
            log_event("purchase_confirmed", {
                "purchase_id": str(purchase_id),
                "total": float(purchase_data["total_amount"]),
                "branch_id": str(purchase_data.get("branch_id", "")),
                "user_id": str(purchase_data.get("user_id", "")),
                "supplier_id": str(purchase_data.get("supplier_id", "")),
                "items_count": sum(d.get("quantity", 1) for d in details_data)
            })
        except Exception as e:
            print(f"[warn] no se pudo registrar evento NoSQL: {e}")

        return {"status": "success", "purchase_id": purchase_id}
    except Exception as e:
        print(f"Error en compra (Rollback automático): {e}")
        raise e
    finally:
        conn.close()

