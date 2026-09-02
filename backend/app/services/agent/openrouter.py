import os
import json
import httpx
from typing import List

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# Using an open/free model per the requirements
DEFAULT_MODEL = "meta-llama/llama-3-8b-instruct:free"

SYSTEM_PROMPT = """
You are the explanation-generation component of a government helpline's AI triage system.
Your job is to provide a short, specific, plain-language explanation for why a case was assigned a certain risk tier and why specific actions were recommended.
You will be given the SVI score, the assigned risk tier, the recommended actions, and a list of specific 'flags' and their underlying 'signals'.

RULES:
1. Keep it short (2-3 sentences max).
2. Explicitly reference the actual signals and flags passed in (e.g. "The 4.2s long pause and threat language keyword match triggered an intimidation flag...").
3. NEVER use generic phrases like "The AI flagged this case" or "Based on the AI model". Write as if you are summarizing the evidence directly.
4. Output ONLY the explanation text, nothing else.
"""

async def generate_explanation(
    svi_score: float, 
    risk_tier: str, 
    actions: List[str], 
    flags: List[dict]
) -> str:
    """
    Calls OpenRouter API to generate a plain-text explanation.
    """
    if not OPENROUTER_API_KEY:
        # Fallback if no API key is provided, so the system doesn't crash
        # during local development without a key.
        return _generate_fallback_explanation(svi_score, risk_tier, actions, flags)

    prompt = (
        f"SVI Score: {svi_score}\n"
        f"Assigned Risk Tier: {risk_tier}\n"
        f"Recommended Actions: {', '.join(actions) if actions else 'None'}\n"
        f"Flags and Signals:\n"
    )
    
    for f in flags:
        name = f.get("name", "Unknown")
        conf = f.get("confidence", 0.0)
        signals = f.get("signals", [])
        prompt += f"- {name} (confidence {conf}): {', '.join(signals)}\n"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT.strip()},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 150
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"OpenRouter API error: {e}")
        return _generate_fallback_explanation(svi_score, risk_tier, actions, flags)

def _generate_fallback_explanation(svi_score, risk_tier, actions, flags) -> str:
    """Fallback if API fails or is unconfigured."""
    flag_names = [f.get('name') for f in flags]
    explanation = f"Case assigned to {risk_tier} tier with SVI {svi_score}."
    if flag_names:
        explanation += f" Detected flags: {', '.join(flag_names)}."
    if actions:
        explanation += f" Recommended: {', '.join(actions)}."
    return explanation
