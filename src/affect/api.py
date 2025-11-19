"""VAD API and SDK."""

class VADService:
    """Streaming and batch VAD API."""

    def process_batch(self, audio_path, transcript_path):
        """Process audio file in batch mode."""
        raise NotImplementedError

    def process_stream(self, audio_stream):
        """Process audio stream in real-time."""
        raise NotImplementedError
