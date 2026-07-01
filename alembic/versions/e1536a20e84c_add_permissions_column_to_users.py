"""add permissions column to users

Revision ID: e1536a20e84c
Revises: e142a1eddeff
Create Date: 2026-07-01 22:07:29.909585

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1536a20e84c'
down_revision: Union[str, None] = 'e142a1eddeff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema. Agrega la columna permissions (JSON) a users.

    El modelo User declaraba `permissions` pero ninguna migración la creaba,
    provocando `column users.permissions does not exist`. Se descarta el drift
    espurio de FKs de `purchases` que autogenerate detecta (recrea las mismas FKs).
    """
    op.add_column('users', sa.Column('permissions', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'permissions')
