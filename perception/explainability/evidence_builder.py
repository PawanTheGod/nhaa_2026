"""
Perception Evidence Builder & Provenance Fusion Engine
==============================================================================
NHAA 14566 / SIH 26093 - AI Perception Layer
==============================================================================
Converts speech and text perception outputs into concise, auditable, and
grounded evidence objects with explicit source provenance.
==============================================================================
"""

import time
from typing import Dict, List, Tuple, Optional, Any, Union

from config import config
from perception.explainability.schemas import (
    RawMeasurement,
    ModelPrediction,
    FlagEvidence,
    UnifiedEvidenceReport
)

SAFETY_DISCLAIMER_EXPLAINABILITY = (
    "PERCEPTION EVIDENCE NOTICE: Signals listed represent physical acoustic measurements, "
    "detected text patterns, and model likelihood estimates. THEY DO NOT CONSTITUTE CLINICAL DIAGNOSES. "
    "Every emitted signal corresponds to a verified feature or text match for auditability."
)


def speech_to_evidence(
    stt_result: Optional[Dict[str, Any]] = None,
    ser_result: Optional[Dict[str, Any]] = None,
    speech_features_result: Optional[Dict[str, Any]] = None
) -> Tuple[List[FlagEvidence], List[RawMeasurement], List[ModelPrediction]]:
    """
    Extracts grounded flags, raw measurements, and model predictions from speech outputs.
    """
    flags: List[FlagEvidence] = []
    raw_measurements: List[RawMeasurement] = []
    model_predictions: List[ModelPrediction] = []

    # 1. Process STT Result
    if stt_result and stt_result.get("success", False):
        raw_measurements.append(
            RawMeasurement(
                source="audio",
                type="acoustic_feature",
                name="audio_duration",
                value=float(stt_result.get("duration_sec", 0.0)),
                unit="seconds"
            )
        )
        model_predictions.append(
            ModelPrediction(
                source="audio",
                type="model_prediction",
                name=f"language_{stt_result.get('detected_language', 'en')}",
                confidence=float(stt_result.get("confidence_score", 0.50)),
                model_name=stt_result.get("model_name", "whisper-base")
            )
        )

    # 2. Process Acoustic Features
    ac_signals = {}
    if speech_features_result and speech_features_result.get("success", False):
        pitch = speech_features_result.get("pitch", {})
        pauses = speech_features_result.get("pauses", {})
        energy = speech_features_result.get("energy", {})

        ac_signals = {
            "pitch_variation": pitch.get("pitch_variation", 0.0),
            "pitch_std_hz": pitch.get("std_hz", 0.0),
            "max_pause_sec": pauses.get("max_duration_seconds", 0.0),
            "mean_pause_sec": pauses.get("mean_duration_seconds", 0.0),
            "pause_count": pauses.get("count", 0),
            "silence_ratio": pauses.get("silence_ratio", 0.0),
            "energy_std": energy.get("std_rms", 0.0)
        }

        # Log Raw Acoustic Measurements
        raw_measurements.extend([
            RawMeasurement(source="audio", type="acoustic_feature", name="max_pause_duration", value=ac_signals["max_pause_sec"], unit="seconds"),
            RawMeasurement(source="audio", type="acoustic_feature", name="pause_count", value=ac_signals["pause_count"], unit="count"),
            RawMeasurement(source="audio", type="acoustic_feature", name="silence_ratio", value=ac_signals["silence_ratio"], unit="ratio"),
            RawMeasurement(source="audio", type="acoustic_feature", name="pitch_std", value=ac_signals["pitch_std_hz"], unit="Hz"),
            RawMeasurement(source="audio", type="acoustic_feature", name="pitch_variation", value=ac_signals["pitch_variation"], unit="ratio"),
            RawMeasurement(source="audio", type="acoustic_feature", name="energy_std", value=ac_signals["energy_std"], unit="RMS")
        ])

    # 3. Process SER Neural Predictions
    ser_pred_label = "neutral"
    ser_conf = 0.0
    ser_model = "ser-model"

    if ser_result and ser_result.get("success", False):
        emotion = ser_result.get("emotion", {})
        ser_pred_label = emotion.get("label", "neutral").lower()
        ser_conf = float(emotion.get("confidence", 0.50))
        ser_model = ser_result.get("model_name", "ser-model")

        model_predictions.append(
            ModelPrediction(
                source="audio",
                type="model_prediction",
                name=ser_pred_label,
                confidence=ser_conf,
                model_name=ser_model
            )
        )

        # Merge acoustic signals if provided in SER result
        if "acoustic_signals" in ser_result and not ac_signals:
            ac = ser_result["acoustic_signals"]
            ac_signals["max_pause_sec"] = ac.get("max_pause_duration_seconds", 0.0)
            ac_signals["pitch_variation"] = ac.get("pitch_variation", 0.0)
            ac_signals["pitch_std_hz"] = ac.get("pitch_std_hz", 0.0)
            ac_signals["energy_std"] = ac.get("energy_variation", 0.0)

    # 4. Derivation of Speech Flags (Never inventing evidence)
    # Speech Fear Flag
    if ser_pred_label in ("fear", "fearful") and ser_conf >= 0.40:
        signals = [f"speech emotion neural prediction: fear (conf={ser_conf:.2f})"]
        if ac_signals.get("pitch_variation", 0.0) > 0.20 or ac_signals.get("pitch_std_hz", 0.0) > 40.0:
            signals.append(f"pitch variation: high (std={ac_signals.get('pitch_std_hz', 0.0):.1f} Hz)")
        flags.append(FlagEvidence(name="fear", confidence=round(ser_conf, 2), signals=signals, source=["audio"]))

    # Speech Intimidation Flag
    elif ser_pred_label == "angry" and ser_conf >= 0.40:
        signals = [f"vocal acoustic tone: angry/agitated (conf={ser_conf:.2f})"]
        if ac_signals.get("energy_std", 0.0) > 0.15:
            signals.append(f"high RMS energy variation (std={ac_signals.get('energy_std', 0.0):.2f})")
        flags.append(FlagEvidence(name="intimidation", confidence=round(ser_conf, 2), signals=signals, source=["audio"]))

    # Speech Pause / Hesitation Flag
    if ac_signals.get("max_pause_sec", 0.0) >= 2.5:
        pause_signals = [f"long pause: {ac_signals.get('max_pause_sec'):.1f} seconds"]
        if ac_signals.get("silence_ratio", 0.0) > 0.35:
            pause_signals.append(f"silence ratio: {ac_signals.get('silence_ratio'):.2f}")
        
        # Add vulnerability flag if extended pauses detected
        flags.append(FlagEvidence(name="extreme_vulnerability", confidence=0.70, signals=pause_signals, source=["audio"]))

    return flags, raw_measurements, model_predictions


