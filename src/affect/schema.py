"""JSON schema validation."""
import json
import jsonschema
from pathlib import Path

# Load schema
SCHEMA_PATH = Path(__file__).parent.parent.parent / "config" / "schema_affect.json"
with open(SCHEMA_PATH) as f:
    VAD_SCHEMA = json.load(f)

def validate_vad_output(vad_data):
    """Validate VAD JSON against schema.

    Args:
        vad_data: dict with samples, events, confidence, provenance

    Returns:
        bool: True if valid

    Raises:
        ValueError: If validation fails
    """
    try:
        jsonschema.validate(instance=vad_data, schema=VAD_SCHEMA)
        return True
    except jsonschema.ValidationError as e:
        raise ValueError(f"Schema validation failed: {e.message}")
    except jsonschema.SchemaError as e:
        raise ValueError(f"Invalid schema: {e.message}")
