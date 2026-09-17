"""add_departure_point

Revision ID: e7f8a9b0c1d2
Revises: d1e2f3a4b5c6
Create Date: 2026-09-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e7f8a9b0c1d2'
down_revision = 'd1e2f3a4b5c6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('departure_detail', sa.Column('departure_point', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('departure_detail', 'departure_point')