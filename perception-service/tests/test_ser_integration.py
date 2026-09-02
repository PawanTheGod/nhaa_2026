"""
Manual Integration Test for Speech Emotion Recognition (SER) Module
==============================================================================
Runs real Wav2Vec2 neural model inference and acoustic feature extraction
against a sample WAV audio file.
==============================================================================
"""

import os
import unittest
from perception.ser.ser_module import audio_to_emotion
from utils.audio_utils import generate_synthetic_audio

class TestSERIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.makedirs("samples", exist_ok=True)
        cls.test_wav = "samples/test_ser_integration.wav"
        generate_synthetic_audio(cls.test_wav, duration_sec=3.0, sample_rate=16000)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_wav):
            os.remove(cls.test_wav)

    def test_real_emotion_recognition_end_to_end(self):
        print("\n[SER Integration Test] Running real Wav2Vec2 neural model inference...")
        result = audio_to_emotion(self.test_wav)

        self.assertTrue(result["success"])
        self.assertIsNone(result["error"])
        self.assertIn("label", result["emotion"])
        self.assertGreaterEqual(result["emotion"]["confidence"], 0.0)
        self.assertLessEqual(result["emotion"]["confidence"], 1.0)
        self.assertGreater(len(result["top_predictions"]), 0)

        ac = result["acoustic_signals"]
        self.assertIn("pitch_variation", ac)
        self.assertIn("pause_count", ac)
        self.assertIn("energy_variation", ac)

        print(f"[SER Integration Test SUCCESS] Predicted emotion: {result['emotion']['label']} ({result['emotion']['confidence']:.2f})")
        print("Processing time:", result["processing_time"], "s")

if __name__ == "__main__":
    unittest.main()
