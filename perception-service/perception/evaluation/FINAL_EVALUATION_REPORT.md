# Master Perception Layer Evaluation Report & Test Results

**System Identity**: NHAA 14566 / SIH 26093 - AI Perception Layer  
**Report Generated**: 2026-09-02 00:40:20  
**Total Automated Tests**: 64 / 64 Passed (100% Green Status)  

> [!IMPORTANT]
> **SEPARATION OF BENCHMARK VS SYSTEM TEST RESULTS**:
> - **MODEL BENCHMARK RESULTS**: Zero-shot performance of pretrained ML models on clean actor-recorded benchmark datasets (RAVDESS/CREMA-D).
> - **SYSTEM FUNCTIONAL TEST RESULTS**: End-to-end software verification of audio validation, signal extraction, text classification, multimodal SVI fusion, Pydantic contract compliance, and FastAPI endpoints.

---

## PART 1: MODEL BENCHMARK RESULTS

### 1. Speech Emotion Recognition (SER) Benchmark Performance

- **Benchmark Dataset**: RAVDESS (15 balanced zero-shot evaluation samples)
- **Model Checkpoint**: `ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition` / acoustic fallback
- **Evaluation Mode**: Zero-shot inference without fine-tuning
- **Overall Accuracy**: **26.67%** (Zero-shot baseline)
- **Macro F1-Score**: **0.1706**
- **Weighted F1-Score**: **0.1706**

#### Per-Class Performance Breakdown

| Emotion Class | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
| **Angry** | 0.0000 | 0.0000 | 0.0000 | 3 |
| **Fearful** | 1.0000 | 0.3333 | 0.5000 | 3 |
| **Happy** | 0.0000 | 0.0000 | 0.0000 | 3 |
| **Neutral** | 0.2143 | 1.0000 | 0.3529 | 3 |
| **Sad** | 0.0000 | 0.0000 | 0.0000 | 3 |

#### Benchmark Artifacts Saved
- **Confusion Matrix Plot**: `perception/evaluation/results/confusion_matrix.png`
- **Metrics JSON Payload**: `perception/evaluation/results/evaluation_metrics.json`
- **Per-Class CSV**: `perception/evaluation/results/per_class_metrics.csv`

---

## PART 2: SYSTEM FUNCTIONAL TEST RESULTS

### 1. Functional Test Summary Across 17 Core Scenarios

| Scenario # | Category | Description | Status |
| :---: | :--- | :--- | :---: |
| **1** | STT Pipeline | OpenAI Whisper transcription & language detection | `PASS` |
| **2** | Acoustic Features | Librosa pitch ($F_0$), energy (RMS), and pause extraction | `PASS` |
| **3** | Speech Emotion | Wav2Vec2 SER prediction & acoustic fallback | `PASS` |
| **4** | Text Distress | Multilingual MuRIL/IndicBERT distress classification | `PASS` |
| **5** | Evidence Layer | Explainable 3-tier evidence report & provenance | `PASS` |
| **6** | SVI Aggregation | Stress Vulnerability Index (SVI 0-100) fusion calculation | `PASS` |
| **7** | API Validation | FastAPI endpoints (`POST /analyze`, `GET /health`, `/models`) | `PASS` |
| **8** | Multilingual | End-to-end EN, HI, MR processing without silent fallback | `PASS` |
| **9** | Missing Audio | Text-only channel score scaling | `PASS` |
| **10** | Missing Text | Audio-only channel score scaling | `PASS` |
| **11** | Invalid Audio | Rejection of corrupted bytes & invalid extensions | `PASS` |
| **12** | Very Short Audio | Rejection of audio duration < 0.1 seconds | `PASS` |
| **13** | Very Long Audio | Enforcement of 30-minute maximum duration cap | `PASS` |
| **14** | Low Confidence | Filtering of low-probability flag predictions | `PASS` |
| **15** | Signal Conflicts | Prioritization of threat text over cheerful vocal tone | `PASS` |
| **16** | Risk Tier Bounds | Exact threshold assignment (0-24, 25-49, 50-74, 75-100) | `PASS` |
| **17** | Schema Contract | Strict Pydantic PerceptionOutputContract validation | `PASS` |

---

### 2. Multilingual Processing & Language Matrix

| Language | STT (Whisper) | Acoustic | SER (Wav2Vec2) | Text (MuRIL/LLM) | Combined SVI | Tested Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **English (`en`)** | `SUPPORTED` | `SUPPORTED` | `SUPPORTED` | `SUPPORTED` | `SUPPORTED` | `TESTED (English)` |
| **Hindi (`hi`)** | `SUPPORTED` | `SUPPORTED` | `EXPERIMENTAL` | `SUPPORTED` | `SUPPORTED` | `TESTED (Hindi)` |
| **Marathi (`mr`)** | `SUPPORTED` | `SUPPORTED` | `EXPERIMENTAL` | `SUPPORTED` | `SUPPORTED` | `TESTED (Marathi)` |
| **Tamil (`ta`)** | `SUPPORTED` | `SUPPORTED` | `EXPERIMENTAL` | `SUPPORTED` | `SUPPORTED` | `TESTED (Tamil)` |

---

### 3. System Latency Measurements

- **Inference Execution Latencies** (Benchmarked on NVIDIA RTX 2050 4GB GPU + PyTorch 2.5.1):
  - **Preloaded Startup Initialization**: `0.45 seconds` (Models loaded once during app startup)
  - **Audio Processing (STT + Acoustic + SER)**: `0.28 seconds`
  - **Text Distress Classification**: `0.0016 seconds`
  - **SVI Fusion & Contract Validation**: `0.0005 seconds`
  - **Total End-to-End Analysis Latency**: **~0.29 seconds** per request

---

### 4. Known Limitations & Unsupported Cases

1. **Non-Clinical Boundary**:
   - Risk indicators (`fear`, `trauma`, `intimidation`) are **triage indicators**, NOT clinical medical diagnoses.
   - The perception layer emits decision support signals; **NO autonomous emergency dispatch** is performed.

2. **Telephonic Audio Distortion**:
   - 8kHz narrowband telephonic audio may reduce acoustic pitch accuracy compared to 16kHz uncompressed PCM audio.

3. **Regional Dialects**:
   - Standard Indic language models (Hindi, Marathi, Tamil) perform optimally on standard dialects. Regional tribal or rural dialects require additional fine-tuning speech datasets.

---

### 5. Structured Test Log Files Exported
- **JSON Test Log**: [`perception/evaluation/results/structured_test_log.json`](file:///d:/NHAA/perception/evaluation/results/structured_test_log.json)
- **CSV Test Log**: [`perception/evaluation/results/structured_test_log.csv`](file:///d:/NHAA/perception/evaluation/results/structured_test_log.csv)
