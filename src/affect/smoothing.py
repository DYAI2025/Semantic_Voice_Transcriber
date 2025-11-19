"""EMA smoothing with latency constraint."""

def smooth_vad_ema(vad_samples, lambda_=0.3):
    """Apply exponential moving average smoothing.

    Args:
        vad_samples: List of normalized VAD samples
        lambda_: Smoothing factor (0-1, higher = more smoothing)

    Returns:
        List of smoothed VAD samples
    """
    raise NotImplementedError
