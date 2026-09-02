from app.models import RiskTier

# Explicit thresholds (can be easily tuned later)
TIER_THRESHOLDS = {
    "low_max": 29.99,
    "moderate_max": 59.99,
    "high_max": 84.99,
    "critical_min": 85.0
}

# Forced minimum tiers based on specific flags
# These override raw SVI score thresholds.
FLAG_TIER_OVERRIDES = {
    "suicidal_ideation": RiskTier.high,
    "intimidation": RiskTier.high,
    "silent_distress_signal": RiskTier.critical
}

# The list of possible actions (must match the expected strings in UI/schema)
AVAILABLE_ACTIONS = {
    "counselling",
    "legal aid",
    "medical assistance",
    "police intervention",
    "witness protection",
    "emergency support"
}

def determine_risk_tier(svi_score: float, flags: list[dict]) -> RiskTier:
    """
    Determines the risk tier based on SVI score and flags.
    Follows inspectable rule-based thresholds.
    """
    # 1. Base tier from score
    if svi_score <= TIER_THRESHOLDS["low_max"]:
        base_tier = RiskTier.low
    elif svi_score <= TIER_THRESHOLDS["moderate_max"]:
        base_tier = RiskTier.moderate
    elif svi_score <= TIER_THRESHOLDS["high_max"]:
        base_tier = RiskTier.high
    else:
        base_tier = RiskTier.critical

    # 2. Apply forced overrides from flags
    # We rank tiers logically to ensure we only upgrade, never downgrade.
    tier_ranks = {
        RiskTier.low: 1,
        RiskTier.moderate: 2,
        RiskTier.high: 3,
        RiskTier.critical: 4
    }
    
    current_tier = base_tier
    current_rank = tier_ranks[current_tier]

    for flag in flags:
        flag_name = flag.get("name", "").lower()
        if flag_name in FLAG_TIER_OVERRIDES:
            override_tier = FLAG_TIER_OVERRIDES[flag_name]
            override_rank = tier_ranks[override_tier]
            if override_rank > current_rank:
                current_tier = override_tier
                current_rank = override_rank

    return current_tier

def recommend_actions(risk_tier: RiskTier, flags: list[dict]) -> list[str]:
    """
    Recommends specific actions based on the final risk tier and specific flags.
    """
    actions = set()
    flag_names = [f.get("name", "").lower() for f in flags]

    # Baseline tier-based rules
    if risk_tier in [RiskTier.moderate, RiskTier.high, RiskTier.critical]:
        actions.add("counselling")
    
    if risk_tier in [RiskTier.high, RiskTier.critical]:
        actions.add("police intervention")

    if risk_tier == RiskTier.critical:
        actions.add("emergency support")

    # Flag-specific rules
    if "suicidal_ideation" in flag_names:
        actions.update(["medical assistance", "emergency support", "counselling"])
    
    if "intimidation" in flag_names or "threat" in flag_names:
        actions.update(["legal aid", "police intervention", "witness protection"])
        
    if "physical_abuse" in flag_names or "violence" in flag_names:
        actions.update(["medical assistance", "police intervention"])
        
    if "silent_distress_signal" in flag_names:
        actions.update(["emergency support", "police intervention", "witness protection"])

    # Fallback for Low tier
    if not actions:
        actions.add("counselling") # Or could remain empty, depending on exact product requirement

    return sorted(list(actions))
