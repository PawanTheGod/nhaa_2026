"""Add current_level to cases

Adds current_level integer column to cases table.
Represents escalation level: 0=operator, 1=district, 2=state, 3=ministry.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002_add_current_level"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.add_column(
            "cases",
            sa.Column(
                "current_level",
                sa.Integer(),
                nullable=True,
                server_default="0",
                comment="Escalation level: 0=operator, 1=district, 2=state, 3=ministry",
            ),
        )
    else:
        op.add_column(
            "cases",
            sa.Column(
                "current_level",
                sa.Integer(),
                nullable=True,
                default=0,
            ),
        )


def downgrade() -> None:
    op.drop_column("cases", "current_level")
