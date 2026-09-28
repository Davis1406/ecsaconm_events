"""add_programme_entry_video_url

Optional external video link (YouTube/Vimeo/Google Drive, etc.) for a
programme entry, shown as a "Watch video" link on the room pages instead of
uploading the raw file — for recordings/video-embedded decks too large to
usefully host directly off our own server.

Revision ID: c1d2e3f4a5b6
Revises: e7f8a9b0c1d2
Create Date: 2026-09-28 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c1d2e3f4a5b6'
down_revision = 'e7f8a9b0c1d2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'programme_entry',
        sa.Column('video_url', sa.String(length=1000), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('programme_entry', 'video_url')
