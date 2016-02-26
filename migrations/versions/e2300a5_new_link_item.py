"""new link column for each feed item

Revision ID: e2300a5
Revises: None
Create Date: 2016-02-26 16:27
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import expression

# revision identifiers, used by Alembic.
revision = "e2300a5"
down_revision = "8a3e1e2"


def upgrade():
    op.add_column("db_feed_item",
        sa.Column("link", sa.Text, server_default = "")
    )


def downgrade():
    op.drop_column("db_feed_item", "link")
