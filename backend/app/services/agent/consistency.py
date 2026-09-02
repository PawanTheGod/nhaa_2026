from app.models import RiskTier

def _tier_to_int(tier: RiskTier) -> int:
    mapping = {
        RiskTier.low: 1,
        RiskTier.moderate: 2,
        RiskTier.high: 3,
        RiskTier.critical: 4
    }
    return mapping.get(tier, 1)

def check_consistency(ai_tier: RiskTier, officer_tier: RiskTier) -> bool:
    """
    Compares the AI-determined risk tier against the officer's manually 
    submitted risk tier.
    
    Returns True if the difference is more than 1 level (indicating a severe mismatch
    that should be flagged for supervisor review).
    """
    ai_val = _tier_to_int(ai_tier)
    officer_val = _tier_to_int(officer_tier)
    
    return abs(ai_val - officer_val) > 1
