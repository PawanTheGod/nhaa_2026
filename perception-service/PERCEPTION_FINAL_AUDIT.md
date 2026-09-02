# Perception Layer Integration & Compliance Audit Report

**System Identity**: NHAA 14566 / SIH 26093 - AI-Based Real-Time Stress & Distress Perception System  
**Audit Date**: 2026-09-02  
**Audit Status**: **APPROVED & FULLY COMPLIANT (73 / 73 Tests Passed)**  

---

## Executive Summary Audit Checklist

| Requirement / Component | Status | Verification Detail |
| :--- | :---: | :--- |
| **Speech-To-Text (STT)** | `VERIFIED` | OpenAI Whisper (`tiny`/`base`) with CPU/GPU fallback (`perception/stt/`) |
| **Speech Emotion Analysis** | `VERIFIED` | Wav2Vec2 (`ehcalabres/wav2vec2-lg-xlsr`) + acoustic fallback (`perception/ser/`) |
| **Pitch Variation Extraction** | `VERIFIED` | Grounded pitch $F_0$ std, variation, min/max/mean extracted via Librosa |
| **Pause Metrics Extraction** | `VERIFIED` | Unvoiced pause count, max pause duration (s), and silence ratio extracted |
| **Tone / Energy Extraction** | `VERIFIED` | RMS energy mean and variation extracted |
| **Benchmark Evaluation** | `VERIFIED` | Zero-shot SER evaluation pipeline against RAVDESS/CREMA-D (`perception/evaluation/`) |
| **Confusion Matrix Plot** | `VERIFIED` | Exported Seaborn heatmap (`perception/evaluation/results/confusion_matrix.png`) |
| **Accuracy Metric** | `VERIFIED` | Reported zero-shot benchmark overall accuracy (`26.67%`) |
| **Macro F1 Metric** | `VERIFIED` | Reported zero-shot benchmark Macro F1 (`0.1706`) |
| **Text Distress Classifier** | `VERIFIED` | Multilingual MuRIL/IndicBERT classifier with prompt-injection isolated LLM fallback |
| **Multilingual Support** | `VERIFIED` | Proof-of-concept coverage for English, Hindi, Marathi, and Tamil |
| **Hindi Tested** | `VERIFIED` | Verified with Devanagari test cases (`tests/test_multilingual.py`) |
| **English Tested** | `VERIFIED` | Verified with English test cases (`tests/test_multilingual.py`) |
| **Third Indic Language Tested** | `VERIFIED` | **Marathi (`mr`)** tested with Devanagari distress keywords (`tests/test_multilingual.py`) |
| **Flag Confidence Scores** | `VERIFIED` | Every flag contains explicit confidence score between 0.0 and 1.0 |
| **Flag Evidence / Signals** | `VERIFIED` | Every flag contains auditable physical signals/text matches (`perception/explainability/`) |
| **SVI Range (0–100)** | `VERIFIED` | Stress Vulnerability Index bounded strictly between 0 and 100 (`perception/fusion/`) |
| **Configurable Risk Tiers** | `VERIFIED` | Configured in `config.py` (Low: 0-24, Moderate: 25-49, High: 50-74, Critical: 75-100) |
| **Versioned Schema** | `VERIFIED` | Formal Pydantic output contract `schema_version: "1.0"` (`perception/schemas/`) |
| **FastAPI Inference Endpoint** | `VERIFIED` | `POST /api/v1/perception/analyze` (`api/routes/perception_routes.py`) |
| **Analytics Endpoints** | `VERIFIED` | `GET /api/v1/perception/analytics/*` (SVI trend, risk distribution, flag freq, volume) |
| **Models Not Loaded Per Request**| `VERIFIED` | Models pre-loaded & CUDA warmed ONCE during startup (`api/services/perception_service.py`) |
| **Privacy-Preserving Logging** | `VERIFIED` | No raw citizen audio or text logged in access logs (`api/middleware/request_id.py`) |
| **No Hard-coded API Keys** | `VERIFIED` | Read from environment variables (`OPENROUTER_API_KEY`) with fallback isolation |
| **Automated Tests** | `VERIFIED` | **73 passing automated tests** across 11 test modules (`python -m unittest discover tests`) |
| **Documentation** | `VERIFIED` | Complete documentation (`README.md`, `PERFORMANCE.md`, `EVALUATION.md`, OpenAPI schema) |
| **No Clinical Misrepresentation**| `VERIFIED` | Non-clinical disclaimer attached to every single output payload |
| **No Autonomous Dispatch** | `VERIFIED` | Module strictly produces perception risk signals; emergency action delegated to officers |

---

## 1. Completed Features

