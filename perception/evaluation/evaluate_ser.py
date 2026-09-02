"""
Speech Emotion Recognition (SER) Benchmark Evaluation Pipeline
==============================================================================
NHAA 14566 / SIH 26093 - AI Perception Layer
==============================================================================
Evaluates pretrained SER checkpoints on RAVDESS / CREMA-D benchmarks.
Calculates Accuracy, Macro F1, Weighted F1, Per-Class Metrics, and Confusion Matrix.
==============================================================================
"""

import os
import sys
import json
import time
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)

from perception.ser import audio_to_emotion, DEFAULT_EMOTION_MODEL
from perception.evaluation.dataset_loader import (
    BenchmarkDatasetLoader,
    LABEL_ALIASES,
    generate_synthetic_benchmark_dataset
)

# Disclaimer stating that benchmark accuracy is not real-world deployment accuracy
EVAL_SAFETY_DISCLAIMER = (
    "BENCHMARK EVALUATION NOTICE: Accuracy and F1 scores reported are measured on open benchmark datasets "
    "(RAVDESS / CREMA-D) under zero-shot evaluation conditions. "
    "DO NOT EQUATE BENCHMARK ACCURACY TO REAL-WORLD HELPLINE DEPLOYMENT ACCURACY OR CLINICAL VALIDITY. "
    "Noise, dialect variation, and high call stress in live government helpline calls introduce domain shifts."
)


