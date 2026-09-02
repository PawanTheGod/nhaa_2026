"""
Perception-to-SVI Aggregation Engine & Multimodal Fusion Pipeline
==============================================================================
NHAA 14566 / SIH 26093 - AI Perception Layer
==============================================================================
SAFETY & PROTOTYPE DISCLAIMER:
- The Stress Vulnerability Index (SVI 0-100) is a PROTOTYPE risk-scoring mechanism.
- IT IS NOT A CLINICALLY VALIDATED PSYCHOLOGICAL SCORE OR MEDICAL DIAGNOSIS.
- Must be validated on helpline caller datasets prior to operational deployment.
==============================================================================
"""

import time
from typing import Dict, List, Tuple, Optional, Any, Union

from config import config
from perception.explainability import build_unified_evidence_report
from perception.fusion.schemas import (
    SVIResult,
    SourcesMap,
    ModelMetadataMap,
    PerceptionPayload
)

SVI_SAFETY_DISCLAIMER = (
    "PROTOTYPE PERCEPTION SIGNAL: The SVI score (0-100) and risk tiers represent an automated triage "
    "risk prioritization estimate. IT DOES NOT CONSTITUTE A CLINICAL DIAGNOSIS OR PSYCHOLOGICAL ASSESMENT. "
    "Final triage decisions and emergency responses must be evaluated by human helpline officers."
)


def determine_risk_tier(score: int) -> str:
    """
    Lookup risk tier from configurable SVIConfig thresholds.
    0-24 = Low, 25-49 = Moderate, 50-74 = High, 75-100 = Critical
    """
    s_cfg = config.svi
    if score <= s_cfg.tier_low_max:
        return "Low"
    elif score <= s_cfg.tier_moderate_max:
        return "Moderate"
    elif score <= s_cfg.tier_high_max:
        return "High"
    else:
        return "Critical"


def calculate_svi(
    flags: List[Dict[str, Any]],
    acoustic_signals: Optional[Dict[str, Any]] = None,
    ser_emotion: Optional[Dict[str, Any]] = None,
    has_speech: bool = True,
    has_text: bool = True
) -> Tuple[int, str]:
    """
    Computes composite Stress Vulnerability Index (SVI) score (0-100) and risk tier.
    
    Formula Component Contributions:
    1. Text Distress Flags (Max 50 pts): sum(Weight * Confidence)
    2. Speech Emotion Neural Probability (Max 30 pts): Weight * Confidence
    3. Acoustic Feature Stress (Max 20 pts): Pause duration + pitch std + silence ratio
    
    Missing Data Scaling:
    - Text-Only: SVI = min(100, S_text * 2.0)
    - Audio-Only: SVI = min(100, (S_emotion + S_acoustic) * 2.0)
    - Multimodal: SVI = S_text + S_emotion + S_acoustic
    """
    s_cfg = config.svi
    acoustic_signals = acoustic_signals or {}
    ser_emotion = ser_emotion or {}

    # 1. Text Distress Contribution (Max 75 pts for severe life threats)
    text_score = 0.0
    has_severe_threat = False
    for flag in flags:
        fname = flag.get("name", "").lower()
        fconf = float(flag.get("confidence", 0.50))
        weight = s_cfg.flag_weights.get(fname, 20.0)
        text_score += (weight * fconf)
        if fname in ("intimidation", "suicidal_ideation", "trauma") and fconf >= 0.70:
            has_severe_threat = True

    text_score = min(75.0, text_score)

    # 2. Speech Emotion Contribution (Max 30 pts)
    ser_label = ser_emotion.get("label", "neutral").lower()
    ser_conf = float(ser_emotion.get("confidence", 0.50))
    em_weight = s_cfg.emotion_weights.get(ser_label, 0.0)
    emotion_score = min(30.0, em_weight * ser_conf)

    # 3. Acoustic Feature Stress Contribution (Max 20 pts)
    acoustic_score = 0.0
    
    # Extended pause contribution (Max 8 pts)
    max_pause = float(acoustic_signals.get("max_pause_duration_seconds", 0.0))
    if max_pause >= 3.5:
        acoustic_score += 8.0
    elif max_pause >= 2.0:
        acoustic_score += 4.0

    # Pitch variation contribution (Max 7 pts)
    pitch_var = float(acoustic_signals.get("pitch_variation", 0.0))
    pitch_std = float(acoustic_signals.get("pitch_std_hz", 0.0))
    if pitch_var >= 0.25 or pitch_std >= 50.0:
        acoustic_score += 7.0
    elif pitch_std >= 35.0:
        acoustic_score += 4.0

    # Silence ratio contribution (Max 5 pts)
    silence_ratio = float(acoustic_signals.get("silence_ratio", 0.0))
    if silence_ratio >= 0.40:
        acoustic_score += 5.0

    acoustic_score = min(20.0, acoustic_score)

    # 4. Multi-channel score aggregation & scaling
    if has_speech and has_text:
        raw_svi = text_score + emotion_score + acoustic_score
    elif has_text and not has_speech:
        # Scale text score to 0-100 range
        raw_svi = min(100.0, text_score * 1.33)
    elif has_speech and not has_text:
        # Scale audio score to 0-100 range
        raw_svi = min(100.0, (emotion_score + acoustic_score) * 2.0)
    else:
        raw_svi = 0.0

    # Severe threat safety boost (Ensures life-threatening complaints are never downgraded below High Risk 65+)
    if has_severe_threat and raw_svi < 65.0:
        raw_svi = max(65.0, text_score + 10.0)

    final_score = int(round(max(float(s_cfg.min_svi_score), min(float(s_cfg.max_svi_score), float(raw_svi)))))
    tier = determine_risk_tier(final_score)

    return final_score, tier


