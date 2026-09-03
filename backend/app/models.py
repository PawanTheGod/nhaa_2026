from datetime import datetime
from enum import Enum as PyEnum
from typing import Any

from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Enum, ForeignKey, Index,
    Integer, JSON, Numeric, String, Text, func,
)
from sqlalchemy.orm import relationship

from app.database import Base

# BigInteger for PostgreSQL, Integer for SQLite (which requires INTEGER for autoincrement)
BigInt = BigInteger().with_variant(Integer, "sqlite")


class ChannelOrigin(str, PyEnum):
    portal = "portal"
    chatbot = "chatbot"
    ivrs = "ivrs"
    mobile_app = "mobile_app"


class CaseStatus(str, PyEnum):
    new = "new"
    in_progress = "in_progress"
    escalated = "escalated"
    resolved = "resolved"
    closed = "closed"


class RiskTier(str, PyEnum):
    low = "low"
    moderate = "moderate"
    high = "high"
    critical = "critical"


class OfficerRole(str, PyEnum):
    operator = "operator"      # NHAA Call Centre Operator (Level 0)
    dsp = "dsp"                # Deputy Superintendent of Police — District level (Level 1)
    sp = "sp"                  # Superintendent of Police — District/State level (Level 2)
    ig = "ig"                  # Inspector General of Police — State/Zone level (Level 3)
    # Compatibility with existing historical DB rows
    district = "district"
    state = "state"
    ministry = "ministry"
    police = "police"
    dlsa = "dlsa"
    medical = "medical"
    counselor = "counselor"
    witness_protection = "witness_protection"


class NotificationStatus(str, PyEnum):
    pending = "pending"
    sent = "sent"
    delivered = "delivered"
    failed = "failed"


