"""init_bd

Revision ID: 20b5665a6da6
Revises: 
Create Date: 2026-05-26 03:28:15.296898

"""
import os

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20b5665a6da6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    sql_path = os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'bd_struct.sql')
    
    with open(sql_path, 'r', encoding='utf-8') as file:
        sql_script = file.read()

        op.execute(sql_script)
        

def downgrade() -> None:
    """Downgrade schema."""
    pass
