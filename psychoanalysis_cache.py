# psychoanalysis_cache.py
import json
import hashlib
from pathlib import Path

class CacheManager:
    """Hash-based cache for psychoanalysis results to avoid redundant OpenAI API calls"""

    def __init__(self, cache_dir="cache/psychoanalysis"):
        """Initialize cache manager

        Args:
            cache_dir: Directory to store cached analyses
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def compute_transcript_hash(self, transcript_data):
        """Compute SHA256 hash of transcript content

        Args:
            transcript_data: Dictionary with transcript_meta and utterances

        Returns:
            str: SHA256 hash (64 hex chars)
        """
        # Sort keys for deterministic JSON serialization
        transcript_json = json.dumps(transcript_data, sort_keys=True, ensure_ascii=False)

        # Compute SHA256 hash
        hash_obj = hashlib.sha256(transcript_json.encode('utf-8'))
        return hash_obj.hexdigest()

    def get_cached_analysis(self, transcript_data):
        """Retrieve cached analysis if exists

        Args:
            transcript_data: Dictionary with transcript_meta and utterances

        Returns:
            dict or None: Cached analysis result, or None if no cache exists
        """
        transcript_hash = self.compute_transcript_hash(transcript_data)
        cache_file = self.cache_dir / f"{transcript_hash}.json"

        if not cache_file.exists():
            return None

        # Load and return cached analysis
        with open(cache_file, 'r', encoding='utf-8') as f:
            cached_analysis = json.load(f)

        return cached_analysis

    def save_analysis(self, transcript_data, analysis):
        """Save analysis to cache

        Args:
            transcript_data: Dictionary with transcript_meta and utterances
            analysis: Analysis result to cache
        """
        transcript_hash = self.compute_transcript_hash(transcript_data)
        cache_file = self.cache_dir / f"{transcript_hash}.json"

        # Save analysis to cache file
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
