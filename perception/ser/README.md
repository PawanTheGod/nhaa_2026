# Speech Emotion Recognition (SER) Component

Part of **NHAA 14566 / SIH 26093 - AI Perception Layer**

---

## 1. Overview
The Speech Emotion Recognition (SER) component classifies acoustic speech emotion probabilities using open-source Wav2Vec2/HuBERT pretrained neural network checkpoints while simultaneously extracting explicit, interpretable acoustic signals (**pitch variation**, **pause duration/patterns**, **energy dynamics**).

---

## 2. Selected Pretrained Checkpoint

- **Model Identifier**: `superb/wav2vec2-base-superb-er` (SUPERB Benchmark Speech Emotion Recognition)
- **Base Architecture**: Wav2Vec2 Base (`facebook/wav2vec2-base`) fine-tuned on emotion speech datasets.
- **License**: Apache 2.0 / MIT (fully compatible with open-source prototypes).
- **Emotion Categories**: `neutral`, `happy`, `sad`, `angry`.
- **Local Cache**: Weight files (~360MB) are downloaded automatically on first run and cached in `~/.cache/huggingface/hub/`. Model weights are **never committed to Git**.

---

## 3. Separation of Physical Signals vs Clinical Diagnoses

> [!IMPORTANT]
> **CRITICAL ETHICAL & SAFETY MANDATE**:
> - Emotion predictions estimated by neural networks represent **physical acoustic pattern classifications ONLY**.
> - They **DO NOT** constitute clinical, medical, or psychological diagnoses.
> 
> **Explicit Mappings Disallowed**:
> - $\text{fear} \neq \text{trauma}$
> - $\text{sadness} \neq \text{depression}$
> - $\text{low energy} \neq \text{suicidal ideation}$
>
> Raw emotion likelihoods and acoustic features are preserved as separate perception signals, which downstream triage policy decision engines and human officers interpret in full context.

---

## 4. Output Data Schema

```json
{
  "success": true,
  "error": null,
  "emotion": {
    "label": "fear",
    "confidence": 0.81
  },
  "top_predictions": [
    { "label": "fear", "confidence": 0.81 },
    { "label": "sad", "confidence": 0.12 },
    { "label": "neutral", "confidence": 0.05 },
    { "label": "angry", "confidence": 0.02 }
  ],
  "acoustic_signals": {
    "pitch_variation": 0.2111,
    "pitch_mean_hz": 205.08,
    "pitch_std_hz": 43.29,
    "pitch_range_hz": 154.34,
    "pause_count": 1,
    "mean_pause_duration_seconds": 0.86,
    "max_pause_duration_seconds": 0.86,
    "silence_ratio": 0.288,
    "energy_variation": 0.1694,
    "mean_rms": 0.2575,
    "speaking_rate_proxy": 0.94
  },
  "model_name": "superb/wav2vec2-base-superb-er",
  "processing_time": 0.42,
  "safety_disclaimer": "PERCEPTION SIGNAL ONLY: Emotion predictions are acoustic signals..."
}
```

---

## 5. Usage Example

### CLI
```powershell
python -m perception.ser --audio samples/test.wav
```

### Python API
```python
from perception.ser import audio_to_emotion

result = audio_to_emotion("samples/test.wav")

print("Top Emotion Label :", result["emotion"]["label"])
print("Confidence        :", result["emotion"]["confidence"])
print("Pitch Variation   :", result["acoustic_signals"]["pitch_variation"])
print("Pause Count       :", result["acoustic_signals"]["pause_count"])
```
