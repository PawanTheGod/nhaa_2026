"""
Unit and Integration Tests for STT Pipeline
"""

import os
import pytest
import unittest
from utils.audio_utils import generate_synthetic_audio, get_audio_duration
from stt.stt_pipeline import SpeechToTextPipeline, STTResult
from config import TESTED_LANGUAGES, UNTESTED_LANGUAGES

class TestSTTPipeline(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.test_audio_path = "temp_test_stt.wav"
        generate_synthetic_audio(cls.test_audio_path, duration_sec=3.0, sample_rate=16000)
        cls.pipeline = SpeechToTextPipeline(model_size="tiny", device="cpu")

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_audio_path):
            os.remove(cls.test_audio_path)

    def test_audio_duration_utility(self):
        duration = get_audio_duration(self.test_audio_path)
        self.assertAlmostEqual(duration, 3.0, delta=0.1)

    def test_transcribe_english(self):
        result = self.pipeline.transcribe(self.test_audio_path, language="en")
        self.assertIsInstance(result, STTResult)
        self.assertEqual(result.language, "en")
        self.assertIn("TESTED (English)", result.tested_status)
        self.assertGreaterEqual(result.confidence_score, 0.0)
        self.assertLessEqual(result.confidence_score, 1.0)

    def test_transcribe_hindi(self):
        result = self.pipeline.transcribe(self.test_audio_path, language="hi")
        self.assertEqual(result.language, "hi")
        self.assertIn("TESTED (Hindi)", result.tested_status)

    def test_transcribe_tamil(self):
        result = self.pipeline.transcribe(self.test_audio_path, language="ta")
        self.assertEqual(result.language, "ta")
        self.assertIn("TESTED (Tamil)", result.tested_status)

    def test_untested_language_flagging(self):
        result = self.pipeline.transcribe(self.test_audio_path, language="bn")
        self.assertEqual(result.language, "bn")
        self.assertIn("UNTESTED (Bengali)", result.tested_status)

    def test_mongo_dict_format(self):
        result = self.pipeline.transcribe(self.test_audio_path, language="hi")
        mongo_doc = result.to_mongo_dict()
        self.assertIn("transcript", mongo_doc)
        self.assertIn("language", mongo_doc)
        self.assertIn("tested_status", mongo_doc)
        self.assertIn("safety_disclaimer", mongo_doc)

if __name__ == "__main__":
    unittest.main()
