"""add_media_usher_participation_roles

Revision ID: f1a2b3c4d5e6
Revises: e6f7a8b9c0d1
Create Date: 2026-09-10 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f1a2b3c4d5e6'
down_revision = 'e6f7a8b9c0d1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # MySQL stores the ENUM inline on the column — extend the value list with
    # the two new participation roles (Media, Usher).
    op.alter_column(
        'registration',
        'participation_role',
        existing_type=sa.Enum(
            'secretariat', 'delegate', 'presenter', 'speaker', 'sponsor',
            'moderator', 'participant', 'student', 'exhibitor', 'media',
            'usher', 'world', 'other_africa', 'member_state', 'moh',
            name='participationrole',
        ),
        nullable=False,
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        'registration',
        'participation_role',
        existing_type=sa.Enum(
            'secretariat', 'delegate', 'presenter', 'speaker', 'sponsor',
            'moderator', 'participant', 'student', 'exhibitor', 'world',
            'other_africa', 'member_state', 'moh',
            name='participationrole',
        ),
        nullable=False,
        existing_nullable=False,
    )