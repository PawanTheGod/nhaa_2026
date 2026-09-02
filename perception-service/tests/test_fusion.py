"""
Unit Test Suite for Perception-to-SVI Fusion Engine
==============================================================================
Tests risk tier boundaries (Low, Moderate, High, Critical), missing speech/text
channel scaling, SVI scoring calculations, and Pydantic schema validation.
==============================================================================
"""

import unittest
from perception.fusion.svi_engine import (
    determine_risk_tier,
    calculate_svi,
    compute_perception_fusion,
    PerceptionFusionEngine
)
from perception.fusion.schemas import SVIResult, PerceptionPayload

class TestFusionEngine(unittest.TestCase):

    def test_risk_tier_boundaries(self):
        """Boundary tests for all 4 risk tiers (Low, Moderate, High, Critical)."""
        self.assertEqual(determine_risk_tier(0), "Low")
        self.assertEqual(determine_risk_tier(24), "Low")
        self.assertEqual(determine_risk_tier(25), "Moderate")
        self.assertEqual(determine_risk_tier(49), "Moderate")
        self.assertEqual(determine_risk_tier(50), "High")
        self.assertEqual(determine_risk_tier(74), "High")
        self.assertEqual(determine_risk_tier(75), "Critical")
        self.assertEqual(determine_risk_tier(100), "Critical")

    def test_multimodal_svi_calculation(self):
        sample_flags = [
            {"name": "suicidal_ideation", "confidence": 0.90},
            {"name": "intimidation", "confidence": 0.85}
        ]
        ac_signals = {
            "max_pause_duration_seconds": 4.0,
            "pitch_variation": 0.30,
            "silence_ratio": 0.45
        }
        ser_emotion = {"label": "fearful", "confidence": 0.85}

        score, tier = calculate_svi(
            flags=sample_flags,
            acoustic_signals=ac_signals,
            ser_emotion=ser_emotion,
            has_speech=True,
            has_text=True
        )

        self.assertGreaterEqual(score, 75)
        self.assertEqual(tier, "Critical")

    def test_text_only_call_handling(self):
        sample_flags = [{"name": "fear", "confidence": 0.80}]
        
        score, tier = calculate_svi(
            flags=sample_flags,
            has_speech=False,
            has_text=True
        )

        self.assertGreater(score, 0)
        self.assertIn(tier, ["Low", "Moderate", "High", "Critical"])

        # Test compute_perception_fusion payload
        payload = compute_perception_fusion(
            text_distress_result={
                "success": True,
                "language": "en",
                "model": "google/muril-base-cased",
                "flags": [{"name": "fear", "confidence": 0.80, "signals": ["fear text"]}]
            }
        )

        self.assertFalse(payload["sources"]["speech"])
        self.assertTrue(payload["sources"]["text"])

    def test_audio_only_call_handling(self):
        ser_out = {
            "success": True,
            "emotion": {"label": "fearful", "confidence": 0.85},
            "model_name": "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition",
            "acoustic_signals": {
                "max_pause_duration_seconds": 3.8,
                "pitch_variation": 0.28,
                "silence_ratio": 0.42
            }
        }
        stt_out = {
            "success": True,
            "duration_sec": 4.0,
            "confidence_score": 0.92,
            "detected_language": "hi",
            "model_name": "whisper-tiny"
        }

        payload = compute_perception_fusion(
            stt_result=stt_out,
            ser_result=ser_out
        )

        self.assertTrue(payload["sources"]["speech"])
        self.assertFalse(payload["sources"]["text"])
        self.assertGreater(payload["svi"]["score"], 40)

    def test_pydantic_payload_validation(self):
        engine = PerceptionFusionEngine()
        payload_obj = engine.process_case(case_id="CASE-TEST-100")

        self.assertIsInstance(payload_obj, PerceptionPayload)
        self.assertEqual(payload_obj.schema_version, "1.0")
        self.assertEqual(payload_obj.case_id, "CASE-TEST-100")
        self.assertIn("PROTOTYPE PERCEPTION SIGNAL", payload_obj.safety_disclaimer)

if __name__ == "__main__":
    unittest.main()