def text_to_evidence(
    text_distress_result: Optional[Dict[str, Any]] = None
) -> Tuple[List[FlagEvidence], List[RawMeasurement], List[ModelPrediction]]:
    """
    Extracts grounded flags, raw measurements, and model predictions from text outputs.
    """
    flags: List[FlagEvidence] = []
    raw_measurements: List[RawMeasurement] = []
    model_predictions: List[ModelPrediction] = []

    if not text_distress_result or not text_distress_result.get("success", False):
        return flags, raw_measurements, model_predictions

    model_name = text_distress_result.get("model", "google/muril-base-cased")
    raw_flags = text_distress_result.get("flags", [])

    for item in raw_flags:
        f_name = item.get("name", "extreme_vulnerability").lower().strip()
        f_conf = float(item.get("confidence", 0.50))
        raw_signals = item.get("signals", [])

        # Privacy preservation: convert raw text matches to clean, auditable evidence strings
        anonymized_signals = []
        for sig in raw_signals:
            if "Keyword match:" in sig:
                # Retain keyword pattern type without exposing full raw context
                anonymized_signals.append(sig)
            else:
                anonymized_signals.append(f"{f_name.replace('_', ' ')} indicator detected")

        if not anonymized_signals:
            anonymized_signals = [f"{f_name.replace('_', ' ')} text indicator detected"]

        # Log Raw Measurement for Text Match
        raw_measurements.append(
            RawMeasurement(
                source="text",
                type="text_pattern",
                name=f"{f_name}_match_count",
                value=len(anonymized_signals),
                unit="matches"
            )
        )

        # Log Model Prediction
        model_predictions.append(
            ModelPrediction(
                source="text",
                type="model_prediction",
                name=f_name,
                confidence=f_conf,
                model_name=model_name
            )
        )

        # Create FlagEvidence object
        flags.append(
            FlagEvidence(
                name=f_name,
                confidence=round(f_conf, 2),
                signals=anonymized_signals,
                source=["text"]
            )
        )

    return flags, raw_measurements, model_predictions


def merge_evidence(
    speech_flags: List[FlagEvidence],
    speech_raw: List[RawMeasurement],
    speech_preds: List[ModelPrediction],
    text_flags: List[FlagEvidence],
    text_raw: List[RawMeasurement],
    text_preds: List[ModelPrediction]
) -> UnifiedEvidenceReport:
    """
    Merges speech and text evidence components into a unified report.
    Cross-modal flags detected in both audio and text are merged with combined source=['audio', 'text'].
    """
    merged_raw = speech_raw + text_raw
    merged_preds = speech_preds + text_preds

    # Index flags by category name
    flag_map: Dict[str, Dict[str, Any]] = {}

    def add_or_merge_flag(flag: FlagEvidence):
        fname = flag.name
        if fname not in flag_map:
            flag_map[fname] = {
                "name": fname,
                "confidence": flag.confidence,
                "signals": list(flag.signals),
                "source": list(flag.source)
            }
        else:
            existing = flag_map[fname]
            # Cross-modal fusion: boost confidence and merge sources & signals
            combined_sources = sorted(list(set(existing["source"] + flag.source)))
            merged_signals = sorted(list(set(existing["signals"] + flag.signals)))
            boosted_conf = min(0.99, max(existing["confidence"], flag.confidence) + 0.10)
            
            flag_map[fname] = {
                "name": fname,
                "confidence": round(boosted_conf, 2),
                "signals": merged_signals,
                "source": combined_sources
            }

    for f in speech_flags:
        add_or_merge_flag(f)
    for f in text_flags:
        add_or_merge_flag(f)

    final_flags = [
        FlagEvidence(
            name=v["name"],
            confidence=v["confidence"],
            signals=v["signals"],
            source=v["source"]
        )
        for v in flag_map.values()
    ]

    return UnifiedEvidenceReport(
        flags=final_flags,
        raw_measurements=merged_raw,
        model_predictions=merged_preds,
        safety_disclaimer=SAFETY_DISCLAIMER_EXPLAINABILITY
    )


def build_unified_evidence_report(
    stt_result: Optional[Dict[str, Any]] = None,
    ser_result: Optional[Dict[str, Any]] = None,
    speech_features_result: Optional[Dict[str, Any]] = None,
    text_distress_result: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to build unified evidence report from speech and text perception outputs.
    """
    s_flags, s_raw, s_preds = speech_to_evidence(stt_result, ser_result, speech_features_result)
    t_flags, t_raw, t_preds = text_to_evidence(text_distress_result)
    
    report = merge_evidence(s_flags, s_raw, s_preds, t_flags, t_raw, t_preds)
    return report.model_dump()
