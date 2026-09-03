"""
Aatmman Agent Decision Engine — v2 (reconciled with Vinit's real schema)

Changes from v1:
  - State machine now operates on (status, current_level) pairs from Vinit's
    real CaseStatus + OfficerRole enums. No invented status names.
  - Authority matrix uses the single 9-value OfficerRole enum exactly:
    operator, district, state, ministry, police, dlsa, medical, counselor,
    witness_protection  (NOT "legalaid", NOT "responderType")
  - recommend_actions() returns a list AND builds the nested-object flags shape
    expected by the DB flags JSON column.
  - Tier thresholds unchanged and still inspectable.
"""
from app.models import RiskTier, CaseStatus, OfficerRole

# ─── Tier thresholds (can be tuned without touching logic) ────────────────────
TIER_THRESHOLDS = {
    "low_max": 29.99,
    "moderate_max": 59.99,
    "high_max": 84.99,
    "critical_min": 85.0,
}

# ─── Flag-based forced minimum tiers ─────────────────────────────────────────
FLAG_TIER_OVERRIDES: dict[str, RiskTier] = {
    "suicidal_ideation": RiskTier.high,
    "intimidation": RiskTier.high,
    "silent_distress_signal": RiskTier.critical,
}

# ─── State machine: real (status, current_level) pairs ───────────────────────
# Every meaningful state is a (CaseStatus, OfficerRole | None) tuple.
# "None" for current_level means the case hasn't been escalated yet.
#
# Transition table: what actions are allowed given the current state.
# Maps (status, current_level) -> list[str] of allowed actions.
ALLOWED_ACTIONS_BY_STATE: dict[tuple, list[str]] = {
    (CaseStatus.new,         None):                ["assign_operator", "ai_triage"],
    (CaseStatus.in_progress, OfficerRole.operator): ["escalate_to_dsp", "resolve", "close"],
    (CaseStatus.escalated,   OfficerRole.dsp):      ["escalate_to_sp", "resolve", "investigate"],
    (CaseStatus.escalated,   OfficerRole.sp):       ["escalate_to_ig", "resolve"],
    (CaseStatus.escalated,   OfficerRole.ig):       ["resolve", "direct_intervention"],
    (CaseStatus.resolved,    None):                 ["close", "reopen"],
    (CaseStatus.closed,      None):                 [],
}

def get_allowed_actions(status: CaseStatus, current_level: OfficerRole | None) -> list[str]:
    """
    Returns the list of allowed case-transition actions for a given
    (status, current_level) pair from Vinit's real schema.
    Uses the real enum values — no invented status names.
    """
    return ALLOWED_ACTIONS_BY_STATE.get((status, current_level), [])

# ─── Authority matrix ─────────────────────────────────────────────────────────
# Indian Police Hierarchy: operator, dsp, sp, ig
#
# Maps role -> set of actions that role is allowed to perform.
AUTHORITY_MATRIX: dict[OfficerRole, set[str]] = {
    OfficerRole.operator: {"ai_triage", "assign_operator", "escalate_to_dsp", "resolve"},
    OfficerRole.dsp:      {"escalate_to_sp", "investigate", "resolve", "confirm_critical"},
    OfficerRole.sp:       {"escalate_to_ig", "resolve", "confirm_critical"},
    OfficerRole.ig:       {"direct_intervention", "resolve", "close"},
}

def check_authority(role: OfficerRole, action: str, status: CaseStatus, current_level: OfficerRole | None) -> bool:
    """
    Returns True if `role` is allowed to perform `action` given the case's
    current (status, current_level) pair.

    Signature agreed with Aditya:
        check_authority(role: OfficerRole, action: str,
                        status: CaseStatus, current_level: OfficerRole | None)

    Both role and current_level must use the 9-value OfficerRole enum from
    Vinit's models.py — no separate 'responderType' field.
    """
    allowed_for_state = get_allowed_actions(status, current_level)
    allowed_for_role = AUTHORITY_MATRIX.get(role, set())
    return action in allowed_for_state and action in allowed_for_role

