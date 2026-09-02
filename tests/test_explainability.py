"""
Unit Test Suite for Explainability & Evidence Generation Layer
==============================================================================
Tests source provenance validation, cross-modal evidence merging,
non-invention of evidence, and Pydantic schema validation.
==============================================================================
"""

import unittest
from perception.explainability import (
    speech_to_evidence,
    text_to_evidence,
    merge_evidence,
    build_unified_evidence_report,
    RawMeasurement,
    ModelPrediction,
    FlagEvidence,
    UnifiedEvidenceReport
)

class TestExplainability(unittest.TestCase):

    def setUp(self):
        self.sample_speech_features = {
            "success": True,
            "pitch": {"pitch_variation": 0.25, "std_hz": 45.0, "mean_hz": 210.0},
            "pauses": {"max_duration_seconds": 3.5, "count": 2, "silence_ratio": 0.40},
            "energy": {"std_rms": 0.18, "mean_rms": 0.25}
        }
        self.sample_ser = {
            "success": True,
            "emotion": {"label": "fearful", "confidence": 0.82},
            "model_name": "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
        }
        self.sample_stt = {
            "success": True,
            "duration_sec": 4.5,
            "confidence_score": 0.95,
            "detected_language": "en",
            "model_name": "whisper-tiny"
        }
        self.sample_text_distress = {
            "success": True,
            "language": "en",
            "model": "google/muril-base-cased",
            "flags": [
                {
                    "name": "fear",
                    "confidence": 0.78,
                    "signals": ["Keyword match: 'terrified' in text"]
                },
                {
                    "name": "intimidation",
                    "confidence": 0.88,
                    "signals": ["Keyword match: 'threat' in text"]
                }
            ]
        }

    def test_speech_to_evidence_provenance(self):
        flags, raw, preds = speech_to_evidence(self.sample_stt, self.sample_ser, self.sample_speech_features)

        # Assert every raw measurement source is 'audio'
        for m in raw:
            self.assertEqual(m.source, "audio")

        # Assert every model prediction source is 'audio'
        for p in preds:
            self.assertEqual(p.source, "audio")

        # Assert every flag contains 'audio' in source
        for f in flags:
            self.assertIn("audio", f.source)

    def test_text_to_evidence_provenance(self):
        flags, raw, preds = text_to_evidence(self.sample_text_distress)

        for m in raw:
            self.assertEqual(m.source, "text")

        for p in preds:
            self.assertEqual(p.source, "text")

        for f in flags:
            self.assertIn("text", f.source)

    def test_cross_modal_merge_evidence(self):
        s_flags, s_raw, s_preds = speech_to_evidence(self.sample_stt, self.sample_ser, self.sample_speech_features)
        t_flags, t_raw, t_preds = text_to_evidence(self.sample_text_distress)

        report = merge_evidence(s_flags, s_raw, s_preds, t_flags, t_raw, t_preds)

        self.assertIsInstance(report, UnifiedEvidenceReport)
        
        # Check merged fear flag (present in both audio and text)
        fear_flag = next((f for f in report.flags if f.name == "fear"), None)
        self.assertIsNotNone(fear_flag)
        self.assertEqual(sorted(fear_flag.source), ["audio", "text"])
        self.assertGreater(fear_flag.confidence, 0.80)  # Fusion confidence boost
        self.assertGreater(len(fear_flag.signals), 1)

    def test_invalid_source_validation(self):
        with self.assertRaises(ValueError):
            RawMeasurement(source="video", type="test", name="test", value=1, unit="unit")

        with self.assertRaises(ValueError):
            FlagEvidence(name="fear", confidence=0.8, signals=["test"], source=["invalid_source"])

    def test_build_unified_evidence_report_convenience(self):
        report_dict = build_unified_evidence_report(
            stt_result=self.sample_stt,
            ser_result=self.sample_ser,
            speech_features_result=self.sample_speech_features,
            text_distress_result=self.sample_text_distress
        )

        self.assertIn("flags", report_dict)
        self.assertIn("raw_measurements", report_dict)
        self.assertIn("model_predictions", report_dict)
        self.assertIn("safety_disclaimer", report_dict)

if __name__ == "__main__":
    unittest.main()
