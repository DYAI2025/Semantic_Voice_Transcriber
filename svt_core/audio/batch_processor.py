#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Processor - Efficient processing of multiple audio files

Optimizes processing of multiple files by:
- Reusing loaded models across files (avoid repeated loading)
- GPU memory management (clear cache between files)
- Progress tracking and error handling
- Parallel processing where possible

Usage:
    processor = BatchDiarizer(
        hf_token="...",
        enable_embedding_extraction=True
    )

    results = processor.process_batch(audio_files)
"""

import logging
import gc
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BatchResult:
    """Result from processing a single file in batch"""
    audio_path: Path
    success: bool
    segments: List[Dict[str, Any]]
    error: Optional[str] = None
    duration: Optional[float] = None  # Processing time in seconds


class BatchDiarizer:
    """
    Efficient batch processing of multiple audio files for speaker diarization

    Key Features:
    - Model reuse: Load diarization pipeline once, reuse for all files
    - GPU memory management: Clear cache between files
    - Progress tracking: Log progress through batch
    - Error isolation: One file failure doesn't stop the batch
    """

    def __init__(
        self,
        hf_token: str,
        min_speakers: int = 1,
        max_speakers: int = 10,
        enable_embedding_extraction: bool = False,
        enable_speaker_matching: bool = False,
        device: str = None
    ):
        """
        Initialize batch diarizer

        Args:
            hf_token: Hugging Face authentication token
            min_speakers: Minimum number of speakers
            max_speakers: Maximum number of speakers
            enable_embedding_extraction: Extract speaker embeddings
            enable_speaker_matching: Match speakers to known profiles
            device: Device to use ('cuda', 'cpu', or None for auto)
        """
        self.hf_token = hf_token
        self.min_speakers = min_speakers
        self.max_speakers = max_speakers
        self.enable_embedding_extraction = enable_embedding_extraction
        self.enable_speaker_matching = enable_speaker_matching
        self.device = device

        # Lazy-loaded diarizer (created on first use)
        self._diarizer = None

    def _get_diarizer(self):
        """Get or create diarizer instance (lazy initialization)"""
        if self._diarizer is None:
            from svt_core.audio.diarization import SpeakerDiarizer

            logger.info("Initializing diarizer for batch processing...")
            self._diarizer = SpeakerDiarizer(
                use_auth_token=self.hf_token,
                min_speakers=self.min_speakers,
                max_speakers=self.max_speakers,
                enable_embedding_extraction=self.enable_embedding_extraction,
                enable_speaker_matching=self.enable_speaker_matching,
                device=self.device
            )
            logger.info("✅ Diarizer initialized")

        return self._diarizer

    def process_batch(
        self,
        audio_files: List[Path],
        num_speakers: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int, Path], None]] = None
    ) -> List[BatchResult]:
        """
        Process multiple audio files in batch

        Args:
            audio_files: List of audio file paths
            num_speakers: Fixed number of speakers for all files (None for auto-detect)
            progress_callback: Optional callback(current, total, file_path) for progress updates

        Returns:
            List of BatchResult objects, one per input file

        Example:
            def on_progress(current, total, file):
                print(f"Processing {current}/{total}: {file.name}")

            results = processor.process_batch(files, progress_callback=on_progress)
        """
        logger.info(f"=" * 70)
        logger.info(f"BATCH DIARIZATION")
        logger.info(f"=" * 70)
        logger.info(f"Processing {len(audio_files)} files...")
        logger.info("")

        results = []

        for idx, audio_path in enumerate(audio_files, 1):
            # Progress callback
            if progress_callback:
                progress_callback(idx, len(audio_files), audio_path)

            logger.info(f"[{idx}/{len(audio_files)}] Processing: {audio_path.name}")

            # Process file
            result = self._process_single_file(audio_path, num_speakers)
            results.append(result)

            # Log result
            if result.success:
                logger.info(
                    f"  ✅ Success: {len(result.segments)} segments "
                    f"({result.duration:.1f}s)" if result.duration else ""
                )
            else:
                logger.error(f"  ❌ Failed: {result.error}")

            # Memory management between files
            self._cleanup_memory()

            logger.info("")

        # Summary
        success_count = sum(1 for r in results if r.success)
        failed_count = len(results) - success_count

        logger.info("=" * 70)
        logger.info("BATCH SUMMARY")
        logger.info("=" * 70)
        logger.info(f"✅ Successful: {success_count}/{len(results)}")
        logger.info(f"❌ Failed: {failed_count}/{len(results)}")

        if failed_count > 0:
            logger.info("")
            logger.info("Failed files:")
            for result in results:
                if not result.success:
                    logger.info(f"  - {result.audio_path.name}: {result.error}")

        return results

    def _process_single_file(
        self,
        audio_path: Path,
        num_speakers: Optional[int]
    ) -> BatchResult:
        """
        Process a single audio file

        Args:
            audio_path: Path to audio file
            num_speakers: Fixed number of speakers (None for auto-detect)

        Returns:
            BatchResult with success status and segments
        """
        import time

        start_time = time.time()

        try:
            # Get diarizer (lazy init)
            diarizer = self._get_diarizer()

            # Diarize
            segments = diarizer.diarize(audio_path, num_speakers=num_speakers)

            duration = time.time() - start_time

            return BatchResult(
                audio_path=audio_path,
                success=True,
                segments=segments,
                duration=duration
            )

        except Exception as e:
            duration = time.time() - start_time

            logger.error(f"Error processing {audio_path.name}: {e}")

            return BatchResult(
                audio_path=audio_path,
                success=False,
                segments=[],
                error=str(e),
                duration=duration
            )

    def _cleanup_memory(self):
        """
        Clean up memory between files

        Note: Keeps the diarizer loaded, only clears caches
        """
        # Run garbage collection
        gc.collect()

        # Clear CUDA cache if available
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                logger.debug("Cleared CUDA cache")
        except ImportError:
            pass

    def close(self):
        """
        Close and clean up diarizer

        Call this when done with batch processing to free all resources
        """
        if self._diarizer is not None:
            logger.info("Cleaning up diarizer...")
            del self._diarizer
            self._diarizer = None
            gc.collect()

            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except ImportError:
                pass

            logger.info("✅ Cleanup complete")


def process_directory(
    directory: Path,
    hf_token: str,
    pattern: str = "*.wav",
    **diarizer_kwargs
) -> List[BatchResult]:
    """
    Convenience function to process all audio files in a directory

    Args:
        directory: Directory containing audio files
        hf_token: Hugging Face token
        pattern: File pattern to match (default: "*.wav")
        **diarizer_kwargs: Additional arguments for BatchDiarizer

    Returns:
        List of BatchResult objects

    Example:
        results = process_directory(
            Path("Eingang/Patient"),
            hf_token="hf_...",
            pattern="*.opus",
            enable_embedding_extraction=True
        )
    """
    # Find all matching audio files
    audio_files = sorted(directory.glob(pattern))

    if not audio_files:
        logger.warning(f"No files matching '{pattern}' found in {directory}")
        return []

    logger.info(f"Found {len(audio_files)} files matching '{pattern}'")

    # Create batch processor
    processor = BatchDiarizer(hf_token=hf_token, **diarizer_kwargs)

    try:
        # Process batch
        results = processor.process_batch(audio_files)
        return results
    finally:
        # Clean up
        processor.close()
