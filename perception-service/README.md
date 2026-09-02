# 🎙️ NHAA AI Perception Layer — Multilingual Emotion & Distress Triage

**Unified sleeve note:** this service lives in `nhaa-unified/perception-service/` and must run on **port 8001**. Port 8000 is reserved for Vinit’s Central Case API.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-orange.svg)](https://pytorch.org/)
[![Tests Passing](https://img.shields.io/badge/Tests-73%2F73%20PASSED-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **SIH 26093 / Helpline AI Perception Module (Vedika's Role)**  
> An open-source, multi-modal AI perception engine designed for government helpline triage. Listens to caller voice audio and reads text to extract speech-to-text transcripts, speech emotion probabilities, named acoustic pitch/pause features, and text distress signals—fusing them into a normalized **Stress Vulnerability Index (SVI 0–100)** with grounded explainability evidence.

---

## 🌟 Key Capabilities & Features

- **🎙️ Speech-To-Text (STT) Pipeline**: Powered by OpenAI Whisper with initial prompt forced Devanagari script decoding for Indic speech (Hindi, Marathi, English, Tamil).
- **🎭 Speech Emotion Recognition (SER)**: Wav2Vec2 neural speech emotion classifier (`ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition`) with acoustic heuristic fallback.
- **📊 Named Acoustic Feature Extraction**: Grounded bio-signal measurement surfacing pitch variation ($F_0$ mean/std), pause pattern dynamics (silence ratio, max pause duration in seconds), and RMS energy dynamics.
- **🧠 Multilingual Text Distress Classifier**: Fine-tuned MuRIL (`google/muril-base-cased`) transformer + OpenRouter LLM fallback classifying 7 risk categories (`trauma`, `fear`, `depression`, `suicidal_ideation`, `intimidation`, `isolation`, `extreme_vulnerability`).
- **🎯 Stress Vulnerability Index (SVI 0–100)**: Multi-channel scoring engine aggregating weighted distress signals into 4 risk tiers (`Low`, `Moderate`, `High`, `Critical`). Features a **Severe Threat Safety Boost** forcing severe intimidation/suicide risks to High/Critical tier ($\ge 65$).
- **🔍 Grounded Explainability Engine**: Every prediction outputs human-readable evidence strings (e.g., `"Keyword match: 'जान से मार' in text"`, `"long pause: 4.2s"`, `"pitch variance: high"`).
- **🚀 Production-Ready FastAPI Backend**: Fast REST API with model lifespan preloading, CORS support, middleware request logging, interactive `/upload-test` UI, and historical SVI analytics.

---

## 🏗️ System Architecture & Data Flow

```
   [Citizen Voice / Text]
    (IVRS / App / Portal)
              │
              ▼
   ┌─────────────────────────────────────────────────────────────┐
   │                 NHAA AI Perception Layer                    │
   │                                                             │
   │  ┌──────────────────┐    ┌───────────────────────────────┐  │
   │  │   Whisper STT    │    │   Wav2Vec2 SER & Acoustic     │  │
   │  │ (Transcripts)    │    │ (Pitch, Pauses, RMS Energy)   │  │
   │  └────────┬─────────┘    └───────────────┬───────────────┘  │
   │           │                              │                  │
   │           ▼                              │                  │
   │  ┌──────────────────┐                    │                  │
   │  │  MuRIL Text NLP  │                    │                  │
   │  │ (7 Distress Flags)│                   │                  │
   │  └────────┬─────────┘                    │                  │
   │           │                              │                  │
   │           └──────────────┬───────────────┘                  │
   │                          ▼                                  │
   │             ┌─────────────────────────┐                     │
   │             │   SVI Fusion Engine     │                     │
   │             │  (0-100 Score + Tiers)  │                     │
   │             └────────────┬────────────┘                     │
   └──────────────────────────┼──────────────────────────────────┘
                              │
                              ▼ (JSON Contract)
   ┌─────────────────────────────────────────────────────────────┐
   │  Downstream Integration:                                    │
   │  • Vinit's Central Case API (RiskAssessments DB Table)     │
   │  • Aatmman's Agent Layer (Triage Decision & Action)        │
   │  • Pawan & Aditya's Officer Admin Dashboard                 │
   └─────────────────────────────────────────────────────────────┘
```

---

## 🌐 Multilingual Capability Matrix

| Language | Code | STT | Acoustic | SER | Text NLP | SVI Fusion | Status |
|---|---|---|---|---|---|---|---|
| **English** | `en` | SUPPORTED | SUPPORTED | SUPPORTED | SUPPORTED | SUPPORTED | **TESTED** |
| **Hindi** | `hi` | SUPPORTED | SUPPORTED | EXPERIMENTAL | SUPPORTED | SUPPORTED | **TESTED** |
| **Marathi** | `mr` | SUPPORTED | SUPPORTED | EXPERIMENTAL | SUPPORTED | SUPPORTED | **TESTED** |
| **Tamil** | `ta` | SUPPORTED | SUPPORTED | EXPERIMENTAL | SUPPORTED | SUPPORTED | **TESTED** |

---

## 🚀 Quickstart & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Vedika-Goyal/nhaa.git
cd nhaa
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the FastAPI Server
```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8001
```

### 5. Access Interactive Testing UI & API Docs
- **Interactive Audio Tester UI**: `http://localhost:8001/upload-test`
- **Interactive Swagger Docs**: `http://localhost:8001/docs`
- **Health Check**: `http://localhost:8001/health`

---

## 📡 API Endpoint Reference

### `POST /api/v1/perception/analyze`
Analyzes audio and/or text input to produce multimodal perception contract.

**Parameters (Form-Data):**
- `audio` *(Optional UploadFile)*: Audio file (`.wav`, `.mp3`, `.m4a`, `.flac`).
- `text` *(Optional String)*: Citizen text/transcript.
- `language` *(String, Default `"hi"`)*: ISO language code (`"en"`, `"hi"`, `"mr"`, `"ta"`).
- `case_id` *(Optional String)*: Case ID for mapping.
- `channel` *(String, Default `"ivrs"`)*: Ingestion channel (`"ivrs"`, `"phone"`, `"chat"`, `"portal"`, `"mobile_app"`).

**Sample JSON Response:**
```json
{
  "schema_version": "1.0",
  "case_id": "CASE-101",
  "timestamp": 1788293158.637,
  "channel": "ivrs",
  "language": {
    "code": "hi",
    "name": "Hindi",
    "confidence": 0.95
  },
  "svi": {
    "score": 79,
    "risk_tier": "Critical"
  },
  "stt_transcript": "मुझे जीना नहीं है, जान से मारने की धमकी दे रहे हैं",
  "flags": [
    {
      "name": "suicidal_ideation",
      "confidence": 0.85,
      "signals": ["Keyword match: 'जीना नहीं' in text"]
    },
    {
      "name": "intimidation",
      "confidence": 0.75,
      "signals": ["Keyword match: 'मारने की धमकी' in text"]
    }
  ],
  "raw_measurements": [
    {
      "source": "audio",
      "type": "acoustic_feature",
      "name": "max_pause_duration",
      "value": 3.8,
      "unit": "seconds"
    }
  ]
}
```

### Analytics Endpoints (Officer Dashboard Feed)
- `GET /api/v1/perception/analytics/svi-trend`: Weekly SVI average trends per district.
- `GET /api/v1/perception/analytics/risk-distribution`: Risk tier percentage breakdown.
- `GET /api/v1/perception/analytics/flag-frequency`: Distress flag occurrence counts.
- `GET /api/v1/perception/analytics/channel-language-volume`: Ingestion volume matrix.

---

## 🧪 Automated Testing

Execute the complete 73-test suite covering STT, SER, text NLP, SVI fusion, schema contracts, and API routes:

```bash
python -m unittest discover tests
```

**Output:**
```text
Ran 73 tests in 44.966s
OK
```

---

## 🤝 Integration Contracts

### Converting Output to Vinit's Database API (`RiskAssessmentCreate`)
```python
from perception.schemas import PerceptionOutputContract

# Convert perception result to Vinit's exact API schema payload
vinit_payload = perception_contract.to_vinit_payload(case_id_override=101)
# Returns:
# {
#   "case_id": 101,
#   "svi_score": 79.0,
#   "risk_tier": "critical",
#   "flags": {"suicidal_ideation": 0.85, "intimidation": 0.75},
#   "explanation_text": "SVI 79 (Critical). Signals: Keyword match: 'जीना नहीं'; long pause: 3.8s",
#   "model_version": "1.0"
# }
```

---

## ⚠️ Safety & Ethical Notice

> **PERCEPTION SIGNAL ONLY**: This AI module provides triage assistance and distress signal prioritization for human officers. It **DOES NOT** make clinical medical diagnoses nor initiate autonomous emergency dispatches. All high-risk alerts must be reviewed by qualified personnel.

---

## 📁 Repository Structure

```
d:\NHAA\
├── api/                        # FastAPI service & REST endpoints
│   ├── main.py                 # Lifespan app runner & UI server
│   ├── routes/                 # /analyze & /analytics routes
│   └── services/               # PerceptionService orchestrator
├── perception/                 # Core AI perception modules
│   ├── stt/                    # Whisper STT pipeline
│   ├── ser/                    # Wav2Vec2 SER model
│   ├── speech_features/        # Grounded pitch/pause/energy extractors
│   ├── text_distress/          # MuRIL NLP & OpenRouter fallback
│   ├── fusion/                 # SVI 0-100 scoring engine
│   ├── explainability/         # Grounded signal evidence builder
│   ├── evaluation/             # RAVDESS benchmark evaluation suite
│   └── schemas/                # Pydantic contract & Vinit adapter
├── tests/                      # 16 test files (73 automated tests)
├── config.py                   # SVI weights, threshold dataclasses
└── requirements.txt            # Python dependencies
```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
