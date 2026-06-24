"""indices estrategicos SPEC-01

Revision ID: e142a1eddeff
Revises: f8c9d5a43223
Create Date: 2026-06-24 03:11:17.165255

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e142a1eddeff'
down_revision: Union[str, None] = 'f8c9d5a43223'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema. SPEC-01: solo creación de índices estratégicos."""
    # products: escaneo de código de barra y búsqueda por nombre (LIKE 'prefijo%')
    op.create_index('ix_products_barcode', 'products', ['barcode'], unique=False)
    op.create_index('ix_products_name_pattern', 'products', ['name'], unique=False,
                    postgresql_ops={'name': 'varchar_pattern_ops'})
    # sale_details: FK sin índice por defecto (renglones por venta / por producto)
    op.create_index('ix_sale_details_sale', 'sale_details', ['sale_id'], unique=False)
    op.create_index('ix_sale_details_product', 'sale_details', ['product_id'], unique=False)
    # sales: ventas por sucursal+fecha e historial por cliente
    op.create_index('ix_sales_branch_created', 'sales', ['branch_id', 'created_at'], unique=False)
    op.create_index('ix_sales_client', 'sales', ['client_id'], unique=False)
    # inventory_movements: kardex por producto en el tiempo
    op.create_index('ix_inventory_movements_product_created', 'inventory_movements',
                    ['product_id', 'created_at'], unique=False)
    # branch_product: índice PARCIAL para alerta de stock bajo
    op.create_index('ix_branch_product_low_stock', 'branch_product', ['branch_id'], unique=False,
                    postgresql_where=sa.text('stock <= alert_stock'))


def downgrade() -> None:
    """Downgrade schema. SPEC-01: elimina los índices estratégicos."""
    op.drop_index('ix_branch_product_low_stock', table_name='branch_product',
                  postgresql_where=sa.text('stock <= alert_stock'))
    op.drop_index('ix_inventory_movements_product_created', table_name='inventory_movements')
    op.drop_index('ix_sales_client', table_name='sales')
    op.drop_index('ix_sales_branch_created', table_name='sales')
    op.drop_index('ix_sale_details_product', table_name='sale_details')
    op.drop_index('ix_sale_details_sale', table_name='sale_details')
    op.drop_index('ix_products_name_pattern', table_name='products',
                  postgresql_ops={'name': 'varchar_pattern_ops'})
    op.drop_index('ix_products_barcode', table_name='products')
