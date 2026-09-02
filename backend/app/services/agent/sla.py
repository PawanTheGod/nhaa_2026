from datetime import datetime, timezone
from typing import List
from app.models import Cases, RiskTier

# SLAs in hours
SLA_HOURS = {
    RiskTier.critical: 2,
    RiskTier.high: 24,
    RiskTier.moderate: 72,
    RiskTier.low: 168
}

def predict_sla_breach(cases: List[Cases]) -> List[dict]:
    """
    Given a list of open cases, predicts which ones are likely to miss their 
    legal deadline (SLA). Returns a sorted list (highest risk first) of dictionaries 
    containing case info and breach risk level.
    """
    results = []
    now = datetime.now(timezone.utc)
    
    for case in cases:
        if not case.created_at or not case.risk_tier:
            continue
            
        # created_at might be naive in sqlite/postgres depending on config, 
        # assure it's timezone-aware for comparison.
        created = case.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)

        elapsed_hours = (now - created).total_seconds() / 3600.0
        allowed_hours = SLA_HOURS.get(case.risk_tier, 72)
        
        time_remaining = allowed_hours - elapsed_hours
        ratio = elapsed_hours / allowed_hours
        
        if ratio >= 1.0:
            risk = "BREACHED"
        elif ratio >= 0.8:
            risk = "HIGH"
        elif ratio >= 0.5:
            risk = "MEDIUM"
        else:
            risk = "LOW"
            
        results.append({
            "case_id": case.id,
            "risk_tier": case.risk_tier.value,
            "allowed_hours": allowed_hours,
            "elapsed_hours": round(elapsed_hours, 1),
            "time_remaining_hours": round(time_remaining, 1),
            "breach_risk": risk
        })
        
    # Sort: BREACHED first, then HIGH, MEDIUM, LOW. Within category, lowest time_remaining first.
    risk_weights = {"BREACHED": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    results.sort(key=lambda x: (-risk_weights[x["breach_risk"]], x["time_remaining_hours"]))
    
    return results
