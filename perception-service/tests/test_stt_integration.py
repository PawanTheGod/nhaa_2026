"""
Manual Integration Test for STT Module
==============================================================================
Runs real Whisper inference against sample WAV audio files.
==============================================================================
"""

import os
import unittest
from perception.stt.stt_module import audio_to_transcript
from utils.audio_utils import generate_synthetic_audio

class TestSTTIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.makedirs("samples", exist_ok=True)
        cls.test_wav = "samples/test_integration.wav"
        generate_synthetic_audio(cls.test_wav, duration_sec=3.0, sample_rate=16000)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_wav):
            os.remove(cls.test_wav)

    def test_real_transcription_end_to_end(self):
        print("\n[Integration Test] Running real Whisper model inference...")
        result = audio_to_transcript(self.test_wav, language="en", model_name="tiny")
        
        self.assertTrue(result["success"])
        self.assertIsNone(result["error"])
        self.assertEqual(result["detected_language"], "en")
        self.assertIn("TESTED (English)", result["tested_status"])
        self.assertGreaterEqual(result["processing_time"], 0.0)
        self.assertIn("whisper-tiny", result["model_name"])
        print("[Integration Test SUCCESS] Processing time:", result["processing_time"], "s")

if __name__ == "__main__":
    unittest.main()
