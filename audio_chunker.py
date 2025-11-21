#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio Chunker - Splits large audio files into smaller chunks for memory-efficient processing
"""

import librosa
import soundfile as sf
import numpy as np
from pathlib import Path
from typing import List, Optional
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

    @staticmethod
    def merge_chunk_results_from_files(
        chunk_files: List[str],
        chunks: List[dict],
        cleanup_files: bool = True
    ) -> dict:
        """
        Merge chunk results from temp JSON files incrementally to minimize memory usage

        Args:
            chunk_files: List of paths to temp JSON chunk files
            chunks: List of chunk metadata (start times, durations)
            cleanup_files: Delete temp files after reading

        Returns:
            Merged transcription result
        """
        import json
        import gc
        from pathlib import Path

        # Initialize merged result structure
        merged_result = {
            'segments': [],
            'prosody_features': [],
            'speaker_segments': [],
            'overlapped_speech': [],
            'confidence_scores': {
                'segments': [],
                'low_confidence_segments': [],
                'overall_confidence': 0.0,
                'total_segments': 0
            },
            'prosody_baseline': None
        }

        # Running statistics for baseline calculation
        tempo_sum = 0.0
        tempo_sq_sum = 0.0
        pitch_sum = 0.0
        pitch_sq_sum = 0.0
        energy_sum = 0.0
        energy_sq_sum = 0.0
        feature_count = 0

        total_confidence = 0.0
        total_segments = 0

        # Process each chunk file incrementally
        for i, chunk_file in enumerate(chunk_files):
            chunk_path = Path(chunk_file)

            # Get chunk start time
            chunk_start_time = chunks[i].get('start', i * chunks[i].get('duration', 0)) if i < len(chunks) else 0

            # Load chunk result from file
            with open(chunk_path, 'r', encoding='utf-8') as f:
                chunk_result = json.load(f)

            # Merge segments with timestamp adjustment
            for segment in chunk_result.get('segments', []):
                adjusted_segment = segment.copy()
                adjusted_segment['start'] = segment.get('start', 0) + chunk_start_time
                adjusted_segment['end'] = segment.get('end', 0) + chunk_start_time
                merged_result['segments'].append(adjusted_segment)

            # Merge confidence scores
            chunk_confidence = chunk_result.get('confidence_scores', {})
            chunk_segments = chunk_confidence.get('segments', [])
            total_confidence += sum(seg.get('confidence', 0) for seg in chunk_segments)
            total_segments += len(chunk_segments)

            for seg in chunk_segments:
                adjusted_seg = seg.copy()
                adjusted_seg['start'] = seg.get('start', 0) + chunk_start_time
                adjusted_seg['end'] = seg.get('end', 0) + chunk_start_time
                merged_result['confidence_scores']['segments'].append(adjusted_seg)

            for seg in chunk_confidence.get('low_confidence_segments', []):
                adjusted_seg = seg.copy()
                adjusted_seg['start'] = seg.get('start', 0) + chunk_start_time
                adjusted_seg['end'] = seg.get('end', 0) + chunk_start_time
                merged_result['confidence_scores']['low_confidence_segments'].append(adjusted_seg)

            # Merge prosody features and update running statistics
            for feature in chunk_result.get('prosody_features', []):
                adjusted_feature = feature.copy()
                adjusted_feature['start_time'] = feature.get('start_time', 0) + chunk_start_time
                adjusted_feature['end_time'] = feature.get('end_time', 0) + chunk_start_time
                merged_result['prosody_features'].append(adjusted_feature)

                # Update running statistics
                tempo = feature.get('tempo_wpm')
                pitch = feature.get('pitch_mean_hz')
                energy = feature.get('energy_rms')

                if tempo is not None:
                    tempo_sum += tempo
                    tempo_sq_sum += tempo ** 2
                if pitch is not None:
                    pitch_sum += pitch
                    pitch_sq_sum += pitch ** 2
                if energy is not None:
                    energy_sum += energy
                    energy_sq_sum += energy ** 2

                if tempo is not None or pitch is not None or energy is not None:
                    feature_count += 1

            # Merge speaker segments
            for speaker_seg in chunk_result.get('speaker_segments', []):
                adjusted_speaker = speaker_seg.copy()
                adjusted_speaker['start'] = speaker_seg.get('start', 0) + chunk_start_time
                adjusted_speaker['end'] = speaker_seg.get('end', 0) + chunk_start_time
                merged_result['speaker_segments'].append(adjusted_speaker)

            # Merge overlapped speech
            for overlap in chunk_result.get('overlapped_speech', []):
                adjusted_overlap = overlap.copy()
                adjusted_overlap['start'] = overlap.get('start', 0) + chunk_start_time
                adjusted_overlap['end'] = overlap.get('end', 0) + chunk_start_time
                merged_result['overlapped_speech'].append(adjusted_overlap)

            # Delete chunk result from memory
            del chunk_result
            gc.collect()

            # Delete temp file if cleanup enabled
            if cleanup_files:
                try:
                    chunk_path.unlink()
                except Exception as e:
                    logger.warning(f"Could not delete temp file {chunk_path}: {e}")

        # Calculate overall confidence
        if total_segments > 0:
            merged_result['confidence_scores']['overall_confidence'] = total_confidence / total_segments
        merged_result['confidence_scores']['total_segments'] = total_segments

        # Calculate baseline from running statistics
        if feature_count > 0:
            tempo_mean = tempo_sum / feature_count
            tempo_std = np.sqrt(max(0, tempo_sq_sum / feature_count - tempo_mean ** 2))

            pitch_mean = pitch_sum / feature_count
            pitch_std = np.sqrt(max(0, pitch_sq_sum / feature_count - pitch_mean ** 2))

            energy_mean = energy_sum / feature_count
            energy_std = np.sqrt(max(0, energy_sq_sum / feature_count - energy_mean ** 2))

            merged_result['prosody_baseline'] = {
                'tempo_wpm_mean': float(tempo_mean),
                'tempo_wpm_std': float(tempo_std),
                'pitch_mean_hz': float(pitch_mean),
                'pitch_std_hz': float(pitch_std),
                'energy_rms_mean': float(energy_mean),
                'energy_rms_std': float(energy_std)
            }

        logger.info(f"Merged transcription contains {len(merged_result['segments'])} segments")
        return merged_result


def process_large_audio_with_chunking(
    audio_path: str,
    transcribe_func,
    chunk_duration: float = 300.0,
    overlap_duration: float = 5.0,
    cleanup_memory: bool = True,
    **transcribe_kwargs
) -> dict:
    """
    Process a large audio file using chunking with file-based merge to reduce memory

    Args:
        audio_path: Path to audio file
        transcribe_func: Function to transcribe each chunk
        chunk_duration: Duration of each chunk in seconds
        overlap_duration: Overlap between chunks in seconds
        cleanup_memory: Enable memory cleanup between chunks
        **transcribe_kwargs: Additional kwargs for transcribe_func

    Returns:
        Merged transcription result dictionary
    """
    import tempfile
    import json
    import gc
    from pathlib import Path

    logger.info(f"Processing large audio file with chunking: {audio_path}")

    # Create temp directory for chunk files
    temp_dir = tempfile.mkdtemp(prefix="svt_chunks_")
    chunk_files = []
    chunk_paths = []  # Initialize to empty list for cleanup

    try:
        # Split audio into overlapping chunks
        chunker = AudioChunker(chunk_duration=chunk_duration)
        chunk_paths = chunker.process_with_overlap(
            audio_path=audio_path,
            overlap_duration=overlap_duration
        )

        # Check memory before processing
        try:
            import psutil
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            memory_status = {
                'ram_free_gb': mem.available / (1024**3),
                'swap_percent': swap.percent
            }
            logger.info(f"Memory check OK: {memory_status['ram_free_gb']:.1f} GB free, SWAP {memory_status['swap_percent']}%")

            if memory_status['swap_percent'] > 80:
                logger.warning(f"⚠️ SWAP critically high: {memory_status['swap_percent']}%")
        except ImportError:
            logger.warning("psutil not available, skipping memory check")
            memory_status = {'ram_free_gb': 0, 'swap_percent': 0}

        # Process each chunk and save to temp file
        for i, chunk_path in enumerate(chunk_paths):
            logger.info(f"Processing chunk {i+1}/{len(chunk_paths)}: {chunk_path}")

            # Transcribe chunk
            chunk_result = transcribe_func(chunk_path, **transcribe_kwargs)

            # Write chunk result to temp JSON file
            chunk_file = Path(temp_dir) / f"chunk_{i:03d}.json"
            with open(chunk_file, 'w', encoding='utf-8') as f:
                json.dump(chunk_result, f, ensure_ascii=False, indent=2)

            chunk_files.append(str(chunk_file))

            # Clean up chunk result from memory
            del chunk_result

            if cleanup_memory:
                gc.collect()
                gc.collect()  # Run twice for thorough cleanup

                # Clear PyTorch CUDA cache if available
                try:
                    import torch
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                        logger.debug(f"Cleared CUDA cache after chunk {i+1}")
                except ImportError:
                    # torch is not installed; skip CUDA cache clearing
                    pass

                logger.info(f"Cleared memory after processing chunk {i+1}/{len(chunk_paths)}")

                # Check memory after cleanup
                try:
                    import psutil
                    mem = psutil.virtual_memory()
                    swap = psutil.swap_memory()
                    memory_status = {
                        'ram_free_gb': mem.available / (1024**3),
                        'swap_percent': swap.percent
                    }
                    if memory_status['swap_percent'] > 80:
                        logger.warning(f"⚠️ SWAP critically high: {memory_status['swap_percent']}%")
                    logger.info(f"Memory check OK: {memory_status['ram_free_gb']:.1f} GB free, SWAP {memory_status['swap_percent']}%")
                except ImportError:
                    pass

        # Merge results from chunk files
        logger.info(f"Merging results from {len(chunk_files)} audio chunks")

        # Create chunks metadata for merge function
        chunks = []
        effective_chunk_duration = chunk_duration - overlap_duration
        for i in range(len(chunk_files)):
            chunks.append({
                'start': i * effective_chunk_duration,
                'duration': chunk_duration
            })

        merged_result = AudioChunker.merge_chunk_results_from_files(
            chunk_files=chunk_files,
            chunks=chunks,
            cleanup_files=True
        )

        logger.info("Successfully processed and merged all chunks")
        return merged_result

    finally:
        # Clean up temp directory
        try:
            Path(temp_dir).rmdir()
        except OSError:
            logger.warning(f"Could not remove temp directory: {temp_dir}")

        # Clean up temporary audio chunk files
        for chunk_path in chunk_paths:
            try:
                Path(chunk_path).unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"Could not delete temporary chunk file {chunk_path}: {e}")