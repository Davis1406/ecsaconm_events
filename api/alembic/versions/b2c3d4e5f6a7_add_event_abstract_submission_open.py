"""add_event_abstract_submission_open

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-09-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'event',
        sa.Column('abstract_submission_open', sa.Boolean(), nullable=False, server_default='1'),
    )


def downgrade() -> None:
    op.drop_column('event', 'abstract_submission_open')
