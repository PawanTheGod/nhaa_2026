from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models import Cases, RiskTier, CaseStatus
from app.services.agent.decision_engine import determine_risk_tier, recommend_actions
from app.services.agent.openrouter import generate_explanation
from app.services.agent.sla import predict_sla_breach
from app.services.agent.consistency import check_consistency

router = APIRouter(prefix="/agent", tags=["agent"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

class FlagInput(BaseModel):
    name: str
    confidence: float
    signals: List[str]

class AgentProcessInput(BaseModel):
    svi_score: float
    flags: List[FlagInput]

class AgentProcessOutput(BaseModel):
    risk_tier: str
    recommended_actions: List[str]
    explanation: str

@router.post("/process", response_model=AgentProcessOutput)
async def process_case(data: AgentProcessInput):
    """
    Processes risk signals to determine the final risk tier,
    recommend actions, and generate a human-readable explanation via OpenRouter.
    """
    flags_dict = [f.model_dump() for f in data.flags]
    
    # 1. Determine final tier
    tier = determine_risk_tier(data.svi_score, flags_dict)
    
    # 2. Determine actions
    actions = recommend_actions(tier, flags_dict)
    
    # 3. Generate explanation
    explanation = await generate_explanation(data.svi_score, tier.value, actions, flags_dict)
    
    return AgentProcessOutput(
        risk_tier=tier.value,
        recommended_actions=actions,
        explanation=explanation
    )

@router.get("/sla-predictor")
async def sla_predictor(db: AsyncSession = Depends(get_db)):
    """
    Returns open cases ordered by SLA breach risk.
    Uses real CaseStatus enum values from app.models (new, in_progress, escalated).
    Closed and resolved cases are excluded.
    """
    result = await db.execute(
        select(Cases).where(
            Cases.status.in_([CaseStatus.new, CaseStatus.in_progress, CaseStatus.escalated])
        )
    )
    cases = result.scalars().all()

    predictions = predict_sla_breach(cases)
    return predictions

class ConsistencyInput(BaseModel):
    ai_tier: RiskTier
    officer_tier: RiskTier

@router.post("/consistency-check")
async def consistency_check(data: ConsistencyInput):
    """
    Checks if there's a significant mismatch between the AI-assigned tier
    and the human officer's manual tier.
    """
    mismatch = check_consistency(data.ai_tier, data.officer_tier)
    return {
        "mismatch": mismatch,
        "requires_supervisor_review": mismatch
    }