class Cases(Base):
    __tablename__ = "cases"
    __table_args__ = (
        Index("idx_cases_channel", "channel_of_origin"),
        Index("idx_cases_district", "district"),
        Index("idx_cases_state", "state"),
        Index("idx_cases_status", "status"),
        Index("idx_cases_created_at", "created_at"),
    )

    id = Column(BigInt, primary_key=True, autoincrement=True)
    channel_of_origin = Column("channel_of_origin", Enum(ChannelOrigin, name="channel_origin"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    status = Column(Enum(CaseStatus, name="case_status"), nullable=False, default=CaseStatus.new)
    current_level = Column(String(50), nullable=True, comment="police, district, state, or ministry")
    district = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)

    # Incident details
    incident_description = Column(Text, nullable=True)
    incident_date = Column(DateTime(timezone=True), nullable=True)
    language = Column(String(10), nullable=False, default="en")
    is_silent_signal = Column(Boolean, default=False, nullable=False)

    # Foreign keys to victim / assigned officer
    victim_id = Column(BigInt, ForeignKey("victims.id"), nullable=True)
    assigned_officer_id = Column(BigInt, ForeignKey("officers.id"), nullable=True)

    # Computed / AI-filled fields
    svi_score = Column(Numeric(5, 2), nullable=True)
    risk_tier = Column(Enum(RiskTier, name="risk_tier"), nullable=True)
    recommended_action = Column(String(100), nullable=True)
    current_level = Column(Integer, nullable=True, default=0, comment="Escalation level: 0=operator, 1=district, 2=state, 3=ministry")

    victim = relationship("Victims", back_populates="cases")
    assigned_officer = relationship("Officers", back_populates="cases")
    risk_assessments = relationship("RiskAssessments", back_populates="case", cascade="all, delete-orphan")
    sla_deadlines = relationship("SlaDeadlines", back_populates="case", cascade="all, delete-orphan")
    notifications = relationship("Notifications", back_populates="case", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLogs", back_populates="case", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Cases id={self.id} channel={self.channel_of_origin} status={self.status}>"


class Victims(Base):
    __tablename__ = "victims"
    __table_args__ = (Index("idx_victims_pseudoid", "pseudoid"),)

    id = Column(BigInt, primary_key=True, autoincrement=True)
    pseudoid = Column("pseudoid", String(100), nullable=False, unique=True, comment="Pseudonymous reference – never store identity-linked data in plain text")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    age_group = Column(String(20), nullable=True)
    gender = Column(String(20), nullable=True)
    caste_category = Column(String(50), nullable=True)
    language_preference = Column(String(10), nullable=False, default="en")
    consent_given = Column(Boolean, default=False, nullable=False)

    cases = relationship("Cases", back_populates="victim")

    def __repr__(self):
        return f"<Victims id={self.id} pseudoid={self.pseudoid}>"


class RiskAssessments(Base):
    __tablename__ = "risk_assessments"
    __table_args__ = (
        Index("idx_ra_case_id", "case_id"),
        Index("idx_ra_created_at", "created_at"),
        Index("idx_ra_risk_tier", "risk_tier"),
    )

    id = Column(BigInt, primary_key=True, autoincrement=True)
    case_id = Column(BigInt, ForeignKey("cases.id"), nullable=False)
    svi_score = Column(Numeric(5, 2), nullable=False)
    risk_tier = Column(Enum(RiskTier, name="risk_tier"), nullable=False)
    flags = Column(JSON, nullable=True, comment="Arbitrary JSON of detected flags e.g. {trauma, fear, suicidal_ideation}")
    explanation_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    model_version = Column(String(50), nullable=True)

    case = relationship("Cases", back_populates="risk_assessments")

    def __repr__(self):
        return f"<RiskAssessments id={self.id} case_id={self.case_id} svi={self.svi_score} tier={self.risk_tier}>"


class Officers(Base):
    __tablename__ = "officers"
    __table_args__ = (
        Index("idx_officers_role", "role"),
        Index("idx_officers_district", "district"),
        Index("idx_officers_state", "state"),
        Index("idx_officers_username", "username", unique=True),
    )

    id = Column(BigInt, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    role = Column(Enum(OfficerRole, name="officer_role"), nullable=False)
    district = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    badge_id = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # ── Auth credentials (added by Aditya — auth layer) ────────────────────
    username = Column(String(100), nullable=True, unique=True)
    password_hash = Column(String(255), nullable=True)

    cases = relationship("Cases", back_populates="assigned_officer")

    def __repr__(self):
        return f"<Officers id={self.id} name={self.name} role={self.role}>"


class Notifications(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("idx_notif_case_id", "case_id"),
        Index("idx_notif_recipient", "recipient_role"),
        Index("idx_notif_sent_at", "sent_at"),
    )

    id = Column(BigInt, primary_key=True, autoincrement=True)
    case_id = Column(BigInt, ForeignKey("cases.id"), nullable=False)
    recipient_role = Column(Enum(OfficerRole, name="officer_role"), nullable=False)
    channel = Column(String(20), nullable=False, comment="sms, email, push, in_app")
    sent_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(NotificationStatus, name="notification_status"), nullable=False, default=NotificationStatus.pending)
    message_template = Column(JSON, nullable=True)

    case = relationship("Cases", back_populates="notifications")

    def __repr__(self):
        return f"<Notifications id={self.id} case_id={self.case_id} role={self.recipient_role}>"


class AuditLogs(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("idx_audit_case_id", "case_id"),
        Index("idx_audit_timestamp", "timestamp"),
        Index("idx_audit_actor", "actor"),
    )

    id = Column(BigInt, primary_key=True, autoincrement=True)
    actor = Column(String(100), nullable=False, comment="User id or system identifier")
    action = Column(String(100), nullable=False, comment="e.g. case_created, status_updated, risk_assessed")
    case_id = Column(BigInt, ForeignKey("cases.id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    details = Column(JSON, nullable=True)

    case = relationship("Cases", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLogs id={self.id} actor={self.actor} action={self.action}>"


class SlaDeadlines(Base):
    __tablename__ = "sla_deadlines"
    __table_args__ = (
        Index("idx_sla_case_id", "case_id"),
        Index("idx_sla_due_date", "due_date"),
    )

    id = Column(BigInt, primary_key=True, autoincrement=True)
    case_id = Column(BigInt, ForeignKey("cases.id"), nullable=False)
    deadline_type = Column(String(50), nullable=False, comment="e.g. first_response, escalation, resolution")
    due_date = Column(DateTime(timezone=True), nullable=False)
    met = Column(Boolean, default=False, nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    case = relationship("Cases", back_populates="sla_deadlines")

    def __repr__(self):
        return f"<SlaDeadlines id={self.id} case_id={self.case_id} type={self.deadline_type}>"
