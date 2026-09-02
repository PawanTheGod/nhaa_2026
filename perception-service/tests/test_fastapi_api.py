"""
Automated API Test Suite for AI Perception Layer FastAPI Service
==============================================================================
Tests /health, /api/v1/perception/models, /api/v1/perception/analyze,
file upload validations, HTTP error codes, and X-Request-ID headers.
==============================================================================
"""

import unittest
import io
import wave
import numpy as np
from fastapi.testclient import TestClient

from api.main import app

def generate_synthetic_wav_bytes(duration_sec: float = 1.0, sample_rate: int = 16000) -> bytes:
    """Generates synthetic WAV audio in memory for test file upload."""
    num_samples = int(duration_sec * sample_rate)
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)
    sine_wave = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(sine_wave.tobytes())
    return buffer.getvalue()


class TestFastAPIEndpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("gpu_available", data)
        self.assertIn("models_loaded", data)

    def test_models_status_endpoint(self):
        response = self.client.get("/api/v1/perception/models")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "online")
        self.assertIn("models", data)
        self.assertIn("stt", data["models"])

    def test_analyze_text_only(self):
        form_data = {
            "text": "मुझे जान से मारने की धमकी मिल रही है और डर लग रहा है",
            "language": "hi",
            "case_id": "CASE-TEST-881",
            "channel": "chat"
        }
        response = self.client.post("/api/v1/perception/analyze", data=form_data)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["schema_version"], "1.0")
        self.assertEqual(data["case_id"], "CASE-TEST-881")
        self.assertEqual(data["channel"], "chat")
        self.assertTrue(data["sources"]["text"])
        self.assertFalse(data["sources"]["speech"])
        self.assertGreater(data["svi"]["score"], 0)

        flag_names = [f["name"] for f in data["flags"]]
        self.assertIn("intimidation", flag_names)
        self.assertIn("fear", flag_names)

    def test_analyze_audio_and_text(self):
        wav_bytes = generate_synthetic_wav_bytes(duration_sec=1.5)
        files = {
            "audio": ("test_sample.wav", wav_bytes, "audio/wav")
        }
        form_data = {
            "text": "I feel terrified and in danger",
            "language": "en",
            "case_id": "CASE-AUDIO-TEST",
            "channel": "ivrs"
        }

        response = self.client.post("/api/v1/perception/analyze", data=form_data, files=files)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["schema_version"], "1.0")
        self.assertTrue(data["sources"]["speech"])
        self.assertTrue(data["sources"]["text"])
        self.assertIn("X-Request-ID", response.headers)
        self.assertIn("X-Process-Time", response.headers)

    def test_missing_both_inputs_returns_400(self):
        response = self.client.post("/api/v1/perception/analyze", data={"language": "hi"})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("Must provide at least one", data["detail"])

    def test_unsupported_file_extension_returns_415(self):
        files = {
            "audio": ("invalid_file.txt", b"some raw text string", "text/plain")
        }
        response = self.client.post("/api/v1/perception/analyze", files=files)
        self.assertEqual(response.status_code, 415)
        data = response.json()
        self.assertIn("Unsupported audio format", data["detail"])

if __name__ == "__main__":
    unittest.main()
