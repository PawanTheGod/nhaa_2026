"""
Unit Test Suite for Formal Perception Output Contract Schema
==============================================================================
Verifies contract validation, canonical example JSON parsing,
channel and tier constraints, and JSON schema generation.
==============================================================================
"""

import unittest
import json
from pathlib import Path

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
from perception.schemas.export_schema import export_json_schema

EXAMPLE_JSON_PATH = Path(__file__).parent.parent / "perception" / "schemas" / "example_perception_output.json"

class TestContractSchema(unittest.TestCase):

    def test_valid_example_json_validation(self):
        self.assertTrue(EXAMPLE_JSON_PATH.exists())
        with open(EXAMPLE_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        contract_obj = PerceptionOutputContract.model_validate(data)
        self.assertEqual(contract_obj.schema_version, "1.0")
        self.assertEqual(contract_obj.case_id, "CASE-14566-20260902-8821")
        self.assertEqual(contract_obj.svi.score, 68)
        self.assertEqual(contract_obj.svi.risk_tier, "High")

    def test_channel_validation(self):
        valid_payload = {
            "schema_version": "1.0",
            "timestamp": 1234567890.0,
            "channel": "chat",
            "language": {"code": "en", "tested_status": "TESTED (English)"},
            "svi": {"score": 10, "risk_tier": "Low"},
            "flags": [],
            "sources": {"speech": False, "text": True},
            "model_metadata": {"execution_time_sec": 0.01},
            "safety_disclaimer": "Test disclaimer"
        }

        # Valid channel 'chat'
        obj = PerceptionOutputContract.model_validate(valid_payload)
        self.assertEqual(obj.channel, "chat")

        # Invalid channel 'radio'
        invalid_payload = dict(valid_payload)
        invalid_payload["channel"] = "radio"
        with self.assertRaises(ValueError):
            PerceptionOutputContract.model_validate(invalid_payload)

    def test_risk_tier_validation(self):
        with self.assertRaises(ValueError):
            SVIResult(score=50, risk_tier="Severe")

    def test_flag_name_validation(self):
        # Valid flag name
        flag = FlagEvidence(name="intimidation", confidence=0.8, signals=["threat match"], source=["text"])
        self.assertEqual(flag.name, "intimidation")

        # Invalid flag name
        with self.assertRaises(ValueError):
            FlagEvidence(name="unknown_flag_category", confidence=0.8, signals=["test"], source=["text"])

    def test_export_json_schema_utility(self):
        schema_str = export_json_schema()
        self.assertIn("PerceptionOutputContract", schema_str)
        self.assertIn("schema_version", schema_str)

    def test_to_vinit_payload_conversion(self):
        with open(EXAMPLE_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        contract_obj = PerceptionOutputContract.model_validate(data)
        vinit_payload = contract_obj.to_vinit_payload(case_id_override=101)

        self.assertEqual(vinit_payload["case_id"], 101)
        self.assertEqual(vinit_payload["svi_score"], 68.0)
        self.assertEqual(vinit_payload["risk_tier"], "high")
        self.assertIn("intimidation", vinit_payload["flags"])
        self.assertIn("fear", vinit_payload["flags"])
        self.assertEqual(vinit_payload["model_version"], "1.0")

if __name__ == "__main__":
    unittest.main()
