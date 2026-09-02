# NHAA 14566 / SIH 26093 - AI Perception Layer Architecture

## 1. System Identity & Overview
The **AI Perception Layer** is the sensory processing component of the **NHAA 14566 / SIH 26093 Real-Time Helpline Triage System**. It ingests caller audio and text streams from government helpline channels (IVRS, mobile app, portal) and generates structured, explainable perception signals.

> [!IMPORTANT]
> **SAFETY & ETHICAL MANDATE**:
> - This module generates **risk indicators and perception signals ONLY**.
> - It **DOES NOT** make clinical or medical diagnoses.
> - It **DOES NOT** execute autonomous emergency dispatch or critical actions.
> - All outputs are forwarded to downstream decision layers and human helpline officers.

---

## 2. Architecture & Data Flow Boundaries

```
[ Helpline Callers: IVRS / Mobile App / Portal ]
                       │
                       ▼
         [ Vinit's Central Case API ]  <-- Ingests calls, creates case records & streams media
                       │
                       ▼ (HTTP / gRPC / Queue)
          ┌──────────────────────────┐
          │   AI PERCEPTION LAYER    │  <-- OUR MODULE (d:\NHAA)
          │  - Multilingual STT      │
          │  - Speech Acoustic & SER │
          │  - Text Distress Model   │
          │  - Multimodal Fusion     │
          └──────────────────────────┘
                       │
                       ▼ (Structured JSON Perception Signal)
       [ Aatmman's Agentic Decision Layer ] <-- Applies triage policies & alerts human officers
                       │
                       ▼
          [ Admin Dashboard / Officers ]
```

### Interface Dependencies

1. **Upstream Dependency: Vinit's Central Case API**
   - **Role**: Primary data provider and case state manager.
   - **Inputs to Perception Layer**:
     - `case_id`: Unique identifier for caller session.
     - `audio_file_path` / `audio_stream_bytes`: Audio sample (16kHz PCM WAV/FLAC/MP3).
     - `text_payload` (optional): Raw text if caller submitted via chat/portal.
     - `language_hint`: Optional language code (`hi`, `en`, `ta`, etc.).
     - `consent_token`: Caller privacy & data retention consent flags.

2. **Downstream Dependency: Aatmman's Agentic Decision Layer**
   - **Role**: Policy evaluation, decision orchestration, and human officer alerting.
   - **Outputs from Perception Layer**:
     - `svi_score`: Stress Vulnerability Index (0.0 to 100.0).
     - `risk_flags`: Array of flagged categories (`trauma`, `fear`, `depression`, `suicidal ideation`, `intimidation`, `isolation`) each with a confidence score (0.0–1.0).
     - `evidence_signals`: List of raw explainable evidence strings (e.g. `"long pause: 4.2s"`, `"pitch variance: high (std=48.2Hz)"`, `"keyword match: threat language"`).
     - `transcript_data`: Timed transcript segments and detected language status (`TESTED` vs `UNTESTED`).
     - `safety_disclaimer`: Mandatory non-clinical disclaimer.

---

## 3. Directory & Module Structure

```
d:\NHAA\
├── PERCEPTION_ARCHITECTURE.md   # Architecture, data flow & safety specifications
├── requirements.txt            # Python dependencies (PyTorch, Whisper, Transformers, FastAPI)
├── config.py                   # Master configuration & language validation registries
├── stt/                        # Module 1: Multilingual Speech-to-Text Pipeline
│   ├── __init__.py
│   └── stt_pipeline.py
├── ser/                        # Module 2 & 3: Speech Emotion Recognition & Acoustic Analysis (Planned)
│   ├── __init__.py
│   ├── ser_model.py
│   └── evaluate_ser.py
├── text_distress/              # Module 4: Text Distress Classification (MuRIL / OpenRouter) (Planned)
│   ├── __init__.py
│   └── text_distress_classifier.py
├── fusion/                     # Module 5: Multimodal Signal Fusion & SVI Computation (Planned)
│   ├── __init__.py
│   └── triage_fusion.py
├── api/                        # FastAPI Serving Layer & MongoDB Storage Adapters (Planned)
│   ├── __init__.py
│   └── main.py
├── utils/                      # Audio signal processing & test helpers
│   ├── __init__.py
│   └── audio_utils.py
├── tests/                      # Automated Unit & Integration Test Suites
│   ├── __init__.py
│   └── test_stt.py
└── run_stt_demo.py             # CLI Demonstration runner for STT pipeline
```

---

## 4. Hardware & Environment Specifications

- **Python Version**: 3.11.0
- **PyTorch / CUDA**: PyTorch 2.5.1 with CUDA 11.8 / 13.0 compute runtime.
- **GPU Acceleration**: NVIDIA GeForce RTX 2050 (4GB VRAM) available for local accelerated inference.
- **Primary Tested Languages**:
  - English (`en`)
  - Hindi (`hi`)
  - Tamil (`ta`)
- **Untested Indic Languages**: Marathi (`mr`), Bengali (`bn`), Telugu (`te`), etc. (Supported by underlying Whisper & MuRIL models, but explicitly tagged as `UNTESTED` in evaluation logs until validated).

---

## 5. Implementation Status Roadmap

| Component | Status | Details |
| :--- | :---: | :--- |
| **Environment & Architecture Setup** | **COMPLETED** | Verified PyTorch, CUDA, dependencies, directory structure, and `PERCEPTION_ARCHITECTURE.md`. |
| **Step 1: Multilingual STT Pipeline** | **COMPLETED** | Implemented `stt/stt_pipeline.py` with Whisper, language validation flags (`TESTED`/`UNTESTED`), and array audio loading. Unit tests passing. |
| **Step 2: SER & Acoustic Analysis** | **PLANNED** | Feature extraction for pitch variation ($F_0$), pause patterns, tone/energy (RMS), and Wav2Vec2/openSMILE emotion probabilities. |
| **Step 3: SER Benchmark Evaluation** | **PLANNED** | Confusion matrix, Accuracy, and F1 score evaluation script against RAVDESS / CREMA-D benchmarks. |
| **Step 4: Text Distress Classification** | **PLANNED** | MuRIL / IndicBERT fine-tuned model path with OpenRouter LLM zero-shot/few-shot fallback. |
| **Step 5: Multimodal Fusion & SVI API** | **PLANNED** | Composite SVI calculation (0-100), named risk flag evidence formatting, and FastAPI serving endpoints with MongoDB persistence. |
