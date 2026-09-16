"""add_departure_detail

Revision ID: d1e2f3a4b5c6
Revises: b1c2d3e4f5a6
Create Date: 2026-09-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd1e2f3a4b5c6'
down_revision = 'b1c2d3e4f5a6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'departure_detail',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('registration_id', sa.Integer(), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=True),
        sa.Column('token', sa.String(length=100), nullable=False),
        sa.Column('hotel', sa.String(length=255), nullable=True),
        sa.Column('departure_date', sa.String(length=30), nullable=True),
        sa.Column('departure_time', sa.String(length=30), nullable=True),
        sa.Column('submitted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['event.id'], name='fk_departure_detail_event'),
        sa.ForeignKeyConstraint(['registration_id'], ['registration.id'], name='fk_departure_detail_registration'),
        sa.Index('ix_departure_detail', 'event_id', 'email', 'deleted_at'),
    )
    op.create_index('ix_departure_detail_id', 'departure_detail', ['id'])
    op.create_index('ix_departure_detail_token', 'departure_detail', ['token'], unique=True)


def downgrade() -> None:
    op.drop_table('departure_detail')
