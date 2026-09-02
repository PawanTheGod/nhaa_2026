# Multilingual Speech-to-Text (STT) Module

Part of **NHAA 14566 / SIH 26093 - AI Perception Layer**

---

## 1. Overview
The STT module transcribes caller audio recordings into structured text transcripts using local open-source multilingual Whisper models. It supports English, Hindi, Tamil, and other Indian languages without sending audio to third-party API services.

---

## 2. Installation & Requirements

Ensure dependencies are installed:
```powershell
pip install -r requirements.txt
```

Core dependencies:
- `openai-whisper`
- `torch` & `torchaudio`
- `librosa` / `soundfile` / `scipy`
- `numpy`

---

## 3. Model Selection & Cache Storage

### Available Models
| Model | Params | Required VRAM | Speed | Multilingual Accuracy |
| :--- | :---: | :---: | :---: | :---: |
| `tiny` | 39M | ~1 GB | Fast | Basic / Demo |
| `base` | 74M | ~1 GB | Fast | Good (Default for helpline triage) |
| `small` | 244M | ~2 GB | Medium | High |
| `medium` | 769M | ~5 GB | Slow | Very High |
| `large` | 1550M | ~10 GB | Very Slow | Maximum Accuracy |

### Model Weights Download & Storage
- Model weights are downloaded automatically on first load from Hugging Face / OpenAI official repositories.
- Weights are cached locally in the user cache directory: `~/.cache/whisper/`.
- **Git Compliance**: Model binary weights (`.pt`, `.bin`) are explicitly excluded in `.gitignore` and **must never be committed to Git**.

---

## 4. CPU / GPU Acceleration Behavior

- **Automatic CUDA Detection**: The module automatically detects if an NVIDIA GPU with CUDA is present (e.g. NVIDIA RTX 2050) and uses `cuda` with `float16` precision for fast inference.
- **Graceful CPU Fallback**: If CUDA initialization fails or GPU memory is full, the module falls back to `cpu` with `float32` precision automatically without crashing.

---

## 5. Supported Languages & Testing Status

| Language Code | Language | Validation Status |
| :---: | :---: | :---: |
| `en` | English | **TESTED** |
| `hi` | Hindi | **TESTED** |
| `ta` | Tamil | **TESTED** |
| `mr` | Marathi | UNTESTED (Supported by base model) |
| `bn` | Bengali | UNTESTED (Supported by base model) |
| `te` | Telugu | UNTESTED (Supported by base model) |

---

## 6. Supported File Formats & Validations

Supported Formats: `.wav`, `.mp3`, `.m4a`, `.flac`, `.ogg`, `.aac`, `.wma`

Automated Validations:
1. **Missing Files**: Returns `success: False` with `FileNotFoundError` message.
2. **Unsupported Formats**: Validates extension before processing.
3. **Empty Audio Files**: Rejects 0-byte audio files.
4. **Excessively Long Audio**: Rejects files exceeding the maximum threshold (default 1800s / 30 mins).
5. **Model Load Failure**: Returns structured error JSON payload without crashing backend services.

---

## 7. CLI & Python Usage

### CLI Execution
```powershell
python -m perception.stt --audio samples/test.wav --language hi --model base
```

### Python API Usage
```python
from perception.stt import audio_to_transcript

result = audio_to_transcript(
    audio_file="samples/test_call.wav",
    language="hi",
    model_name="base"
)

print("Transcript:", result["transcript"])
print("Language Status:", result["tested_status"])
print("Processing Time:", result["processing_time"], "s")
```

---

## 8. Safety & Ethical Notice
This module generates perception signals only. Transcripts are intended for human officer review and AI triage prioritization. **It does not provide clinical diagnoses or execute automated dispatches.**
