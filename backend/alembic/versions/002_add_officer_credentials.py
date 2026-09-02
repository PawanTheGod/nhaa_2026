"""Add username and password_hash columns to officers table.

Revision: 002_add_officer_credentials
Depends on: 001_initial_schema

Adds:
  - officers.username  VARCHAR(100) UNIQUE
  - officers.password_hash  VARCHAR(255)
  - idx_officers_username (unique index)

Safe to run on an existing database: both columns are nullable,
so existing officer rows remain valid.
Run: alembic upgrade head
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002_add_officer_credentials"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns (nullable so existing rows are unaffected)
    op.add_column(
        "officers",
        sa.Column("username", sa.String(100), nullable=True),
    )
    op.add_column(
        "officers",
        sa.Column("password_hash", sa.String(255), nullable=True),
    )

    # Unique constraint + index on username
    op.create_unique_constraint("uq_officers_username", "officers", ["username"])
    op.create_index("idx_officers_username", "officers", ["username"], unique=True)


def downgrade() -> None:
    op.drop_index("idx_officers_username", table_name="officers")
    op.drop_constraint("uq_officers_username", "officers", type_="unique")
    op.drop_column("officers", "password_hash")
    op.drop_column("officers", "username")
