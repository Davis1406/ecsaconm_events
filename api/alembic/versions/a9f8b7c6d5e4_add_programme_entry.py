"""add_programme_entry

Revision ID: a9f8b7c6d5e4
Revises: f1a2b3c4d5e6
Create Date: 2026-09-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a9f8b7c6d5e4'
down_revision = 'f1a2b3c4d5e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'programme_entry',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=20), nullable=False),
        sa.Column('day', sa.String(length=30), nullable=False),
        sa.Column('session', sa.String(length=20), nullable=True),
        sa.Column('room', sa.String(length=100), nullable=True),
        sa.Column('code', sa.String(length=30), nullable=True),
        sa.Column('theme', sa.String(length=30), nullable=True),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('presenter_name', sa.String(length=200), nullable=True),
        sa.Column('role', sa.Text(), nullable=True),
        sa.Column('activity', sa.Text(), nullable=True),
        sa.Column('original_presenter', sa.String(length=200), nullable=True),
        sa.Column('is_substitution', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('presentation_file', sa.String(length=500), nullable=True),
        sa.Column('presentation_uploaded_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['event.id'], name='fk_programme_entry_event'),
        sa.Index('ix_programme_entry', 'event_id', 'category', 'day', 'deleted_at'),
    )
    op.create_index('ix_programme_entry_id', 'programme_entry', ['id'])
    op.create_index('ix_programme_entry_category', 'programme_entry', ['category'])


def downgrade() -> None:
    op.drop_table('programme_entry')