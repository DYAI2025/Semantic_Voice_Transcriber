#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio Chunker - Splits large audio files into smaller chunks for memory-efficient processing
"""

import librosa
import soundfile as sf
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
import tempfile
import logging

logger = logging.getLogger(__name__)


class AudioChunker:
    """
    Splits large audio files into smaller chunks to reduce memory usage during processing.
    Each chunk can be processed individually and results can be merged back together.
    """

    def __init__(self, chunk_duration: float = 300.0):  # 5 minutes default
        """
        Initialize the audio chunker

        Args:
            chunk_duration: Duration of each chunk in seconds (default 300s = 5 minutes)
        """
        self.chunk_duration = chunk_duration

    def split_audio_file(self, audio_path: str, output_dir: Optional[str] = None) -> List[str]:
        """
        Splits an audio file into smaller chunks

        Args:
            audio_path: Path to the input audio file
            output_dir: Directory to save chunks (if None, uses temporary directory)

        Returns:
            List of paths to the created chunk files
        """
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="audio_chunks_")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Load the full audio file
        audio, sample_rate = librosa.load(audio_path, sr=None, mono=True)
        duration = librosa.get_duration(y=audio, sr=sample_rate)

        logger.info(f"Splitting {audio_path} ({duration:.2f}s) into {self.chunk_duration}s chunks")
        logger.info(f"Sample rate: {sample_rate}Hz, Channels: 1")

        # Calculate number of chunks needed
        num_chunks = int(np.ceil(duration / self.chunk_duration))
        chunk_paths = []

        # Split the audio into chunks
        for i in range(num_chunks):
            start_time = i * self.chunk_duration
            end_time = min((i + 1) * self.chunk_duration, duration)

            # Calculate sample indices
            start_sample = int(start_time * sample_rate)
            end_sample = int(end_time * sample_rate)

            # Extract chunk from audio
            chunk_audio = audio[start_sample:end_sample]

            # Generate output filename
            original_name = Path(audio_path).stem
            chunk_filename = f"{original_name}_chunk_{i:03d}.wav"
            chunk_path = output_dir / chunk_filename

            # Save chunk to file
            sf.write(chunk_path, chunk_audio, sample_rate)
            chunk_paths.append(str(chunk_path))

            logger.info(f"Created chunk {i+1}/{num_chunks}: {chunk_path} ({len(chunk_audio)/sample_rate:.2f}s)")

        logger.info(f"Successfully split audio into {len(chunk_paths)} chunks")
        return chunk_paths

    def process_with_overlap(self, audio_path: str, output_dir: Optional[str] = None, 
                           overlap_duration: float = 5.0) -> List[str]:
        """
        Splits an audio file into chunks with overlap to preserve context at boundaries

        Args:
            audio_path: Path to the input audio file
            output_dir: Directory to save chunks (if None, uses temporary directory)
            overlap_duration: Duration of overlap in seconds

        Returns:
            List of paths to the created chunk files
        """
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="audio_chunks_overlap_")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Load the full audio file
        audio, sample_rate = librosa.load(audio_path, sr=None, mono=True)
        duration = librosa.get_duration(y=audio, sr=sample_rate)

        logger.info(f"Splitting {audio_path} ({duration:.2f}s) into {self.chunk_duration}s chunks with {overlap_duration}s overlap")
        logger.info(f"Sample rate: {sample_rate}Hz, Channels: 1")

        # Calculate number of chunks needed
        effective_chunk_duration = self.chunk_duration - overlap_duration
        num_chunks = int(np.ceil(duration / effective_chunk_duration))
        chunk_paths = []

        # Split the audio into overlapping chunks
        for i in range(num_chunks):
            start_time = i * effective_chunk_duration
            end_time = min(start_time + self.chunk_duration, duration)

            # Calculate sample indices
            start_sample = int(start_time * sample_rate)
            end_sample = int(end_time * sample_rate)

            # Extract chunk from audio
            chunk_audio = audio[start_sample:end_sample]

            # Generate output filename
            original_name = Path(audio_path).stem
            chunk_filename = f"{original_name}_chunk_{i:03d}_overlap.wav"
            chunk_path = output_dir / chunk_filename

            # Save chunk to file
            sf.write(chunk_path, chunk_audio, sample_rate)
            chunk_paths.append(str(chunk_path))

            logger.info(f"Created overlapping chunk {i+1}/{num_chunks}: {chunk_path} ({len(chunk_audio)/sample_rate:.2f}s)")

        logger.info(f"Successfully split audio into {len(chunk_paths)} overlapping chunks")
        return chunk_paths

    @staticmethod
    def merge_transcription_results(chunk_results: List[dict], audio_path: str, 
                                  chunk_duration: float = 300.0, 
                                  overlap_duration: float = 0.0) -> dict:
        """
        Merges transcription results from multiple chunks back into a single result

        Args:
            chunk_results: List of transcription results from each chunk
            audio_path: Path to the original audio file
            chunk_duration: Duration of each chunk in seconds
            overlap_duration: Duration of overlap between chunks in seconds

        Returns:
            Merged transcription result
        """
        logger.info(f"Merging results from {len(chunk_results)} audio chunks")

        # Initialize merged result structure
        merged_result = {
            'text': '',
            'segments': [],
            'confidence_scores': {
                'overall_confidence': 0.0,
                'segments': [],
                'low_confidence_segments': [],
                'low_confidence_threshold': 0.5,
                'total_segments': 0
            },
            'prosody_features': [],
            'prosody_baseline': None,
            'speaker_segments': [],
            'overlapped_speech': []
        }

        total_confidence = 0.0
        total_segments = 0

        # Calculate effective chunk duration if overlapping
        effective_chunk_duration = chunk_duration - overlap_duration

        # Process each chunk result
        for i, chunk_result in enumerate(chunk_results):
            # Adjust timestamps for the current chunk
            chunk_start_time = i * effective_chunk_duration

            # Merge text
            if i == 0:
                # For first chunk, use text as is
                merged_result['text'] += chunk_result.get('text', '')
            else:
                # For subsequent chunks, add with space
                merged_result['text'] += ' ' + chunk_result.get('text', '').lstrip()

            # Merge segments with adjusted timestamps
            chunk_segments = chunk_result.get('segments', [])
            for segment in chunk_segments:
                adjusted_segment = segment.copy()
                adjusted_segment['start'] = segment.get('start', 0) + chunk_start_time
                adjusted_segment['end'] = segment.get('end', 0) + chunk_start_time
                merged_result['segments'].append(adjusted_segment)

            # Merge confidence scores
            chunk_confidence = chunk_result.get('confidence_scores', {})
            chunk_segments = chunk_confidence.get('segments', [])
            total_confidence += sum(seg.get('confidence', 0) for seg in chunk_segments)
            total_segments += len(chunk_segments)

            # Add chunk segments to the main segments list
            for seg in chunk_confidence.get('segments', []):
                adjusted_seg = seg.copy()
                adjusted_seg['start'] = seg.get('start', 0) + chunk_start_time
                adjusted_seg['end'] = seg.get('end', 0) + chunk_start_time
                merged_result['confidence_scores']['segments'].append(adjusted_seg)

            # Add low confidence segments
            for seg in chunk_confidence.get('low_confidence_segments', []):
                adjusted_seg = seg.copy()
                adjusted_seg['start'] = seg.get('start', 0) + chunk_start_time
                adjusted_seg['end'] = seg.get('end', 0) + chunk_start_time
                merged_result['confidence_scores']['low_confidence_segments'].append(adjusted_seg)

            # Merge prosody features
            chunk_prosody = chunk_result.get('prosody_features', [])
            for feature in chunk_prosody:
                adjusted_feature = feature.copy()
                adjusted_feature['start_time'] = feature.get('start_time', 0) + chunk_start_time
                adjusted_feature['end_time'] = feature.get('end_time', 0) + chunk_start_time
                merged_result['prosody_features'].append(adjusted_feature)

            # Merge speaker segments
            chunk_speakers = chunk_result.get('speaker_segments', [])
            for speaker_seg in chunk_speakers:
                adjusted_speaker = speaker_seg.copy()
                adjusted_speaker['start'] = speaker_seg.get('start', 0) + chunk_start_time
                adjusted_speaker['end'] = speaker_seg.get('end', 0) + chunk_start_time
                merged_result['speaker_segments'].append(adjusted_speaker)

            # Merge overlapped speech
            chunk_overlaps = chunk_result.get('overlapped_speech', [])
            for overlap in chunk_overlaps:
                adjusted_overlap = overlap.copy()
                adjusted_overlap['start'] = overlap.get('start', 0) + chunk_start_time
                adjusted_overlap['end'] = overlap.get('end', 0) + chunk_start_time
                merged_result['overlapped_speech'].append(adjusted_overlap)

        # Calculate overall confidence
        if total_segments > 0:
            merged_result['confidence_scores']['overall_confidence'] = total_confidence / total_segments
        merged_result['confidence_scores']['total_segments'] = total_segments

        # Calculate baseline from merged features
        merged_result['prosody_baseline'] = AudioChunker._calculate_merged_baseline(
            merged_result['prosody_features']
        )

        logger.info(f"Merged transcription contains {len(merged_result['segments'])} segments")
        return merged_result

    @staticmethod
    def _calculate_merged_baseline(prosody_features: List[dict]) -> Optional[dict]:
        """
        Calculate baseline from merged prosody features
        """
        if not prosody_features:
            return None

        # Extract values for baseline calculation
        tempo_values = [f['tempo_wpm'] for f in prosody_features if f.get('tempo_wpm') is not None]
        pitch_values = [f['pitch_mean_hz'] for f in prosody_features if f.get('pitch_mean_hz') is not None]
        energy_values = [f['energy_rms'] for f in prosody_features if f.get('energy_rms') is not None]

        # Calculate mean and std for each feature
        baseline = {
            'tempo_wpm_mean': float(np.mean(tempo_values)) if tempo_values else 0.0,
            'tempo_wpm_std': float(np.std(tempo_values)) if tempo_values else 0.0,
            'pitch_mean_hz': float(np.mean(pitch_values)) if pitch_values else 0.0,
            'pitch_std_hz': float(np.std(pitch_values)) if pitch_values else 0.0,
            'energy_rms_mean': float(np.mean(energy_values)) if energy_values else 0.0,
            'energy_rms_std': float(np.std(energy_values)) if energy_values else 0.0
        }

        return baseline


def process_large_audio_with_chunking(
    audio_path: str,
    transcribe_func,
    chunk_duration: float = 300.0,  # 5 minutes default
    overlap_duration: float = 5.0,   # 5 seconds overlap
    cleanup_memory: bool = True,     # Clean up memory between chunks
    **transcribe_kwargs
) -> dict:
    """
    Process a large audio file using chunking to reduce memory usage

    Args:
        audio_path: Path to the large audio file
        transcribe_func: Function to call for transcribing each chunk
        chunk_duration: Duration of each chunk in seconds
        overlap_duration: Duration of overlap between chunks in seconds
        cleanup_memory: Whether to perform memory cleanup between chunks
        **transcribe_kwargs: Additional arguments to pass to the transcribe function

    Returns:
        Merged transcription result for the entire audio file
    """
    import gc  # Import garbage collection module
    
    logger.info(f"Processing large audio file with chunking: {audio_path}")

    # Create chunker instance
    chunker = AudioChunker(chunk_duration=chunk_duration)

    # Split audio into chunks
    chunk_paths = chunker.process_with_overlap(
        audio_path=audio_path,
        overlap_duration=overlap_duration
    )

    try:
        # Process each chunk
        chunk_results = []
        for i, chunk_path in enumerate(chunk_paths):
            # Memory Safety Check before processing each chunk
            try:
                import psutil
                mem = psutil.virtual_memory()
                swap = psutil.swap_memory()
                free_gb = mem.available / (1024**3)

                # Check if enough memory is available
                MIN_FREE_GB = 3.0
                if free_gb < MIN_FREE_GB:
                    raise MemoryError(
                        f"Insufficient memory: {free_gb:.1f} GB free (need {MIN_FREE_GB} GB). "
                        f"SWAP: {swap.percent:.0f}% used"
                    )

                # Warning if SWAP is critically high
                if swap.percent > 90:
                    logger.warning(f"⚠️ SWAP critically high: {swap.percent:.0f}%")

                logger.info(f"Memory check OK: {free_gb:.1f} GB free, SWAP {swap.percent:.0f}%")
            except ImportError:
                logger.warning("psutil not available, skipping memory check")
            except MemoryError as e:
                logger.error(f"Memory safety check failed: {e}")
                raise

            logger.info(f"Processing chunk {i+1}/{len(chunk_paths)}: {chunk_path}")

            # Call the transcription function on the chunk
            chunk_result = transcribe_func(chunk_path, **transcribe_kwargs)
            chunk_results.append(chunk_result)
            
            # Clean up memory if requested
            if cleanup_memory:
                # Force aggressive garbage collection to free up memory
                gc.collect()
                gc.collect()  # Run twice for more thorough cleanup

                # Clear PyTorch CUDA cache if available
                try:
                    import torch
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                        logger.debug(f"Cleared CUDA cache after chunk {i+1}")
                except ImportError:
                    pass

                logger.info(f"Cleared memory after processing chunk {i+1}/{len(chunk_paths)}")

        # Merge results from all chunks
        merged_result = chunker.merge_transcription_results(
            chunk_results=chunk_results,
            audio_path=audio_path,
            chunk_duration=chunk_duration,
            overlap_duration=overlap_duration
        )

        logger.info("Successfully processed and merged all chunks")
        return merged_result

    finally:
        # Clean up temporary chunk files
        for chunk_path in chunk_paths:
            try:
                Path(chunk_path).unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"Could not delete temporary chunk file {chunk_path}: {e}")