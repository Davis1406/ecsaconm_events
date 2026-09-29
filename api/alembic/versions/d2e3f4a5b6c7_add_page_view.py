"""add_page_view

Tracks opens of public pages (the public Conference presentations page) —
one row per open, with an anonymous per-browser visitor id and, when known,
the user (via the signed ref on their certificate-email link).

Revision ID: d2e3f4a5b6c7
Revises: c1d2e3f4a5b6
Create Date: 2026-09-29 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd2e3f4a5b6c7'
down_revision = 'c1d2e3f4a5b6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'page_view',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('page', sa.String(length=100), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=True),
        sa.Column('visitor_id', sa.String(length=64), nullable=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=300), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_page_view_id', 'page_view', ['id'])
    op.create_index('ix_page_view_page_event_created', 'page_view', ['page', 'event_id', 'created_at'])


def downgrade() -> None:
    op.drop_index('ix_page_view_page_event_created', table_name='page_view')
    op.drop_index('ix_page_view_id', table_name='page_view')
    op.drop_table('page_view')
