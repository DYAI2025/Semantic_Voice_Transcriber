"""Turning point event detection."""

def detect_turning_points(vad_samples, config):
    """Detect emotional turning points.

    Args:
        vad_samples: List of smoothed VAD samples
        config: {grad_threshold, persistence_min, hysteresis}

    Returns:
        List of {timestamp, type, dimension, magnitude}
    """
    raise NotImplementedError
