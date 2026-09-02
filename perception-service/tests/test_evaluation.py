"""
Unit Test Suite for Benchmark Evaluation Pipeline
==============================================================================
Tests filename parsers, dataset loading, metric calculations, and artifact generation.
==============================================================================
"""

import os
import shutil
import unittest
from perception.evaluation.dataset_loader import BenchmarkDatasetLoader, generate_synthetic_benchmark_dataset
from perception.evaluation.evaluate_ser import evaluate_ser_on_benchmark

class TestSEREvaluation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_output_dir = "temp_test_eval_results"

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_output_dir):
            shutil.rmtree(cls.test_output_dir)

    def test_ravdess_filename_parser(self):
        loader = BenchmarkDatasetLoader(dataset_name="RAVDESS")
        label = loader.parse_ravdess_filename("03-01-05-01-01-01-01.wav")
        self.assertEqual(label, "angry")

        label_sad = loader.parse_ravdess_filename("03-01-04-02-01-01-02.wav")
        self.assertEqual(label_sad, "sad")

    def test_crema_filename_parser(self):
        loader = BenchmarkDatasetLoader(dataset_name="CREMA-D")
        label = loader.parse_crema_filename("1001_DFA_ANG_XX.wav")
        self.assertEqual(label, "angry")

        label_fear = loader.parse_crema_filename("1002_TIE_FEA_HI.wav")
        self.assertEqual(label_fear, "fearful")

    def test_evaluate_ser_on_benchmark_pipeline(self):
        results = evaluate_ser_on_benchmark(
            dataset_dir=None,
            dataset_name="RAVDESS",
            model_name="mock",
            output_dir=self.test_output_dir
        )

        self.assertIn("overall_accuracy", results)
        self.assertIn("macro_metrics", results)
        self.assertIn("per_class_metrics", results)
        self.assertIn("confusion_matrix", results)

        # Verify artifacts saved
        self.assertTrue(os.path.exists(os.path.join(self.test_output_dir, "confusion_matrix.png")))
        self.assertTrue(os.path.exists(os.path.join(self.test_output_dir, "evaluation_metrics.json")))
        self.assertTrue(os.path.exists(os.path.join(self.test_output_dir, "per_class_metrics.csv")))

        # Check disclaimer presence
        self.assertIn("DO NOT EQUATE BENCHMARK ACCURACY TO REAL-WORLD HELPLINE DEPLOYMENT ACCURACY", results["disclaimer"])

if __name__ == "__main__":
    unittest.main()
