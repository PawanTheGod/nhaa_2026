# Speech Emotion Recognition (SER) Benchmark Evaluation Report

Part of **NHAA 14566 / SIH 26093 - AI Perception Layer**

---

## 1. Overview & Methodology

This evaluation pipeline measures zero-shot classification performance of pretrained Speech Emotion Recognition (SER) checkpoints against open benchmark datasets (**RAVDESS** / **CREMA-D**).

> [!CAUTION]
> **CRITICAL DISCLAIMER ON REAL-WORLD ACCURACY & CLINICAL VALIDITY**:
> - **Benchmark accuracy MUST NOT be called "real-world accuracy."**
> - Performance metrics on clean, actor-recorded benchmark datasets (e.g. RAVDESS) **DO NOT** establish clinical validity or deployment performance in live government emergency helpline calls.
> - Real-world calls feature severe domain shifts: telephonic audio compression (8kHz/16kHz), background ambient noise, regional Indic accents, screaming, crying, and spontaneous unscripted distress.

---

## 2. Evaluation Protocol & Data Leakage Prevention

- **Evaluation Mode**: Zero-shot inference evaluating pretrained weights (`ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition` / `superb/wav2vec2-base-superb-er`).
- **Data Leakage Control**: Model weights were pretrained independently; no benchmark samples were used for fine-tuning during evaluation runs.
- **Audio Preprocessing**:
  - Audio resampled to 16,000 Hz mono PCM.
  - Peak amplitude normalization applied.
  - Signal fed directly into model feature extractor without label leak or post-hoc threshold tweaking.

---

## 3. Ground-Truth Label Mapping & Alignment

To prevent silent merging of incompatible classes, benchmark dataset emotion codes are explicitly mapped to canonical model labels:

| Dataset Label | Canonical Model Label | Status |
| :---: | :---: | :---: |
| `01` / `NEU` | `neutral` | Mapped 1:1 |
| `02` | `calm` | Mapped 1:1 |
| `03` / `HAP` | `happy` | Mapped 1:1 |
| `04` / `SAD` | `sad` | Mapped 1:1 |
| `05` / `ANG` | `angry` | Mapped 1:1 |
| `06` / `FEA` | `fearful` | Mapped 1:1 (`fear` $\rightarrow$ `fearful`) |
| `07` / `DIS` | `disgust` | Mapped 1:1 |
| `08` | `surprised` | Mapped 1:1 (`surprise` $\rightarrow$ `surprised`) |

---

## 4. Evaluation Metrics Computed

- **Overall Accuracy**: Total correct predictions over total evaluation samples.
- **Macro Precision, Recall, F1**: Unweighted arithmetic mean across all evaluated classes.
- **Weighted F1**: Class-support weighted F1-score.
- **Per-Class Metrics**: Precision, Recall, F1-score, and sample support per emotion class.
- **Confusion Matrix**: Full ground-truth vs prediction matrix visualization.

---

## 5. Artifacts Generated

Running the evaluation script exports artifacts to `perception/evaluation/results/`:
- `confusion_matrix.png`: High-resolution Seaborn heatmap plot.
- `evaluation_metrics.json`: Complete JSON metrics payload including execution timestamps.
- `per_class_metrics.csv`: Tabular CSV containing class-wise precision, recall, and F1 scores.

---

## 6. How to Reproduce

Execute the evaluation command:
```powershell
python -m perception.evaluation.evaluate_ser
```

To evaluate a specific dataset directory:
```powershell
python -m perception.evaluation.evaluate_ser --dataset_dir path/to/ravdess --dataset_name RAVDESS --model ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition
```