class PerceptionFusionEngine:
    """Master Multimodal Perception & SVI Aggregation Engine."""

    def __init__(self):
        pass

    def process_case(
        self,
        stt_result: Optional[Dict[str, Any]] = None,
        ser_result: Optional[Dict[str, Any]] = None,
        speech_features_result: Optional[Dict[str, Any]] = None,
        text_distress_result: Optional[Dict[str, Any]] = None,
        case_id: Optional[str] = None
    ) -> PerceptionPayload:
        """
        Combines all perception layer outputs into a standardized PerceptionPayload.
        """
        start_time = time.time()

        has_speech = bool(
            stt_result and stt_result.get("success", False) or
            speech_features_result and speech_features_result.get("success", False)
        )
        has_text = bool(
            text_distress_result and text_distress_result.get("success", False)
        )

        # Build Explainable Evidence Report
        evidence_report = build_unified_evidence_report(
            stt_result=stt_result,
            ser_result=ser_result,
            speech_features_result=speech_features_result,
            text_distress_result=text_distress_result
        )

        # Extract SER emotion dict and acoustic dict for SVI calculation
        ser_emotion = ser_result.get("emotion", {}) if ser_result else {}
        ac_signals = ser_result.get("acoustic_signals", {}) if ser_result else {}
        if speech_features_result and speech_features_result.get("success", False):
            ac_signals.update({
                "max_pause_duration_seconds": speech_features_result.get("pauses", {}).get("max_duration_seconds", 0.0),
                "pitch_variation": speech_features_result.get("pitch", {}).get("pitch_variation", 0.0),
                "pitch_std_hz": speech_features_result.get("pitch", {}).get("std_hz", 0.0),
                "silence_ratio": speech_features_result.get("pauses", {}).get("silence_ratio", 0.0)
            })

        # Calculate SVI score and risk tier
        flags_list = evidence_report.get("flags", [])
        svi_score, risk_tier = calculate_svi(
            flags=flags_list,
            acoustic_signals=ac_signals,
            ser_emotion=ser_emotion,
            has_speech=has_speech,
            has_text=has_text
        )

        # Collect Model Metadata
        stt_m = stt_result.get("model_name") if stt_result else None
        ser_m = ser_result.get("model_name") if ser_result else None
        text_m = text_distress_result.get("model") if text_distress_result else None

        exec_time = round(time.time() - start_time, 3)

        return PerceptionPayload(
            schema_version=config.svi.schema_version,
            case_id=case_id,
            timestamp=round(time.time(), 3),
            svi=SVIResult(score=svi_score, risk_tier=risk_tier),
            stt_transcript=stt_result.get("transcript") if stt_result else None,
            flags=evidence_report.get("flags", []),
            sources=SourcesMap(speech=has_speech, text=has_text),
            raw_measurements=evidence_report.get("raw_measurements", []),
            model_predictions=evidence_report.get("model_predictions", []),
            model_metadata=ModelMetadataMap(
                stt_model=stt_m,
                ser_model=ser_m,
                text_model=text_m,
                execution_time_sec=exec_time
            ),
            safety_disclaimer=SVI_SAFETY_DISCLAIMER
        )


def compute_perception_fusion(
    stt_result: Optional[Dict[str, Any]] = None,
    ser_result: Optional[Dict[str, Any]] = None,
    speech_features_result: Optional[Dict[str, Any]] = None,
    text_distress_result: Optional[Dict[str, Any]] = None,
    case_id: Optional[str] = None
) -> Dict[str, Any]:
    """Convenience function returning dictionary payload."""
    engine = PerceptionFusionEngine()
    payload = engine.process_case(
        stt_result=stt_result,
        ser_result=ser_result,
        speech_features_result=speech_features_result,
        text_distress_result=text_distress_result,
        case_id=case_id
    )
    return payload.model_dump()
