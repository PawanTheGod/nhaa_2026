"""
Multilingual End-to-End Test Suite for AI Perception Layer
==============================================================================
NHAA 14566 / SIH 26093 - AI Perception Layer
==============================================================================
Validates full pipeline execution (Audio -> STT -> Acoustic -> SER -> Text -> SVI)
and metadata preservation for Proof-of-Concept Languages:
1. English (en)
2. Hindi (hi)
3. Marathi (mr)
==============================================================================
"""

import os
import tempfile
import unittest
import numpy as np
import soundfile as sf
from fastapi.testclient import TestClient

from config import LANGUAGE_CAPABILITY_MATRIX, TESTED_LANGUAGES
from perception.text_distress import text_to_distress_flags, get_text_classifier
from perception.schemas import PerceptionOutputContract
from api.main import app

class TestMultilingualPerception(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.classifier = get_text_classifier()
        
        # Create a synthetic 1-second 16kHz sine wave audio file for tests
        cls.temp_dir = tempfile.mkdtemp()
        cls.audio_path = os.path.join(cls.temp_dir, "multilingual_test.wav")
        sr = 16000
        t = np.linspace(0, 1.0, sr, endpoint=False)
        audio_data = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
        sf.write(cls.audio_path, audio_data, sr)

    def test_language_capability_matrix_completeness(self):
        """Verifies language capability matrix contains English, Hindi, and Marathi."""
        self.assertIn("en", LANGUAGE_CAPABILITY_MATRIX)
        self.assertIn("hi", LANGUAGE_CAPABILITY_MATRIX)
        self.assertIn("mr", LANGUAGE_CAPABILITY_MATRIX)

        for lang_code in ["en", "hi", "mr"]:
            info = LANGUAGE_CAPABILITY_MATRIX[lang_code]
            self.assertIn(info["stt"], ["SUPPORTED", "TESTED", "EXPERIMENTAL"])
            self.assertIn(info["ser"], ["SUPPORTED", "TESTED", "EXPERIMENTAL"])
            self.assertIn(info["text"], ["SUPPORTED", "TESTED", "EXPERIMENTAL"])

    def test_marathi_text_distress_classification(self):
        """Tests Marathi text distress keyword extraction and flag detection."""
        marathi_text = "मला मदत करा, मला मारहाण आणि धमकी दिली जात आहे, मी खूप घाबरलोय"
        res = self.classifier.classify(marathi_text, language="mr")

        self.assertEqual(res.language, "mr")
        flag_names = [f.name for f in res.flags]
        self.assertIn("intimidation", flag_names)
        self.assertIn("fear", flag_names)

    def test_hindi_text_distress_classification(self):
        """Tests Hindi text distress keyword extraction and flag detection."""
        hindi_text = "मुझे बचाओ, मुझे जान से मारने की धमकी मिल रही है और डर लग रहा है"
        res = self.classifier.classify(hindi_text, language="hi")

        self.assertEqual(res.language, "hi")
        flag_names = [f.name for f in res.flags]
        self.assertIn("intimidation", flag_names)
        self.assertIn("fear", flag_names)

    def test_english_text_distress_classification(self):
        """Tests English text distress keyword extraction and flag detection."""
        english_text = "Help me, I am terrified and receiving threats of violence"
        res = self.classifier.classify(english_text, language="en")

        self.assertEqual(res.language, "en")
        flag_names = [f.name for f in res.flags]
        self.assertIn("intimidation", flag_names)
        self.assertIn("fear", flag_names)

    def test_e2e_english_pipeline_endpoint(self):
        """Tests end-to-end pipeline execution for English."""
        with open(self.audio_path, "rb") as f:
            response = self.client.post(
                "/api/v1/perception/analyze",
                files={"audio_file": ("english_sample.wav", f, "audio/wav")},
                data={"text": "I am scared and need help immediately", "language": "en", "channel": "ivrs"}
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["language"]["code"], "en")
        self.assertEqual(data["language"]["name"], "English")
        self.assertIn("TESTED", data["language"]["tested_status"])
        self.assertGreaterEqual(data["svi"]["score"], 0)

    def test_e2e_hindi_pipeline_endpoint(self):
        """Tests end-to-end pipeline execution for Hindi."""
        with open(self.audio_path, "rb") as f:
            response = self.client.post(
                "/api/v1/perception/analyze",
                files={"audio_file": ("hindi_sample.wav", f, "audio/wav")},
                data={"text": "मुझे बहुत डर लग रहा है और धमकी दी गई है", "language": "hi", "channel": "ivrs"}
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["language"]["code"], "hi")
        self.assertEqual(data["language"]["name"], "Hindi")
        self.assertIn("TESTED", data["language"]["tested_status"])
        self.assertGreaterEqual(data["svi"]["score"], 0)

    def test_e2e_marathi_pipeline_endpoint(self):
        """Tests end-to-end pipeline execution for Marathi without silent English fallback."""
        with open(self.audio_path, "rb") as f:
            response = self.client.post(
                "/api/v1/perception/analyze",
                files={"audio_file": ("marathi_sample.wav", f, "audio/wav")},
                data={"text": "मला खूप भीती वाटत आहे आणि धमकी मिळाली आहे", "language": "mr", "channel": "ivrs"}
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Crucial Rule: Do NOT silently fall back to English!
        self.assertEqual(data["language"]["code"], "mr")
        self.assertEqual(data["language"]["name"], "Marathi")
        self.assertEqual(data["language"]["stt_status"], "SUPPORTED")
        self.assertEqual(data["language"]["ser_status"], "EXPERIMENTAL")
        self.assertEqual(data["language"]["text_status"], "SUPPORTED")
        self.assertIn("TESTED", data["language"]["tested_status"])
        self.assertGreaterEqual(data["svi"]["score"], 0)

if __name__ == "__main__":
    unittest.main()