# ─── Tier determination ───────────────────────────────────────────────────────
def determine_risk_tier(svi_score: float, flags: list[dict]) -> RiskTier:
    """
    Determines risk tier from SVI score + flag overrides.
    Never downgrades — only upgrades.
    """
    if svi_score <= TIER_THRESHOLDS["low_max"]:
        base_tier = RiskTier.low
    elif svi_score <= TIER_THRESHOLDS["moderate_max"]:
        base_tier = RiskTier.moderate
    elif svi_score <= TIER_THRESHOLDS["high_max"]:
        base_tier = RiskTier.high
    else:
        base_tier = RiskTier.critical

    tier_ranks = {
        RiskTier.low: 1,
        RiskTier.moderate: 2,
        RiskTier.high: 3,
        RiskTier.critical: 4,
    }
    current_tier = base_tier

    for flag in flags:
        flag_name = flag.get("name", "").lower()
        if flag_name in FLAG_TIER_OVERRIDES:
            override = FLAG_TIER_OVERRIDES[flag_name]
            if tier_ranks[override] > tier_ranks[current_tier]:
                current_tier = override

    return current_tier


# ─── Action recommendations ───────────────────────────────────────────────────
def recommend_actions(risk_tier: RiskTier, flags: list[dict]) -> list[str]:
    """
    Recommends specific support actions based on tier + flag contents.
    Returns a sorted, deduplicated list.
    Action strings match the human-readable labels used in Pawan's UI.
    """
    actions: set[str] = set()
    flag_names = [f.get("name", "").lower() for f in flags]

    if risk_tier in (RiskTier.moderate, RiskTier.high, RiskTier.critical):
        actions.add("counselling")

    if risk_tier in (RiskTier.high, RiskTier.critical):
        actions.add("police intervention")

    if risk_tier == RiskTier.critical:
        actions.add("emergency support")

    if "suicidal_ideation" in flag_names:
        actions.update(["medical assistance", "emergency support", "counselling"])

    if "intimidation" in flag_names or "threat" in flag_names:
        actions.update(["legal aid", "police intervention", "witness protection"])

    if "physical_abuse" in flag_names or "violence" in flag_names:
        actions.update(["medical assistance", "police intervention"])

    if "silent_distress_signal" in flag_names:
        actions.update(["emergency support", "police intervention", "witness protection"])

    if not actions:
        actions.add("counselling")

    return sorted(actions)


# ─── Nested-object flags shape (shared contract with Vedika & Vinit) ─────────
def build_flags_db_object(flags: list[dict]) -> dict:
    """
    Converts Vedika's list-of-flag-objects into the nested-object shape
    agreed for the DB `flags` JSON column:

        {
            "trauma":            {"present": true, "confidence": 0.82, "signals": ["long pause: 4.2s"]},
            "suicidal_ideation": {"present": true, "confidence": 0.91, "signals": ["keyword match"]},
            ...
        }

    This shape is now FINAL and shared with:
      - Vedika  (produces it)
      - Vinit   (stores it — flags JSON column has no enforced schema)
      - Pawan   (renders it in Case File detail panel)
      - Pushp   (reads confidence/signals in test assertions)
    """
    result: dict = {}
    for f in flags:
        name = f.get("name", "").lower()
        if not name:
            continue
        result[name] = {
            "present": True,
            "confidence": round(float(f.get("confidence", 0.0)), 4),
            "signals": f.get("signals", []),
        }
    return result


# ─── Routing-reason text ──────────────────────────────────────────────────────
def build_routing_reason(
    risk_tier: RiskTier,
    actions: list[str],
    status: CaseStatus,
    current_level: OfficerRole | None,
    flags: list[dict],
) -> str:
    """
    Generates a routing-reason string for audit logs and the copilot panel.
    Uses real (status, current_level) from Vinit's schema — never invented names.
    """
    level_str = current_level.value if current_level else "unassigned"
    flag_names = [f.get("name") for f in flags if f.get("name")]

    reason = (
        f"Case is currently {status.value} at level '{level_str}'. "
        f"AI assessed risk as {risk_tier.value.upper()}"
    )
    if flag_names:
        reason += f" based on flags: {', '.join(flag_names)}"
    if actions:
        reason += f". Recommended: {', '.join(actions)}."
    return reason
