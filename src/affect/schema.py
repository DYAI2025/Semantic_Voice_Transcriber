"""JSON schema validation."""

def validate_vad_output(vad_data):
    """Validate VAD JSON against schema.

    Args:
        vad_data: dict with samples, events, confidence, provenance

    Returns:
        bool: True if valid

    Raises:
        ValueError: If validation fails
    """
    raise NotImplementedError
