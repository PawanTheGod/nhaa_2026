# AI Perception Output Contract Schema (v1.0)

Part of **NHAA 14566 / SIH 26093 - AI Perception Layer**

---

## 1. Overview & Purpose
This package defines the formal, versioned Pydantic and JSON Schema output contract for the AI Perception Layer.

### Shared Integration Points
- **Downstream Consumer**: **Aatmman's Agentic Decision Layer** (consumes risk flags, SVI score, and evidence signals to execute decision policies).
- **Upstream Producer/Store**: **Vinit's Central Case API & Risk-Assessment Backend** (persists perception payloads against helpline `case_id`s in MongoDB).

---

## 2. Python Import Interface
Other team modules can import the contract schema directly without duplicating fields:

```python
from perception.schemas import (
    PerceptionOutputContract,
    LanguageMetadata,
    SVIResult,
    FlagEvidence,
    RawMeasurement,
    ModelPrediction,
    SourcesMap,
    ModelMetadataMap
)
```

---

## 3. Field Specification Summary

| Field | Type | Description | Validation / Constraints |
| :--- | :--- | :--- | :--- |
| `schema_version` | `str` | Schema contract version | Default `"1.0"` |
| `case_id` | `Optional[str]` | Central Case API identifier | Optional string |
| `timestamp` | `float` | Unix timestamp of perception execution | Automatic |
| `channel` | `str` | Ingestion channel | `ivrs`, `phone`, `chat`, `portal`, `mobile_app` |
| `language` | `LanguageMetadata` | Language code & test status | Code e.g. `'hi'`, `'en'`, `'ta'` |
| `svi` | `SVIResult` | SVI score & risk tier | Score `0–100`, Tier: `Low`, `Moderate`, `High`, `Critical` |
| `flags` | `List[FlagEvidence]` | Extracted risk flag evidence | Names: `trauma`, `fear`, `depression`, `suicidal_ideation`, `intimidation`, `isolation`, `extreme_vulnerability` |
| `sources` | `SourcesMap` | Active channels processed | `speech` (`bool`), `text` (`bool`) |
| `raw_measurements` | `List[RawMeasurement]` | Grounded physical measurements | Sources: `audio`, `text` |
| `model_predictions` | `List[ModelPrediction]` | Neural model likelihoods | Sources: `audio`, `text` |
| `model_metadata` | `ModelMetadataMap` | Model names & execution time | STT, SER, Text models |
| `safety_disclaimer` | `str` | Mandatory non-clinical warning | Fixed string |

---

## 4. Contract Files

- [`perception_contract.py`](file:///d:/NHAA/perception/schemas/perception_contract.py): Pydantic v2 contract classes.
- [`example_perception_output.json`](file:///d:/NHAA/perception/schemas/example_perception_output.json): Canonical example JSON matching schema.
- [`perception_schema_v1.json`](file:///d:/NHAA/perception/schemas/perception_schema_v1.json): Auto-generated JSON Schema export.
- [`export_schema.py`](file:///d:/NHAA/perception/schemas/export_schema.py): Exporter utility script (`python -m perception.schemas.export_schema`).
