# Multilingual Text Distress-Classification Module

Part of **NHAA 14566 / SIH 26093 - AI Perception Layer**

---

## 1. Overview
The `text_distress` module extracts distress risk indicators from citizen text submissions and transcripts in **English (`en`)**, **Hindi (`hi`)**, and **Tamil (`ta`)**.

> [!IMPORTANT]
> **SAFETY & ETHICAL MANDATE**:
> - Extracted flags represent **textual risk indicators**, NOT clinical medical diagnoses.
> - Signals provide evidence for helpline triage prioritization under human officer oversight.

---

## 2. Target Risk Flags

| Risk Flag | Description | Key Indicators / Evidence |
| :--- | :--- | :--- |
| `trauma` | Trauma / flashback language | Flashbacks, nightmares, horrific events, abuse |
| `fear` | Acute terror, panic, threat | Scared, terrified, danger, घबराहट, பயம் |
| `depression` | Hopelessness, severe sadness | Hopeless, worthless, हताश, निराशा, நம்பிக்கையின்மை |
| `suicidal_ideation` | Suicidal intent | Self-harm, suicide, आत्महत्या, जान दे दूंगा |
| `intimidation` | Coercion, threats, blackmail | Threat, blackmail, धमकी, जान से मारने की धमकी, மிரட்டல் |
| `isolation` | Social isolation | Alone, abandoned, अकेलापन, ஆதரவற்ற |
| `extreme_vulnerability` | Total helplessness | No food, shelterless, लाचार, बेघर, அனாதை |

---

## 3. Dual-Path Architecture

```
[ Input Citizen Text ]
          │
          ▼
 [ Input Sanitization ] (Removes XML break-outs & prompt injection commands)
          │
          ▼
 ┌─────────────────────────────────────────────────────────┐
 │ Choice of Classifier Path                               │
 │  ├── Path A: Primary Local Model (MuRIL / IndicBERT)     │
 │  └── Path B: Fallback OpenRouter LLM (Llama 3.3 / Mistral)│
 └─────────────────────────────────────────────────────────┘
          │
          ▼
 [ Pydantic Validation ] (Validates DistressFlag & TextDistressResponse schemas)
          │
          ▼
 [ Structured JSON Output ]
```

---

## 4. Prompt-Injection Resistance

Citizen text must be treated as **untrusted input**. The module implements defense mechanisms against prompt injection:
1. **Input Sanitization**: Removes XML break-out attempts (`</untrusted_user_text>`) and neutralizes injection commands (`ignore previous instructions`, `system prompt:`).
2. **Strict Tag Isolation**: Wraps untrusted text inside `<untrusted_user_text>...</untrusted_user_text>` tags.
3. **Instruction Safeguards**: Instructs LLM models to treat user text strictly as passive data without executing embedded commands.

---

## 5. OpenRouter Fallback Client Configuration

To use the OpenRouter LLM fallback path:
```powershell
# Set API key in environment variables (DO NOT hard-code API keys)
$env:OPENROUTER_API_KEY = "sk-or-v1-..."
```

If `OPENROUTER_API_KEY` is not set or network is offline, the client falls back to the local multilingual classifier without crashing.

---

## 6. CLI & Python Usage

### CLI Execution
```powershell
python -m perception.text_distress --text "मुझे जान से मारने की धमकी मिल रही है" --language hi
```

### Python API Usage
```python
from perception.text_distress import text_to_distress_flags

result = text_to_distress_flags(
    text="I am terrified and being threatened by my landlord",
    language="en"
)

print("Language Status :", result["tested_status"])
for flag in result["flags"]:
    print(f"Flag: {flag['name']} (Conf: {flag['confidence']}) -> {flag['signals']}")
```
