"""add_event_type_organiser_participant

Revision ID: a1b2c3d4e5f6
Revises: 8500ec08dd91
Create Date: 2026-05-25 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '8500ec08dd91'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create event_type table
    op.create_table(
        'event_type',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_type'),
    )
    op.create_index('ix_event_type_id', 'event_type', ['id'])

    # Create organiser table
    op.create_table(
        'organiser',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('organiser', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organiser'),
    )
    op.create_index('ix_organiser_id', 'organiser', ['id'])

    # Add new columns to event table
    op.add_column('event', sa.Column('event_type_id', sa.Integer(), nullable=True))
    op.add_column('event', sa.Column('organiser_id', sa.Integer(), nullable=True))
    op.add_column('event', sa.Column('capacity', sa.Integer(), nullable=True))

    op.create_foreign_key(
        'fk_event_event_type', 'event', 'event_type', ['event_type_id'], ['id']
    )
    op.create_foreign_key(
        'fk_event_organiser', 'event', 'organiser', ['organiser_id'], ['id']
    )

    # Create participant table
    op.create_table(
        'participant',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('event_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(20), nullable=True),
        sa.Column('firstname', sa.String(100), nullable=False),
        sa.Column('lastname', sa.String(100), nullable=False),
        sa.Column('institution', sa.String(200), nullable=True),
        sa.Column('country_id', sa.Integer(), nullable=True),
        sa.Column('email', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(30), nullable=True),
        sa.Column('registration_number', sa.String(50), nullable=True),
        sa.Column('picture', sa.Text(), nullable=True),
        sa.Column('paid', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['event.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['country_id'], ['country.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_participant_id', 'participant', ['id'])
    op.create_index('ix_participant', 'participant', ['deleted_at'])


def downgrade() -> None:
    op.drop_index('ix_participant', table_name='participant')
    op.drop_index('ix_participant_id', table_name='participant')
    op.drop_table('participant')

    op.drop_constraint('fk_event_organiser', 'event', type_='foreignkey')
    op.drop_constraint('fk_event_event_type', 'event', type_='foreignkey')
    op.drop_column('event', 'capacity')
    op.drop_column('event', 'organiser_id')
    op.drop_column('event', 'event_type_id')

    op.drop_index('ix_organiser_id', table_name='organiser')
    op.drop_table('organiser')

    op.drop_index('ix_event_type_id', table_name='event_type')
    op.drop_table('event_type')
