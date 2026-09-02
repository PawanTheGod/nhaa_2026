"""
Speech Emotion Recognition (SER) Package for AI Perception Layer
==============================================================================
Classifies speech emotion probabilities using pretrained Wav2Vec2/HuBERT models
and merges explicit acoustic signals (pitch, pauses, energy).
==============================================================================
"""

from .ser_module import audio_to_emotion, SpeechEmotionRecognizer, get_ser_recognizer, DEFAULT_EMOTION_MODEL

__all__ = ["audio_to_emotion", "SpeechEmotionRecognizer", "get_ser_recognizer", "DEFAULT_EMOTION_MODEL"]
