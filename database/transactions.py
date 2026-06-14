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
                return {"status" : "success", "sale_id": sale_id}
    except Exception as e:
        print(f"Error en venta (Rollback automático): {e}")
        raise e
    finally:
        conn.close()
