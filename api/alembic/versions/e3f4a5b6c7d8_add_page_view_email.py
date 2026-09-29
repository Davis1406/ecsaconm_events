"""add_page_view_email

Email typed by a visitor into the public presentations page's access prompt
(asked once per device before preview/download), so opens can be attributed
even for visitors who didn't arrive via a tagged certificate-email link.

Revision ID: e3f4a5b6c7d8
Revises: d2e3f4a5b6c7
Create Date: 2026-09-29 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e3f4a5b6c7d8'
down_revision = 'd2e3f4a5b6c7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('page_view', sa.Column('email', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('page_view', 'email')
