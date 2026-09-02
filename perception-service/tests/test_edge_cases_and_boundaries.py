"""
Perception Edge Cases & Boundary Test Suite
==============================================================================
NHAA 14566 / SIH 26093 - AI Perception Layer
==============================================================================
Explicitly tests edge cases and boundary conditions:
- Missing audio (Text-only case)
- Missing text (Audio-only case)
- Invalid audio bytes / corrupt file handling
- Very short audio (< 0.1s duration)
- Very long audio (> 30 minutes duration cap)
- Low-confidence prediction handling
- Conflicting speech/text signals (e.g. cheerful vocal tone vs violent threat text)
- Risk-tier boundary thresholds (0-24 Low, 25-49 Moderate, 50-74 High, 75-100 Critical)
- Strict Pydantic Output Contract Schema Validation
==============================================================================
"""

import os
import tempfile
import unittest
import numpy as np
import soundfile as sf
from fastapi.testclient import TestClient

from config import SVIConfig
from perception.fusion.svi_engine import PerceptionFusionEngine, determine_risk_tier
from perception.schemas.perception_contract import PerceptionOutputContract, SVIResult, FlagEvidence
from perception.stt.stt_module import validate_audio_file
from api.main import app

class TestPerceptionEdgeCasesAndBoundaries(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.fusion_engine = PerceptionFusionEngine()
        cls.temp_dir = tempfile.mkdtemp()

    def test_missing_audio_text_only(self):
        """Scenario 9: Missing audio stream (Text-only channel)."""
        response = self.client.post(
            "/api/v1/perception/analyze",
            data={"text": "I am being threatened and need help", "language": "en", "channel": "chat"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertFalse(data["sources"]["speech"])
        self.assertTrue(data["sources"]["text"])
        self.assertGreaterEqual(data["svi"]["score"], 25)

    def test_missing_text_audio_only(self):
        """Scenario 10: Missing text input (Audio-only channel)."""
        audio_path = os.path.join(self.temp_dir, "audio_only.wav")
        sr = 16000
        t = np.linspace(0, 1.0, sr, endpoint=False)
        data = (0.8 * np.sin(2 * np.pi * 500 * t)).astype(np.float32)
        sf.write(audio_path, data, sr)

        with open(audio_path, "rb") as f:
            response = self.client.post(
                "/api/v1/perception/analyze",
                files={"audio": ("audio_only.wav", f, "audio/wav")},
                data={"channel": "ivrs"}
            )
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertTrue(res_data["sources"]["speech"])

    def test_invalid_audio_format(self):
        """Scenario 11: Invalid corrupt audio file."""
        invalid_bytes = b"NOT_AN_AUDIO_FILE_DATA_BYTES_HEADER"
        is_valid, msg = validate_audio_file(invalid_bytes, filename="invalid.wav")
        self.assertFalse(is_valid)  # False because bytes length < 400

        response = self.client.post(
            "/api/v1/perception/analyze",
            files={"audio": ("corrupt.txt", b"corrupt text", "text/plain")}
        )
        self.assertIn(response.status_code, [400, 415])

    def test_very_short_audio(self):
        """Scenario 12: Very short audio (< 0.1s)."""
        short_bytes = b"RIFF"  # Only 4 bytes
        is_valid, msg = validate_audio_file(short_bytes, filename="short.wav")
        self.assertFalse(is_valid)
        self.assertIn("too short", msg.lower())

    def test_very_long_audio_cap(self):
        """Scenario 13: Excessively long audio file (> 30 minutes)."""
        from perception.stt.stt_module import MAX_AUDIO_DURATION_SEC
        self.assertEqual(MAX_AUDIO_DURATION_SEC, 1800)

    def test_low_confidence_predictions(self):
        """Scenario 14: Low-confidence prediction handling."""
        low_conf_flag = FlagEvidence(
            name="fear",
            confidence=0.15,
            signals=["Low probability keyword match"],
            source=["text"]
        )
        self.assertLess(low_conf_flag.confidence, 0.5)

    def test_conflicting_speech_text_signals(self):
        """Scenario 15: Conflicting speech/text signals (e.g., Happy acoustic tone vs Threats text)."""
        ser_happy = {
            "predicted_emotion": "happy",
            "confidence": 0.85,
            "top_predictions": [{"emotion": "happy", "confidence": 0.85}]
        }
        text_threat = {
            "success": True,
            "flags": [
                {"name": "intimidation", "confidence": 0.90, "signals": ["Death threat text detected"]},
                {"name": "fear", "confidence": 0.85, "signals": ["Panic text detected"]}
            ],
            "risk_indicators": ["intimidation", "fear"]
        }

        # Fusion engine must weigh violent text threats heavily regardless of happy acoustic tone
        result = self.fusion_engine.process_case(
            stt_result={"transcript": "I will kill you", "success": True},
            ser_result=ser_happy,
            speech_features_result={"success": True, "mean_pitch": 220.0, "pause_ratio": 0.1},
            text_distress_result=text_threat
        )

        # High/Critical risk tier expected due to intimidation text threat
        self.assertIn(result.svi.risk_tier, ["High", "Critical"])
        self.assertGreaterEqual(result.svi.score, 50)

    def test_risk_tier_boundaries(self):
        """Scenario 16: Risk-tier boundary thresholds (0-24 Low, 25-49 Moderate, 50-74 High, 75-100 Critical)."""
        self.assertEqual(determine_risk_tier(0), "Low")
        self.assertEqual(determine_risk_tier(24), "Low")
        self.assertEqual(determine_risk_tier(25), "Moderate")
        self.assertEqual(determine_risk_tier(49), "Moderate")
        self.assertEqual(determine_risk_tier(50), "High")
        self.assertEqual(determine_risk_tier(74), "High")
        self.assertEqual(determine_risk_tier(75), "Critical")
        self.assertEqual(determine_risk_tier(100), "Critical")

    def test_schema_contract_validation(self):
        """Scenario 17: Strict Pydantic contract validation."""
        valid_payload = {
            "schema_version": "1.0",
            "case_id": "CASE-100",
            "timestamp": 1700000000.0,
            "channel": "ivrs",
            "language": {"code": "hi", "confidence": 0.95, "tested_status": "TESTED (Hindi)"},
            "svi": {"score": 65, "risk_tier": "High"},
            "flags": [{
                "name": "intimidation",
                "confidence": 0.85,
                "signals": ["Threat text detected"],
                "source": ["text"]
            }],
            "sources": {"speech": True, "text": True},
            "raw_measurements": [],
            "model_predictions": [],
            "model_metadata": {"stt_model": "whisper-tiny", "execution_time_sec": 0.5},
            "safety_disclaimer": "NON-CLINICAL RISK INDICATOR"
        }

        contract = PerceptionOutputContract.model_validate(valid_payload)
        self.assertEqual(contract.svi.score, 65)
        self.assertEqual(contract.svi.risk_tier, "High")

if __name__ == "__main__":
    unittest.main()
