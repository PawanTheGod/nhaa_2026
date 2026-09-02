"""
SER Benchmark Evaluation Package for AI Perception Layer
==============================================================================
Evaluates Speech Emotion Recognition models against RAVDESS and CREMA-D open benchmarks.
==============================================================================
"""

from .evaluate_ser import evaluate_ser_on_benchmark

__all__ = ["evaluate_ser_on_benchmark"]
