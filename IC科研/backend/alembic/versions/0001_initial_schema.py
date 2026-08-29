"""Initial IC Research Copilot schema.

Revision ID: 0001
Revises: None
"""
from alembic import op

from app.models import Base

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    Base.metadata.create_all(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    for table in reversed(Base.metadata.sorted_tables):
        table.drop(bind=op.get_bind(), checkfirst=True)

