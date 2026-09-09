"""add_attendance_form_response

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-09-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'attendance_form_response',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('firstname', sa.String(length=100), nullable=True),
        sa.Column('lastname', sa.String(length=100), nullable=True),
        sa.Column('abstract_title', sa.String(length=500), nullable=True),
        sa.Column('token', sa.String(length=100), nullable=False),
        sa.Column('response', sa.String(length=30), nullable=True),
        sa.Column('responded_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['event.id'], name='fk_attendance_form_event'),
        sa.Index('ix_attendance_form_response', 'event_id', 'email', 'deleted_at'),
    )
    op.create_index('ix_attendance_form_response_id', 'attendance_form_response', ['id'])
    op.create_index('ix_attendance_form_response_token', 'attendance_form_response', ['token'], unique=True)


def downgrade() -> None:
    op.drop_table('attendance_form_response')