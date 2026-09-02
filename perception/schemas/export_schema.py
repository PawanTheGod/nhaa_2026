"""
Utility Script to Export Perception Output Contract as JSON Schema
==============================================================================
Exports perception_schema_v1.json for cross-team backend validation.
==============================================================================
"""

import json
from pathlib import Path
from perception.schemas.perception_contract import PerceptionOutputContract

OUTPUT_JSON_SCHEMA_PATH = Path(__file__).parent / "perception_schema_v1.json"

def export_json_schema() -> str:
    """Exports Pydantic model to JSON Schema format."""
    schema_dict = PerceptionOutputContract.model_json_schema()
    schema_str = json.dumps(schema_dict, indent=2)
    
    with open(OUTPUT_JSON_SCHEMA_PATH, "w", encoding="utf-8") as f:
        f.write(schema_str)
        
    print(f"[Schema Export SUCCESS] Saved JSON schema to: {OUTPUT_JSON_SCHEMA_PATH}")
    return schema_str

if __name__ == "__main__":
    export_json_schema()
