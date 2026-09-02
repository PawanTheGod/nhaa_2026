"""
Speech-to-Text (STT) Subpackage for AI Perception Layer
"""
from .stt_module import audio_to_transcript, SpeechToTextManager, get_stt_manager, validate_audio_file

__all__ = ["audio_to_transcript", "SpeechToTextManager", "get_stt_manager", "validate_audio_file"]
