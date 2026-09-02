# Interpretable Acoustic Speech-Feature Extraction Module

Part of **NHAA 14566 / SIH 26093 - AI Perception Layer**

---

## 1. Overview
The `speech_features` module extracts structural acoustic measurements from raw caller audio recordings. Instead of relying solely on black-box neural emotion labels, it surfaces explicit acoustic features (**pitch variability**, **pause patterns**, **energy dynamics**) required for transparent AI helpline triage.

---

## 2. Extracted Features & Mathematical Derivation

### A. Pitch ($F_0$ Fundamental Frequency)
- **Algorithm**: Probabilistic YIN (`librosa.pyin`) over human vocal range (65 Hz to 2093 Hz).
- **Features Extracted**:
  - `mean_hz`: $\mu_{F_0} = \frac{1}{N} \sum_{i=1}^N F_{0,i}$ (Baseline pitch height)
  - `median_hz`: Median pitch value (robust to pitch tracking outliers)
  - `min_hz` / `max_hz`: Fundamental frequency bounds
  - `std_hz`: $\sigma_{F_0}$ (Pitch variation / voice inflections)
  - `range_hz`: $F_{0,\max} - F_{0,\min}$ (Dynamic pitch range)
  - `pitch_variation`: $\frac{\sigma_{F_0}}{\mu_{F_0}}$ (Coefficient of pitch variation, unitless)

### B. Energy / Loudness Dynamics
- **Algorithm**: Root Mean Square (RMS) frame energy computation.
- **Features Extracted**:
  - `mean_rms`: Average frame signal amplitude
  - `std_rms`: Energy standard deviation (vocal dynamic range)
  - `max_rms`: Peak signal amplitude
  - `mean_energy`: Mean signal power ($\mathbb{E}[\text{RMS}^2]$)

### C. Speech Activity & Pause Patterns
- **Algorithm**: Energy-based non-silent interval splitting (`librosa.effects.split` with $top\_db=25$).
- **Features Extracted**:
  - `total_duration_sec`: Total length of recording
  - `voiced_duration_sec`: Total active speech duration
  - `silence_duration_sec`: Total silence duration
  - `count`: Number of pause gaps $\ge 0.20$ seconds (ignores micro-stops between consonants)
  - `mean_duration_seconds`: Average pause length
  - `max_duration_seconds`: Maximum single pause length
  - `silence_ratio`: $\frac{\text{Silence Duration}}{\text{Total Duration}}$ ($0.0$ to $1.0$)

### D. Basic Speech Characteristics
- **Zero Crossing Rate (`mean_zcr`)**: Rate of signal sign changes per frame (distinguishes unvoiced fricatives / noise from voiced vowels).
- **Speaking Rate Proxy (`speaking_rate_proxy`)**: Voiced burst count per second of active speech ($\frac{\text{Voiced Segments}}{\text{Voiced Duration}}$).

---

## 3. Why These Features Are Interpretable

1. **Pause Hesitation Patterns**: Extended silences ($\ge 3.0$ s) or elevated `silence_ratio` ($> 0.40$) can indicate cognitive load, hesitation, distress, or emotional paralysis during emergency calls.
2. **Pitch Variations**: Unusually low pitch variability ($\sigma_{F_0} < 15$ Hz) indicates monotonous/depressed tone, while high pitch spikes ($\sigma_{F_0} > 60$ Hz, $F_{max} > 350$ Hz) indicate acute distress, fear, or crying.
3. **Energy Dynamics**: High RMS variance (`std_rms`) paired with pitch spikes signals agitated speech or distress.

---

## 4. Assumptions & Limitations

- **Sampling Rate**: Audio is resampled to 16,000 Hz mono PCM.
- **Silence Threshold**: Default `top_db = 25.0` dB relative to peak frame energy.
- **Vocal Range**: pYIN pitch range bounded between $C_2$ (65 Hz) and $C_7$ (2093 Hz).
- **Acoustic Noise Limitation**: Background noise or room reverberation in helpline IVRS calls may elevate `silence_ratio` or distort $F_0$ tracking; pre-filtering or adaptive thresholding is recommended.

---

## 5. Usage Example

```python
from perception.speech_features import extract_acoustic_features

features = extract_acoustic_features("samples/test_call.wav")

print("Pitch Mean (Hz) :", features["pitch"]["mean_hz"])
print("Pitch Std (Hz)  :", features["pitch"]["std_hz"])
print("Pause Count     :", features["pauses"]["count"])
print("Max Pause (s)   :", features["pauses"]["max_duration_seconds"])
print("Silence Ratio   :", features["pauses"]["silence_ratio"])
```

---

## 6. Safety & Ethical Notice
Acoustic measurements provide structural physical properties of voice signals for helpline triage prioritization. **They do not constitute a medical diagnosis or prove clinical trauma.**
