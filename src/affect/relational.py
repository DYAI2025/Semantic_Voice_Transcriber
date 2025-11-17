"""Relational synchronicity indicators."""

def compute_synchronicity(vad_samples_speaker_a, vad_samples_speaker_b, window_sec=30):
    """Cross-correlation of arousal curves.

    Args:
        vad_samples_speaker_a: VAD samples for speaker A
        vad_samples_speaker_b: VAD samples for speaker B
        window_sec: Sliding window size in seconds

    Returns:
        float: Synchronicity score [-1, +1]
    """
    raise NotImplementedError
