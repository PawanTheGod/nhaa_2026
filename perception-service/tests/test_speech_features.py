"""
Automated Unit Test Suite for Acoustic Speech-Feature Extractor Module
==============================================================================
Tests pitch tracking, RMS energy dynamics, pause interval extraction,
and input validation checks using synthetic audio files.
==============================================================================
"""

import os
import unittest
from utils.audio_utils import generate_synthetic_audio
from perception.speech_features import extract_acoustic_features, AcousticFeatureExtractor

class TestSpeechFeatures(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.valid_wav = "temp_test_speech_features.wav"
        cls.empty_wav = "temp_test_empty_features.wav"
        cls.invalid_txt = "temp_test_invalid.txt"

        # Generate 4.0s synthetic audio with 440 Hz tone and a 1.0s pause interval
        generate_synthetic_audio(
            cls.valid_wav,
            duration_sec=4.0,
            sample_rate=16000,
            frequency=440.0,
            add_pauses=True
        )

        with open(cls.empty_wav, "wb") as f:
            pass
        with open(cls.invalid_txt, "w") as f:
            f.write("invalid content")

    @classmethod
    def tearDownClass(cls):
        for path in [cls.valid_wav, cls.empty_wav, cls.invalid_txt]:
            if os.path.exists(path):
                os.remove(path)

    def test_extract_features_valid_audio(self):
        res = extract_acoustic_features(self.valid_wav)

        self.assertTrue(res["success"])
        self.assertIsNone(res["error"])
        self.assertAlmostEqual(res["duration_seconds"], 4.0, delta=0.2)

        # Pitch assertions
        pitch = res["pitch"]
        self.assertIn("mean_hz", pitch)
        self.assertIn("std_hz", pitch)
        self.assertIn("range_hz", pitch)
        self.assertGreater(pitch["mean_hz"], 100.0)

        # Energy assertions
        energy = res["energy"]
        self.assertIn("mean_rms", energy)
        self.assertIn("std_rms", energy)
        self.assertGreater(energy["mean_rms"], 0.0)

        # Pause assertions
        pauses = res["pauses"]
        self.assertGreaterEqual(pauses["count"], 1)
        self.assertGreaterEqual(pauses["max_duration_seconds"], 0.5)
        self.assertGreater(pauses["silence_ratio"], 0.1)

        # Speech characteristics assertions
        speech_chars = res["speech_characteristics"]
        self.assertIn("zero_crossing_rate_mean", speech_chars)
        self.assertIn("speaking_rate_proxy", speech_chars)

    def test_missing_file_validation(self):
        res = extract_acoustic_features("non_existent_audio.wav")
        self.assertFalse(res["success"])
        self.assertIn("Audio file not found", res["error"])

    def test_unsupported_format_validation(self):
        res = extract_acoustic_features(self.invalid_txt)
        self.assertFalse(res["success"])
        self.assertIn("Unsupported format", res["error"])

    def test_empty_file_validation(self):
        res = extract_acoustic_features(self.empty_wav)
        self.assertFalse(res["success"])
        self.assertIn("Audio file is empty", res["error"])

if __name__ == "__main__":
    unittest.main()
