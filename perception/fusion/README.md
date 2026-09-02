# Perception-to-SVI Aggregation Engine

Part of **NHAA 14566 / SIH 26093 - AI Perception Layer**

---

## 1. Overview & Prototype Notice

The `fusion` module combines speech perception outputs (STT transcript, Wav2Vec2 SER emotions, acoustic features) and text distress classification signals into a single standardized **Stress Vulnerability Index (SVI 0–100)** payload for **Aatmman's Agentic Decision Layer**.

> [!WARNING]
> **PROTOTYPE RISK-SCORING DISCLAIMER**:
> - The SVI score (0–100) and risk tiers represent an **automated triage risk prioritization estimate**.
> - **IT IS NOT A CLINICALLY VALIDATED PSYCHOLOGICAL DIAGNOSIS.**
> - The scoring system is a prototype and must be validated on government helpline caller datasets prior to operational deployment.

---

## 2. Configurable Risk Tiers & Thresholds

Risk tier boundaries are configured centrally in [`config.py`](file:///d:/NHAA/config.py) (`SVIConfig`) to allow policy updates without hard-coding:

| SVI Score Range | Risk Tier | Description |
| :---: | :---: | :--- |
| **0 – 24** | **Low** | Routine query or low emotional arousal |
| **25 – 49** | **Moderate** | Mild distress or moderate speech inflections |
| **50 – 74** | **High** | Significant distress, fear, or intimidation signals |
| **75 – 100** | **Critical** | Acute distress, suicidal ideation, or severe threat |

---

## 3. Explicit SVI Scoring Formula & Component Weights

The composite SVI score is calculated from 3 weighted perception contributions:

$$\text{SVI}_{\text{Raw}} = S_{\text{text}} + S_{\text{emotion}} + S_{\text{acoustic}}$$

### A. Text Distress Contribution ($S_{\text{text}}$, Max 50 pts)
Each extracted text distress flag contributes based on category severity weight $W_{\text{flag}}$ and confidence $C_{\text{flag}}$:
- `suicidal_ideation`: $W = 45.0$
- `intimidation`: $W = 35.0$
- `trauma`: $W = 30.0$
- `fear`: $W = 25.0$
- `extreme_vulnerability`: $W = 25.0$
- `depression`: $W = 20.0$
- `isolation`: $W = 15.0$

$$S_{\text{text}} = \min\left(50.0, \sum (W_{\text{flag}} \times C_{\text{flag}})\right)$$

### B. Speech Emotion Neural Contribution ($S_{\text{emotion}}$, Max 30 pts)
Based on Wav2Vec2 SER predicted emotion label and confidence:
- `fearful` / `fear`: $W = 30.0$
- `angry`: $W = 25.0$
- `sad`: $W = 20.0$
- `surprised`: $W = 10.0$

$$S_{\text{emotion}} = \min(30.0, W_{\text{emotion}} \times C_{\text{emotion}})$$

### C. Acoustic Feature Stress Contribution ($S_{\text{acoustic}}$, Max 20 pts)
- **Extended Pauses**: Max pause duration $\ge 3.5$ s (+8 pts) or $\ge 2.0$ s (+4 pts).
- **Pitch Variability**: Pitch std $\ge 50$ Hz or pitch variation $\ge 0.25$ (+7 pts) or std $\ge 35$ Hz (+4 pts).
- **Silence Ratio**: Silence ratio $\ge 0.40$ (+5 pts).

$$S_{\text{acoustic}} = \min(20.0, \text{Pause Pts} + \text{Pitch Pts} + \text{Silence Pts})$$

---

## 4. Active Channel Scaling (Handling Missing Audio/Text)

- **Multimodal Call (Audio + Text)**:
  $$\text{SVI}_{\text{Raw}} = S_{\text{text}} + S_{\text{emotion}} + S_{\text{acoustic}}$$
- **Text-Only Call (Chat / Portal)**: `sources: {"speech": false, "text": true}`
  $$\text{SVI}_{\text{Raw}} = \min\left(100.0, S_{\text{text}} \times 2.0\right)$$
- **Audio-Only Call (IVRS / Phone)**: `sources: {"speech": true, "text": false}`
  $$\text{SVI}_{\text{Raw}} = \min\left(100.0, (S_{\text{emotion}} + S_{\text{acoustic}}) \times 2.0\right)$$

---

## 5. Output Payload Schema (`PerceptionPayload`)

```json
{
  "schema_version": "1.0",
  "case_id": "CASE-14566-DEMO",
  "timestamp": 1788248000.123,
  "svi": {
    "score": 67,
    "risk_tier": "High"
  },
  "flags": [
    {
      "name": "intimidation",
      "confidence": 0.85,
      "signals": ["Keyword match: 'मारने की धमकी' in text"],
      "source": ["text"]
    }
  ],
  "sources": {
    "speech": true,
    "text": true
  },
  "model_metadata": {
    "stt_model": "whisper-tiny",
    "ser_model": "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition",
    "text_model": "google/muril-base-cased",
    "execution_time_sec": 0.42
  },
  "safety_disclaimer": "PROTOTYPE PERCEPTION SIGNAL: The SVI score (0-100) and risk tiers represent an automated triage risk prioritization estimate..."
}
```

---

## 6. CLI & Python Usage

### CLI Execution
```powershell
python -m perception.fusion --audio samples/test.wav --text "मुझे धमकी मिल रही है" --language hi
```

### Python API Usage
```python
from perception.fusion import compute_perception_fusion

payload = compute_perception_fusion(
    stt_result=stt_out,
    ser_result=ser_out,
    speech_features_result=ac_out,
    text_distress_result=text_out,
    case_id="CASE-9921"
)

print("SVI Score :", payload["svi"]["score"])
print("Risk Tier :", payload["svi"]["risk_tier"])
```
