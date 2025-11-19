"""Prosody-based affect features extraction."""

def extract_arousal_features(audio_segment, sr=16000):
    """Extract arousal-related prosody features.

    Args:
        audio_segment: Audio signal array
        sr: Sample rate

    Returns:
        dict: {energy_rms, energy_db, zcr}
    """
    raise NotImplementedError