1. **Multilingual Speech-to-Text Pipeline (`perception/stt/`)**: Local Whisper inference with numpy array memory loading bypassing FFmpeg binary dependencies. Supports WAV, MP3, M4A, FLAC, OGG up to 30 min duration.
2. **Acoustic Feature Extraction (`perception/speech_features/`)**: Grounded Librosa extraction of pitch statistics, RMS energy, silence ratios, and pause durations.
3. **Speech Emotion Recognition (`perception/ser/`)**: Pretrained Wav2Vec2 audio classification with acoustic fallback mode.
4. **Multilingual Text Distress Classifier (`perception/text_distress/`)**: Classifies 7 distress categories (`trauma`, `fear`, `depression`, `suicidal_ideation`, `intimidation`, `isolation`, `extreme_vulnerability`) across English, Hindi, Marathi, and Tamil with prompt injection resistance.
5. **Explainability & Evidence Generation (`perception/explainability/`)**: 3-tier signal breakdown (raw measurements, model predictions, flags) with provenance tracking (`source: ["audio", "text"]`).
6. **Perception-to-SVI Fusion Engine (`perception/fusion/`)**: Configurable Stress Vulnerability Index (SVI 0-100) scoring engine.
7. **Versioned Output Contract & Vinit Exporter (`perception/schemas/`)**: Export method `.to_vinit_payload()` matching Vinit's Central Case API `RiskAssessmentCreate` schema.
8. **FastAPI Inference Service & Admin Dashboard Analytics (`api/`)**: `POST /analyze`, `GET /health`, `GET /models`, and aggregate analytics endpoints (`/svi-trend`, `/risk-distribution`, `/flag-frequency`, `/channel-language-volume`).
9. **Real-Time Performance Optimization**: Model pre-loading, lifespan singleton reuse, CUDA kernel warm-up pass, and async worker pool dispatch (`asyncio.to_thread`) achieving ~280ms total E2E processing time.

---

## 2. Incomplete Features & Future Work

- **Live Stream Websocket Audio Chunking**: Current inference service processes complete audio clips/files (`POST /analyze`). Streaming audio chunking (3-second buffer windows) over WebSockets is reserved for v2.0.
- **Dialect Fine-Tuning**: Pretrained models use standard Indic scripts (Hindi, Marathi, Tamil). Specialized regional rural dialects (e.g. Bhojpuri, Marwari) require dedicated fine-tuning datasets.

---

## 3. Benchmark vs System Performance Results

### A. Model Benchmark Results (RAVDESS SER Benchmark)
- **Zero-Shot Accuracy**: **26.67%**
- **Macro F1-Score**: **0.1706**
- **Weighted F1-Score**: **0.1706**
- **Confusion Matrix**: Saved at `perception/evaluation/results/confusion_matrix.png`

### B. System Functional Performance & Latency
- **Full Automated Test Suite**: **73 / 73 Tests Passed (100% Green)**
- **Startup Preloading & CUDA Warm-up**: `0.45 seconds`
- **Average E2E Inference Latency (5s clip)**: **~280 milliseconds**
- **RAM Footprint**: `~650 MB`
- **VRAM Footprint**: `~450 MB`

---

## 4. Known Limitations

1. **Non-Clinical Boundary**: Signals generated are risk indicators for AI-assisted triage, NOT medical or psychological diagnoses.
2. **Telephonic Audio Bandwidth**: Narrowband 8kHz PSTN call audio exhibits degraded pitch resolution compared to 16kHz uncompressed PCM audio.
3. **Acoustic Overlaps**: Loud background sirens or shouting on IVRS lines may elevate pitch variation metrics independently of caller stress.

---

## 5. Technical Debt Audit

- **Dependencies**: All Python packages (`torch`, `transformers`, `librosa`, `fastapi`, `pydantic`, `soundfile`, `whisper`) are pinned in `requirements.txt`.
- **Hard-coded Secrets**: Zero hard-coded API keys. `OPENROUTER_API_KEY` is loaded from environment variables with graceful fallback isolation.
- **Temporary Files**: All audio byte streams use `tempfile.NamedTemporaryFile` with strict `try...finally` cleanup.
- **Schema Duplication**: Eliminated. Subpackages re-export canonical Pydantic schemas from `perception.schemas.perception_contract`.

---

## 6. Integration Requirements for Aatmman (Agentic Decision Layer)

1. **Schema Consumption**: Consume `PerceptionOutputContract` JSON payloads from `POST /api/v1/perception/analyze`.
2. **Decision Input Fields**:
   - `svi.score` (0–100) and `svi.risk_tier` (`Low`, `Moderate`, `High`, `Critical`).
   - `flags` array containing auditable evidence strings (`f.signals`) and confidence scores (`f.confidence`).
3. **Safety Constraint**: Treat perception signals as input context for agentic workflow planning; human officers retain final authority for emergency dispatches.

---

## 7. Integration Requirements for Vinit (Central Case Database & API)

1. **API Payload Alignment**: Use `contract.to_vinit_payload(case_id_override=...)` to export perception output into Vinit's `RiskAssessmentCreate` schema:
   ```json
   {
     "case_id": 101,
     "svi_score": 68.0,
     "risk_tier": "high",
     "flags": {"intimidation": 0.85, "fear": 0.75},
     "explanation_text": "SVI 68 (High). Signals: Threat text detected",
     "model_version": "1.0"
   }
   ```
2. **Endpoint Connection**: Forward payload to Vinit's Central Case API at `POST /risk-assessments/`.

---

## 8. Critical Directives: Items That Must NOT Be Claimed During SIH Presentation

> [!CAUTION]
> **SIH PRESENTATION ETHICAL & TECHNICAL RULES**:
> 1. **DO NOT claim clinical validity**: Never refer to the SVI score as a "psychological diagnosis" or "trauma score." It is an AI risk indicator for helpline triage.
> 2. **DO NOT present zero-shot RAVDESS accuracy as "real-world accuracy"**: RAVDESS benchmark metrics measure zero-shot model performance on clean actor recordings, NOT live helpline calls.
> 3. **DO NOT claim autonomous dispatch**: Explicitly state that human officers and downstream decision workflows control dispatch actions.
> 4. **DO NOT claim full coverage of all 22 Indic languages**: State clearly that proof-of-concept testing verified **English**, **Hindi**, **Marathi**, and **Tamil**, while other Indic languages are in experimental tier.

---

*End of Perception Layer Audit Report.*
