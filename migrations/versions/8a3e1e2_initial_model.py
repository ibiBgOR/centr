"""initial model

Revision ID: 8a3e1e2
Revises: None
Create Date: 2016-02-16 10:40
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import expression

# revision identifiers, used by Alembic.
revision = "8a3e1e2"
down_revision = None


def upgrade():
    op.create_table("DBLogItem",
        sa.Column("id", sa.Integer, primary_key = True),
        sa.Column("message", sa.Text),
        sa.Column("time", sa.DateTime),
        sa.Column("level", sa.String(5)),
        sa.Column("trace", sa.Text),
    )
    op.create_table("DBFeedItem",
        sa.Column("id", sa.Integer, primary_key = True),
        sa.Column("content", sa.Text),
        sa.Column("type", sa.String(20)),
        sa.Column("source", sa.String(20)),
        sa.Column("time", sa.DateTime),
        sa.UniqueConstraint('content', 'source', name = 'uk_content_source'),
    )


def downgrade():
    op.drop_table("DBLogItem")
    op.drop_table("DBFeedItem")
