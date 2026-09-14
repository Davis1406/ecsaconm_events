"""add_programme_entry_abstract_id

Links a programme_entry row (oral/poster schedule slot) to the abstract it
was matched against, so a name-matching pass has somewhere durable to record
its result and future runs can skip entries already linked.

Revision ID: b1c2d3e4f5a6
Revises: a9f8b7c6d5e4
Create Date: 2026-09-14 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b1c2d3e4f5a6'
down_revision = 'a9f8b7c6d5e4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'programme_entry',
        sa.Column('abstract_id', sa.Integer(), nullable=True),
    )
    op.create_index('ix_programme_entry_abstract_id', 'programme_entry', ['abstract_id'])
    op.create_foreign_key(
        'fk_programme_entry_abstract', 'programme_entry', 'abstract',
        ['abstract_id'], ['id'], ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_programme_entry_abstract', 'programme_entry', type_='foreignkey')
    op.drop_index('ix_programme_entry_abstract_id', table_name='programme_entry')
    op.drop_column('programme_entry', 'abstract_id')
