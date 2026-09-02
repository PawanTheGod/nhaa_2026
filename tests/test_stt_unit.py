"""
Unit Tests for STT Module using Mocks
==============================================================================
Uses unittest.mock to test validation logic, error handling, language resolution,
and output schemas without incurring heavy Whisper model inference overhead.
==============================================================================
"""

import os
import unittest
from unittest.mock import MagicMock, patch
from perception.stt.stt_module import audio_to_transcript, get_stt_manager
from utils.audio_utils import generate_synthetic_audio

class TestSTTUnit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.valid_wav = "temp_unit_valid.wav"
        cls.empty_wav = "temp_unit_empty.wav"
        cls.invalid_txt = "temp_unit_invalid.txt"
        generate_synthetic_audio(cls.valid_wav, duration_sec=2.0)
        
        # Create empty wav file and dummy txt file
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
        res = audio_to_transcript("non_existent_file.wav")
        self.assertFalse(res["success"])
        self.assertIn("Audio file not found", res["error"])
        self.assertEqual(res["transcript"], "")

    def test_unsupported_format_validation(self):
        res = audio_to_transcript(self.invalid_txt)
        self.assertFalse(res["success"])
        self.assertIn("Unsupported audio format", res["error"])

    def test_empty_audio_validation(self):
        res = audio_to_transcript(self.empty_wav)
        self.assertFalse(res["success"])
        self.assertIn("Audio file is empty", res["error"])

    @patch("perception.stt.stt_module.get_stt_manager")
    def test_mocked_transcription_success_hindi(self, mock_get_manager):
        # Setup mock manager and model response
        mock_manager = MagicMock()
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "मुझे सहायता चाहिए",
            "language": "hi",
            "segments": [
                {"id": 0, "start": 0.0, "end": 2.0, "text": "मुझे सहायता चाहिए", "avg_logprob": -0.1}
            ]
        }
        mock_manager.model = mock_model
        mock_manager.device = "cpu"
        mock_get_manager.return_value = mock_manager

        res = audio_to_transcript(self.valid_wav, language="hi")
        self.assertTrue(res["success"])
        self.assertEqual(res["transcript"], "मुझे सहायता चाहिए")
        self.assertEqual(res["detected_language"], "hi")
        self.assertIn("TESTED (Hindi)", res["tested_status"])
        self.assertGreater(res["confidence_score"], 0.8)

    @patch("perception.stt.stt_module.get_stt_manager")
    def test_mocked_transcription_untested_language(self, mock_get_manager):
        mock_manager = MagicMock()
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "મદદ કરો",
            "language": "gu",
            "segments": []
        }
        mock_manager.model = mock_model
        mock_manager.device = "cpu"
        mock_get_manager.return_value = mock_manager

        res = audio_to_transcript(self.valid_wav, language="gu")
        self.assertTrue(res["success"])
        self.assertIn("UNTESTED (Gujarati)", res["tested_status"])

if __name__ == "__main__":
    unittest.main()