def evaluate_ser_on_benchmark(
    dataset_dir: Optional[str] = None,
    dataset_name: str = "RAVDESS",
    model_name: str = DEFAULT_EMOTION_MODEL,
    output_dir: str = "perception/evaluation/results"
) -> Dict[str, Any]:
    """
    Evaluates the SER model against a benchmark dataset.
    
    Args:
        dataset_dir: Directory containing benchmark WAV files. If None, uses synthetic benchmark set.
        dataset_name: Name of benchmark dataset ('RAVDESS' or 'CREMA-D').
        model_name: Model checkpoint to evaluate.
        output_dir: Path to save evaluation metrics JSON, CSV, and confusion matrix PNG.
        
    Returns:
        Structured evaluation metrics dictionary.
    """
    start_time = time.time()
    os.makedirs(output_dir, exist_ok=True)

    # 1. Load Dataset Samples
    loader = BenchmarkDatasetLoader(dataset_name=dataset_name)
    if dataset_dir and os.path.exists(dataset_dir):
        print(f"[Evaluation] Loading {dataset_name} dataset from '{dataset_dir}'...")
        samples = loader.load_dataset(dataset_dir)
    else:
        print(f"[Evaluation] No custom dataset directory provided. Generating synthetic {dataset_name} benchmark samples...")
        synthetic_dir = os.path.join(output_dir, "synthetic_benchmark_audio")
        samples = generate_synthetic_benchmark_dataset(target_dir=synthetic_dir, samples_per_class=3)

    if not samples:
        raise ValueError(f"No valid audio samples found for evaluation in dataset directory.")

    print(f"[Evaluation] Successfully loaded {len(samples)} benchmark samples across classes.")

    # 2. Run Zero-Shot SER Model Inference
    y_true = []
    y_pred = []
    inference_times = []

    print(f"[Evaluation] Running zero-shot SER model inference using '{model_name}'...")
    for idx, (filepath, true_label) in enumerate(samples, 1):
        t0 = time.time()
        res = audio_to_emotion(filepath, model_name=model_name)
        inference_times.append(time.time() - t0)

        pred_label_raw = res["emotion"]["label"].lower()
        
        # Align labels using canonical aliases
        norm_true = LABEL_ALIASES.get(true_label.lower(), true_label.lower())
        norm_pred = LABEL_ALIASES.get(pred_label_raw, pred_label_raw)

        y_true.append(norm_true)
        y_pred.append(norm_pred)

    # 3. Compute Metrics
    unique_classes = sorted(list(set(y_true + y_pred)))
    
    acc = float(accuracy_score(y_true, y_pred))
    
    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )
    
    precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", zero_division=0
    )

    per_class_p, per_class_r, per_class_f1, per_class_support = precision_recall_fscore_support(
        y_true, y_pred, labels=unique_classes, zero_division=0
    )

    cm = confusion_matrix(y_true, y_pred, labels=unique_classes)

    per_class_dict = {}
    per_class_rows = []
    for idx, cls_name in enumerate(unique_classes):
        metrics_item = {
            "precision": round(float(per_class_p[idx]), 4),
            "recall": round(float(per_class_r[idx]), 4),
            "f1_score": round(float(per_class_f1[idx]), 4),
            "support": int(per_class_support[idx])
        }
        per_class_dict[cls_name] = metrics_item
        per_class_rows.append({
            "class": cls_name,
            "precision": metrics_item["precision"],
            "recall": metrics_item["recall"],
            "f1_score": metrics_item["f1_score"],
            "support": metrics_item["support"]
        })

    # 4. Save Confusion Matrix Plot
    cm_png_path = os.path.join(output_dir, "confusion_matrix.png")
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=unique_classes,
        yticklabels=unique_classes
    )
    plt.title(f"SER Confusion Matrix ({dataset_name} Benchmark)")
    plt.xlabel("Predicted Emotion Label")
    plt.ylabel("True Benchmark Ground Truth Label")
    plt.tight_layout()
    plt.savefig(cm_png_path, dpi=300)
    plt.close()

    # 5. Save Per-Class Metrics CSV
    csv_path = os.path.join(output_dir, "per_class_metrics.csv")
    df_metrics = pd.DataFrame(per_class_rows)
    df_metrics.to_csv(csv_path, index=False)

    # 6. Format Final Result Object
    total_eval_time = round(time.time() - start_time, 2)
    
    result_metrics = {
        "dataset_name": dataset_name,
        "sample_count": len(samples),
        "classes": unique_classes,
        "model_checkpoint": model_name,
        "evaluation_mode": "Zero-shot Evaluation (Pretrained Weights)",
        "preprocessing": "16kHz Mono PCM Audio Resampling & Peak Normalization",
        "overall_accuracy": round(acc, 4),
        "macro_metrics": {
            "precision": round(float(precision_macro), 4),
            "recall": round(float(recall_macro), 4),
            "f1_score": round(float(f1_macro), 4)
        },
        "weighted_metrics": {
            "precision": round(float(precision_weighted), 4),
            "recall": round(float(recall_weighted), 4),
            "f1_score": round(float(f1_weighted), 4)
        },
        "per_class_metrics": per_class_dict,
        "confusion_matrix": cm.tolist(),
        "mean_inference_time_per_sample_sec": round(float(np.mean(inference_times)), 4),
        "total_evaluation_time_sec": total_eval_time,
        "artifacts_saved": {
            "confusion_matrix_png": cm_png_path,
            "metrics_json": os.path.join(output_dir, "evaluation_metrics.json"),
            "per_class_csv": csv_path
        },
        "disclaimer": EVAL_SAFETY_DISCLAIMER
    }

    # Save Metrics JSON
    json_path = os.path.join(output_dir, "evaluation_metrics.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result_metrics, f, indent=2, ensure_ascii=False)

    # 7. Print Terminal Summary
    print("\n" + "=" * 80)
    print(f"SER BENCHMARK EVALUATION REPORT: {dataset_name}")
    print("=" * 80)
    print(f"Model Checkpoint    : {model_name}")
    print(f"Evaluation Mode     : Zero-shot Evaluation")
    print(f"Total Samples       : {len(samples)}")
    print(f"Overall Accuracy    : {acc * 100:.2f}%")
    print(f"Macro F1-Score      : {f1_macro:.4f}")
    print(f"Weighted F1-Score   : {f1_weighted:.4f}")
    print("\nPer-Class Breakdown:")
    print(df_metrics.to_string(index=False))
    print(f"\nSaved Confusion Matrix Plot : {cm_png_path}")
    print(f"Saved Metrics JSON          : {json_path}")
    print(f"Saved Per-Class CSV         : {csv_path}")
    print("=" * 80)

    return result_metrics

if __name__ == "__main__":
    import argparse
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="SER Benchmark Evaluation CLI")
    parser.add_argument("--dataset_dir", type=str, default=None, help="Directory containing benchmark WAV files")
    parser.add_argument("--dataset_name", type=str, default="RAVDESS", help="RAVDESS or CREMA-D")
    parser.add_argument("--model", type=str, default="mock", help="Pretrained model checkpoint or 'mock'")
    parser.add_argument("--output_dir", type=str, default="perception/evaluation/results", help="Artifact output dir")

    args = parser.parse_args()
    evaluate_ser_on_benchmark(
        dataset_dir=args.dataset_dir,
        dataset_name=args.dataset_name,
        model_name=args.model,
        output_dir=args.output_dir
    )
