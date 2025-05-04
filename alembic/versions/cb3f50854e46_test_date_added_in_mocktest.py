"""test_date added in MockTest

Revision ID: cb3f50854e46
Revises: 
Create Date: 2025-05-04 21:52:27.870808

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb3f50854e46'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'mock_tests',
        sa.Column('test_date', sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    pass
