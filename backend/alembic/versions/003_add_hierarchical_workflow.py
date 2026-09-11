"""Add hierarchical workflow columns and evidence/handoffs tables.

Revision: 003_add_hierarchical_workflow
Depends on: 002_add_officer_credentials
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "003_add_hierarchical_workflow"
down_revision: Union[str, None] = "002_add_officer_credentials"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add new columns to cases table
    op.add_column("cases", sa.Column("person_name", sa.String(200), nullable=True))
    op.add_column("cases", sa.Column("incident_location", sa.Text(), nullable=True))
    op.add_column("cases", sa.Column("person_assaulted_date", sa.DateTime(timezone=True), nullable=True))
    op.add_column("cases", sa.Column("date_of_report", sa.DateTime(timezone=True), nullable=True))
    op.add_column("cases", sa.Column("exit_report", sa.Text(), nullable=True))
    op.add_column("cases", sa.Column("case_summary", sa.Text(), nullable=True))
    op.add_column("cases", sa.Column("is_locked", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("cases", sa.Column("locked_by", sa.BigInteger(), nullable=True))
    op.add_column("cases", sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("cases", sa.Column("forwarded_to_swo", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("cases", sa.Column("judiciary_directive", sa.Text(), nullable=True))

    # 2. Create case_evidence table
    op.create_table(
        "case_evidence",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("case_id", sa.BigInteger(), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("uploaded_by", sa.BigInteger(), sa.ForeignKey("officers.id"), nullable=True),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("file_type", sa.String(50), nullable=True),
        sa.Column("file_size", sa.BigInteger(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("tier_level", sa.String(50), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_evidence_case_id", "case_evidence", ["case_id"])
    op.create_index("idx_evidence_uploaded_at", "case_evidence", ["uploaded_at"])

    # 3. Create case_handoffs table
    op.create_table(
        "case_handoffs",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("case_id", sa.BigInteger(), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("from_officer_id", sa.BigInteger(), sa.ForeignKey("officers.id"), nullable=True),
        sa.Column("to_officer_id", sa.BigInteger(), sa.ForeignKey("officers.id"), nullable=True),
        sa.Column("from_tier", sa.String(50), nullable=True),
        sa.Column("to_tier", sa.String(50), nullable=True),
        sa.Column("handoff_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_handoff_case_id", "case_handoffs", ["case_id"])
    op.create_index("idx_handoff_created_at", "case_handoffs", ["created_at"])


def downgrade() -> None:
    op.drop_table("case_handoffs")
    op.drop_table("case_evidence")
    op.drop_column("cases", "judiciary_directive")
    op.drop_column("cases", "forwarded_to_swo")
    op.drop_column("cases", "locked_at")
    op.drop_column("cases", "locked_by")
    op.drop_column("cases", "is_locked")
    op.drop_column("cases", "case_summary")
    op.drop_column("cases", "exit_report")
    op.drop_column("cases", "date_of_report")
    op.drop_column("cases", "person_assaulted_date")
    op.drop_column("cases", "incident_location")
    op.drop_column("cases", "person_name")
