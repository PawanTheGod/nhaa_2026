# Explainability & Evidence Generation Layer

Part of **NHAA 14566 / SIH 26093 - AI Perception Layer**

---

## 1. Overview
The `explainability` module builds grounded, auditable, and transparent evidence reports for helpline AI triage. It ensures that **every perception prediction is accompanied by explicit evidence signals describing the exact acoustic measurements, detected text keywords, or model predictions that drove it**.

---

## 2. Non-Invention & Provenance Guarantees

> [!IMPORTANT]
> **STRICT AUDITABILITY RULES**:
> 1. **Never Invent Evidence**: Every emitted signal corresponds to a physical acoustic feature, detected text pattern, or model probability score.
> 2. **Explicit Separation**:
>    - `raw_measurements`: Grounded measurements with source, type, name, value, and unit (e.g. `{"source": "audio", "type": "acoustic_feature", "name": "pause_duration", "value": 4.2, "unit": "seconds"}`).
>    - `model_predictions`: Direct neural classifier probabilities (e.g. `{"source": "audio", "type": "model_prediction", "name": "fear", "confidence": 0.81, "model_name": "..."}`).
>    - `flags`: Merged risk indicators containing concise signals and provenance lists (`"source": ["audio", "text"]`).
> 3. **Privacy Preservation**: For text evidence, keyword patterns are summarized into anonymized match descriptions without exposing raw citizen transcripts in audit logs.
> 4. **No Chain-of-Thought**: Hidden LLM reasoning or chain-of-thought is excluded; only auditable features and signals are exposed.

---

## 3. Unified Flag Evidence Schema

```json
{
  "name": "intimidation",
  "confidence": 0.85,
  "signals": [
    "long pause: 4.2 seconds",
    "pitch variation: high (std=43.3 Hz)",
    "Keyword match: 'मारने की धमकी' in text"
  ],
  "source": ["audio", "text"]
}
```

---

## 4. Helper Functions

- `speech_to_evidence(stt_res, ser_res, ac_res)`: Converts audio STT, SER, and acoustic feature outputs into speech flags, raw measurements, and model predictions (`source: ["audio"]`).
- `text_to_evidence(text_distress_res)`: Converts text distress results into text flags, raw measurements, and model predictions (`source: ["text"]`).
- `merge_evidence(speech_flags, ..., text_flags, ...)`: Fuses speech and text channels. Cross-modal flags present in both speech and text are merged into unified flags with `source: ["audio", "text"]` and boosted confidence.

---

## 5. Usage Example

```python
from perception.explainability import build_unified_evidence_report

report = build_unified_evidence_report(
    stt_result=stt_out,
    ser_result=ser_out,
    speech_features_result=ac_out,
    text_distress_result=text_out
)

for flag in report["flags"]:
    print(f"Flag: {flag['name']} (Conf: {flag['confidence']}) Provenance: {flag['source']}")
    for sig in flag["signals"]:
        print(f" - Signal: {sig}")
```
