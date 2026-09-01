"""Alembic migration script — initial schema for NHAA Central Case API.

Creates all 7 tables: cases, victims, risk_assessments, officers,
notifications, audit_logs, sla_deadlines.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


officer_role_enum = sa.Enum(
    "operator", "district", "state", "ministry", "police", "dlsa",
    "medical", "counselor", "witness_protection", name="officer_role",
)
channel_origin_enum = sa.Enum("portal", "chatbot", "ivrs", "mobile_app", name="channel_origin")
case_status_enum = sa.Enum("new", "in_progress", "escalated", "resolved", "closed", name="case_status")
risk_tier_enum = sa.Enum("low", "moderate", "high", "critical", name="risk_tier")
notification_status_enum = sa.Enum("pending", "sent", "delivered", "failed", name="notification_status")


def _is_postgres():
    bind = op.get_bind()
    return bind.dialect.name == "postgresql"


def _create_enum_if_not_exists(enum_type, name):
    if _is_postgres():
        enum_values = list(enum_type.enums)
        enum_list = ", ".join(f"'{v}'" for v in enum_values)
        sql = f'DO $$ BEGIN CREATE TYPE "{name}" AS ENUM ({enum_list}); EXCEPTION WHEN duplicate_object THEN NULL; END $$;'
        op.execute(sa.text(sql))
    else:
        enum_type.create(op.get_bind(), checkfirst=True)


def _drop_enum_if_exists(name):
    if _is_postgres():
        op.execute(sa.text(f'DROP TYPE IF EXISTS "{name}" CASCADE'))
    else:
        # no-op for SQLite; enums are part of table DDL
        pass


def upgrade() -> None:
    # ── victims ──────────────────────────────────────────────
    op.create_table(
        "victims",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("pseudoid", sa.String(100), nullable=False, unique=True, comment="Pseudonymous reference — never store identity-linked data in plain text"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("age_group", sa.String(20), nullable=True),
        sa.Column("gender", sa.String(20), nullable=True),
        sa.Column("caste_category", sa.String(50), nullable=True),
        sa.Column("language_preference", sa.String(10), nullable=False, server_default="en"),
        sa.Column("consent_given", sa.Boolean, nullable=False, server_default="false"),
    )
    op.create_index("idx_victims_pseudoid", "victims", ["pseudoid"])

    # ── officers ─────────────────────────────────────────────
    _create_enum_if_not_exists(officer_role_enum, "officer_role")
    if _is_postgres():
        role_type = postgresql.ENUM(*officer_role_enum.enums, name="officer_role", create_type=False)
        op.create_table(
            "officers",
            sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
            sa.Column("name", sa.String(200), nullable=False),
            sa.Column("role", role_type, nullable=False),
            sa.Column("district", sa.String(100), nullable=True),
            sa.Column("state", sa.String(100), nullable=True),
            sa.Column("badge_id", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        )
    else:
        op.create_table(
            "officers",
            sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
            sa.Column("name", sa.String(200), nullable=False),
            sa.Column("role", officer_role_enum, nullable=False),
            sa.Column("district", sa.String(100), nullable=True),
            sa.Column("state", sa.String(100), nullable=True),
            sa.Column("badge_id", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        )
    op.create_index("idx_officers_role", "officers", ["role"])
    op.create_index("idx_officers_district", "officers", ["district"])
    op.create_index("idx_officers_state", "officers", ["state"])

    # ── cases ────────────────────────────────────────────────
    _create_enum_if_not_exists(channel_origin_enum, "channel_origin")
    _create_enum_if_not_exists(case_status_enum, "case_status")
    _create_enum_if_not_exists(risk_tier_enum, "risk_tier")

    if _is_postgres():
        op.create_table(
            "cases",
            sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
            sa.Column("channel_of_origin", postgresql.ENUM(*channel_origin_enum.enums, name="channel_origin", create_type=False), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("status", postgresql.ENUM(*case_status_enum.enums, name="case_status", create_type=False), nullable=False, server_default="new"),
            sa.Column("district", sa.String(100), nullable=True),
            sa.Column("state", sa.String(100), nullable=True),
            sa.Column("incident_description", sa.Text, nullable=True),
            sa.Column("incident_date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("language", sa.String(10), nullable=False, server_default="en"),
            sa.Column("is_silent_signal", sa.Boolean, nullable=False, server_default="false"),
            sa.Column("victim_id", sa.BigInteger, sa.ForeignKey("victims.id"), nullable=True),
            sa.Column("assigned_officer_id", sa.BigInteger, sa.ForeignKey("officers.id"), nullable=True),
            sa.Column("svi_score", sa.Numeric(4, 2), nullable=True),
            sa.Column("risk_tier", postgresql.ENUM(*risk_tier_enum.enums, name="risk_tier", create_type=False), nullable=True),
            sa.Column("recommended_action", sa.String(100), nullable=True),
        )
    else:
        op.create_table(
            "cases",
            sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
            sa.Column("channel_of_origin", channel_origin_enum, nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("status", case_status_enum, nullable=False, server_default="new"),
            sa.Column("district", sa.String(100), nullable=True),
            sa.Column("state", sa.String(100), nullable=True),
            sa.Column("incident_description", sa.Text, nullable=True),
            sa.Column("incident_date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("language", sa.String(10), nullable=False, server_default="en"),
            sa.Column("is_silent_signal", sa.Boolean, nullable=False, server_default="false"),
            sa.Column("victim_id", sa.BigInteger, sa.ForeignKey("victims.id"), nullable=True),
            sa.Column("assigned_officer_id", sa.BigInteger, sa.ForeignKey("officers.id"), nullable=True),
            sa.Column("svi_score", sa.Numeric(4, 2), nullable=True),
            sa.Column("risk_tier", risk_tier_enum, nullable=True),
            sa.Column("recommended_action", sa.String(100), nullable=True),
        )
    op.create_index("idx_cases_channel", "cases", ["channel_of_origin"])
    op.create_index("idx_cases_district", "cases", ["district"])
    op.create_index("idx_cases_state", "cases", ["state"])
    op.create_index("idx_cases_status", "cases", ["status"])
    op.create_index("idx_cases_created_at", "cases", ["created_at"])

    # ── risk_assessments ─────────────────────────────────────
    if _is_postgres():
        op.create_table(
            "risk_assessments",
            sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
            sa.Column("case_id", sa.BigInteger, sa.ForeignKey("cases.id"), nullable=False),
            sa.Column("svi_score", sa.Numeric(4, 2), nullable=False),
            sa.Column("risk_tier", postgresql.ENUM(*risk_tier_enum.enums, name="risk_tier", create_type=False), nullable=False),
            sa.Column("flags", sa.JSON, nullable=True, comment="Arbitrary JSON of detected flags e.g. {trauma, fear, suicidal_ideation}"),
            sa.Column("explanation_text", sa.Text, nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("model_version", sa.String(50), nullable=True),
        )
    else:
        op.create_table(
            "risk_assessments",
            sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
            sa.Column("case_id", sa.BigInteger, sa.ForeignKey("cases.id"), nullable=False),
            sa.Column("svi_score", sa.Numeric(4, 2), nullable=False),
            sa.Column("risk_tier", risk_tier_enum, nullable=False),
            sa.Column("flags", sa.JSON, nullable=True, comment="Arbitrary JSON of detected flags e.g. {trauma, fear, suicidal_ideation}"),
            sa.Column("explanation_text", sa.Text, nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("model_version", sa.String(50), nullable=True),
        )
    op.create_index("idx_ra_case_id", "risk_assessments", ["case_id"])
    op.create_index("idx_ra_created_at", "risk_assessments", ["created_at"])
    op.create_index("idx_ra_risk_tier", "risk_assessments", ["risk_tier"])

    # ── notifications ────────────────────────────────────────
    _create_enum_if_not_exists(notification_status_enum, "notification_status")
    if _is_postgres():
        op.create_table(
            "notifications",
            sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
            sa.Column("case_id", sa.BigInteger, sa.ForeignKey("cases.id"), nullable=False),
            sa.Column("recipient_role", postgresql.ENUM(*officer_role_enum.enums, name="officer_role", create_type=False), nullable=False),
            sa.Column("channel", sa.String(20), nullable=False, comment="sms, email, push, in_app"),
            sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("status", postgresql.ENUM(*notification_status_enum.enums, name="notification_status", create_type=False), nullable=False, server_default="pending"),
            sa.Column("message_template", sa.JSON, nullable=True),
        )
    else:
        op.create_table(
            "notifications",
            sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
            sa.Column("case_id", sa.BigInteger, sa.ForeignKey("cases.id"), nullable=False),
            sa.Column("recipient_role", officer_role_enum, nullable=False),
            sa.Column("channel", sa.String(20), nullable=False, comment="sms, email, push, in_app"),
            sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("status", notification_status_enum, nullable=False, server_default="pending"),
            sa.Column("message_template", sa.JSON, nullable=True),
        )
    op.create_index("idx_notif_case_id", "notifications", ["case_id"])
    op.create_index("idx_notif_recipient", "notifications", ["recipient_role"])
    op.create_index("idx_notif_sent_at", "notifications", ["sent_at"])

    # ── audit_logs ───────────────────────────────────────────
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("actor", sa.String(100), nullable=False, comment="User id or system identifier"),
        sa.Column("action", sa.String(100), nullable=False, comment="e.g. case_created, status_updated, risk_assessed"),
        sa.Column("case_id", sa.BigInteger, sa.ForeignKey("cases.id"), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("details", sa.JSON, nullable=True),
    )
    op.create_index("idx_audit_case_id", "audit_logs", ["case_id"])
    op.create_index("idx_audit_timestamp", "audit_logs", ["timestamp"])
    op.create_index("idx_audit_actor", "audit_logs", ["actor"])

    # ── sla_deadlines ────────────────────────────────────────
    op.create_table(
        "sla_deadlines",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("case_id", sa.BigInteger, sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("deadline_type", sa.String(50), nullable=False, comment="e.g. first_response, escalation, resolution"),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("met", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_sla_case_id", "sla_deadlines", ["case_id"])
    op.create_index("idx_sla_due_date", "sla_deadlines", ["due_date"])


def downgrade() -> None:
    op.drop_table("sla_deadlines")
    op.drop_table("audit_logs")
    op.drop_table("notifications")
    op.drop_table("risk_assessments")
    op.drop_table("cases")
    op.drop_table("officers")
    op.drop_table("victims")

    _drop_enum_if_exists("notification_status")
    _drop_enum_if_exists("risk_tier")
    _drop_enum_if_exists("case_status")
    _drop_enum_if_exists("channel_origin")
    _drop_enum_if_exists("officer_role")
