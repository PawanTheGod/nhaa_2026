"""
Unit Test Suite for Speech Emotion Recognition (SER) Module using Mocks
==============================================================================
Uses unittest.mock to test validation logic, output schemas, acoustic signal
integration, and safety disclosures without neural network inference overhead.
==============================================================================
"""

import os
import unittest
from unittest.mock import MagicMock, patch
from perception.ser.ser_module import audio_to_emotion, SpeechEmotionRecognizer
from utils.audio_utils import generate_synthetic_audio

class TestSERUnit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.valid_wav = "temp_ser_unit_valid.wav"
        cls.empty_wav = "temp_ser_unit_empty.wav"
        cls.invalid_txt = "temp_ser_unit_invalid.txt"

        generate_synthetic_audio(cls.valid_wav, duration_sec=2.0)
        with open(cls.empty_wav, "wb") as f:
            pass
        with open(cls.invalid_txt, "w") as f:
            f.write("text content")

    @classmethod
    def tearDownClass(cls):
        for path in [cls.valid_wav, cls.empty_wav, cls.invalid_txt]:
            if os.path.exists(path):
                os.remove(path)

    def test_missing_file_validation(self):
        res = audio_to_emotion("non_existent_file.wav")
        self.assertFalse(res["success"])
        self.assertIn("Audio file not found", res["error"])
        self.assertEqual(res["emotion"]["label"], "unknown")

    def test_unsupported_format_validation(self):
        res = audio_to_emotion(self.invalid_txt)
        self.assertFalse(res["success"])
        self.assertIn("Unsupported format", res["error"])

    def test_empty_file_validation(self):
        res = audio_to_emotion(self.empty_wav)
        self.assertFalse(res["success"])
        self.assertIn("Audio file is empty", res["error"])

    @patch("perception.ser.ser_module.get_ser_recognizer")
    @patch("perception.ser.ser_module.extract_acoustic_features")
    def test_mocked_emotion_prediction(self, mock_extract, mock_get_recognizer):
        # Setup mock acoustic features
        mock_extract.return_value = {
            "success": True,
            "pitch": {"pitch_variation": 0.15, "mean_hz": 210.0, "std_hz": 31.5, "range_hz": 110.0},
            "energy": {"mean_rms": 0.25, "std_rms": 0.12},
            "pauses": {"count": 2, "mean_duration_seconds": 0.75, "max_duration_seconds": 1.2, "silence_ratio": 0.25},
            "speech_characteristics": {"speaking_rate_proxy": 1.2}
        }

        # Setup mock recognizer
        mock_recognizer = MagicMock()
        mock_recognizer.predict.return_value = [
            {"label": "fear", "confidence": 0.81},
            {"label": "sad", "confidence": 0.12},
            {"label": "neutral", "confidence": 0.07}
        ]
        mock_get_recognizer.return_value = mock_recognizer

        res = audio_to_emotion(self.valid_wav)

        self.assertTrue(res["success"])
        self.assertEqual(res["emotion"]["label"], "fear")
        self.assertEqual(res["emotion"]["confidence"], 0.81)
        self.assertEqual(len(res["top_predictions"]), 3)

        # Assert named acoustic signals presence
        ac = res["acoustic_signals"]
        self.assertEqual(ac["pitch_variation"], 0.15)
        self.assertEqual(ac["pause_count"], 2)
        self.assertEqual(ac["mean_pause_duration_seconds"], 0.75)
        self.assertEqual(ac["energy_variation"], 0.12)

        # Assert ethical safety disclaimer presence
        self.assertIn("fear ≠ trauma", res["safety_disclaimer"])

if __name__ == "__main__":
    unittest.main()
