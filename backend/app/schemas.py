from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models import (
    CaseStatus, ChannelOrigin, NotificationStatus,
    OfficerRole, RiskTier,
)


def _serialize(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return value


class RiskAssessmentBase(BaseModel):
    svi_score: float = Field(..., ge=0, le=100)
    risk_tier: RiskTier
    flags: Optional[dict[str, Any]] = None
    explanation_text: str
    model_version: Optional[str] = None


class RiskAssessmentCreate(RiskAssessmentBase):
    case_id: int


class RiskAssessmentOut(RiskAssessmentBase):
    model_config = ConfigDict(from_attributes=True, serialize_whatever=True)

    id: int
    case_id: int
    created_at: datetime


class CaseBase(BaseModel):
    channel_of_origin: ChannelOrigin
    district: Optional[str] = None
    state: Optional[str] = None
    incident_description: Optional[str] = None
    incident_date: Optional[datetime] = None
    language: str = "en"
    is_silent_signal: bool = False
    victim_id: Optional[int] = None
    assigned_officer_id: Optional[int] = None


class CaseCreate(CaseBase):
    pass


class CaseUpdate(BaseModel):
    status: Optional[CaseStatus] = None
    district: Optional[str] = None
    state: Optional[str] = None
    incident_description: Optional[str] = None
    assigned_officer_id: Optional[int] = None
    svi_score: Optional[float] = None
    risk_tier: Optional[RiskTier] = None
    recommended_action: Optional[str] = None


class RiskAssessmentMini(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    svi_score: float
    risk_tier: RiskTier
    explanation_text: str
    created_at: datetime


class CaseOut(CaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: CaseStatus
    created_at: datetime
    updated_at: datetime
    svi_score: Optional[float] = None
    risk_tier: Optional[RiskTier] = None
    recommended_action: Optional[str] = None
    risk_assessments: list[RiskAssessmentMini] = []


class CaseDetail(CaseOut):
    risk_assessments: list[RiskAssessmentOut] = []


class SlaDeadlineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    deadline_type: str
    due_date: datetime
    met: bool
    resolved_at: Optional[datetime] = None


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor: str
    action: str
    case_id: Optional[int]
    timestamp: datetime
    details: Optional[dict[str, Any]] = None


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    recipient_role: OfficerRole
    channel: str
    sent_at: Optional[datetime]
    status: NotificationStatus


class OfficerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    role: OfficerRole
    district: Optional[str]
    state: Optional[str]
