#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chunked Diarization - Process very long audio files by chunking

For audio files longer than 15-60 minutes, diarization can consume
excessive memory and may fail. This module splits long audio into
manageable chunks, processes each chunk independently, and merges
the speaker labels back together.

Key Features:
- Automatic chunking for audio > threshold duration
- Overlap handling to prevent boundary issues
- Speaker label consistency across chunks
- Memory-efficient processing of multi-hour recordings

Usage:
    chunked_diarizer = ChunkedDiarizer(
        diarizer=SpeakerDiarizer(...),
        chunk_duration=900.0,  # 15 minutes
        overlap=30.0  # 30 seconds
    )

    segments = chunked_diarizer.diarize_chunked(audio_path)
"""

import logging
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class ChunkedDiarizer:
    """
    Diarize very long audio by chunking and merging speaker labels

    This wrapper around SpeakerDiarizer handles memory-intensive diarization
    of multi-hour recordings by processing in chunks.
    """

    def __init__(
        self,
        diarizer,
        chunk_duration: float = 900.0,  # 15 minutes
        overlap: float = 30.0,  # 30 seconds overlap
        auto_chunk_threshold: float = 1800.0  # Auto-chunk if > 30 minutes
    ):
        """
        Initialize chunked diarizer

        Args:
            diarizer: SpeakerDiarizer instance to use for processing
            chunk_duration: Duration of each chunk in seconds (default: 900s = 15 min)
            overlap: Overlap between chunks in seconds (default: 30s)
            auto_chunk_threshold: Auto-enable chunking for audio longer than this (default: 1800s = 30 min)
        """
        self.diarizer = diarizer
        self.chunk_duration = chunk_duration
        self.overlap = overlap
        self.auto_chunk_threshold = auto_chunk_threshold

    def diarize_chunked(
        self,
        audio_path: Path,
        num_speakers: Optional[int] = None,
        force_chunking: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Diarize audio file, automatically chunking if too long

        Args:
            audio_path: Path to audio file
            num_speakers: Fixed number of speakers (None for auto-detect)
            force_chunking: Force chunking even for short audio

        Returns:
            List of speaker segments with format:
            [
                {
                    'start': 0.0,
                    'end': 5.2,
                    'speaker': 'Speaker A',
                    'speaker_id': 'SPEAKER_00',
                    'duration': 5.2,
                    'confidence': 0.85
                },
                ...
            ]
        """
        # Get audio duration
        import librosa
        duration = librosa.get_duration(path=str(audio_path))

        logger.info(f"Audio duration: {duration:.1f}s ({duration/60:.1f} min)")

        # Decide whether to use chunking
        use_chunking = force_chunking or (duration > self.auto_chunk_threshold)

        if not use_chunking:
            logger.info("Audio duration below chunking threshold, processing in single pass...")
            return self.diarizer.diarize(audio_path, num_speakers=num_speakers)

        # Process with chunking
        logger.info(
            f"Audio duration {duration/60:.1f}min exceeds chunking threshold "
            f"({self.auto_chunk_threshold/60:.1f}min). Processing in chunks of "
            f"{self.chunk_duration/60:.1f}min with {self.overlap}s overlap..."
        )

        return self._process_chunks(audio_path, num_speakers, duration)

    def _process_chunks(
        self,
        audio_path: Path,
        num_speakers: Optional[int],
        duration: float
    ) -> List[Dict[str, Any]]:
        """
        Process audio in chunks and merge results

        Args:
            audio_path: Path to audio file
            num_speakers: Fixed number of speakers (None for auto-detect)
            duration: Total audio duration

        Returns:
            Merged list of speaker segments
        """
        import librosa
        import soundfile as sf

        # Calculate chunks
        chunks = []
        start = 0
        chunk_idx = 0

        while start < duration:
            end = min(start + self.chunk_duration, duration)
            chunks.append({
                'idx': chunk_idx,
                'start': start,
                'end': end,
                'duration': end - start
            })
            start += (self.chunk_duration - self.overlap)
            chunk_idx += 1

        logger.info(f"Splitting audio into {len(chunks)} chunks")

        # Process each chunk
        all_segments = []

        with tempfile.TemporaryDirectory(prefix="chunked_diarization_") as tmp_dir:
            tmp_path = Path(tmp_dir)

            for chunk in chunks:
                logger.info(
                    f"Processing chunk {chunk['idx']+1}/{len(chunks)}: "
                    f"{chunk['start']:.1f}s - {chunk['end']:.1f}s ({chunk['duration']:.1f}s)"
                )

                # Extract chunk audio
                chunk_path = tmp_path / f"chunk_{chunk['idx']:03d}.wav"
                audio, sr = librosa.load(str(audio_path), sr=16000, mono=True)
                start_sample = int(chunk['start'] * sr)
                end_sample = int(chunk['end'] * sr)
                chunk_audio = audio[start_sample:end_sample]
                sf.write(str(chunk_path), chunk_audio, sr)

                # Diarize chunk
                try:
                    chunk_segments = self.diarizer.diarize(
                        chunk_path,
                        num_speakers=num_speakers
                    )

                    # Adjust timestamps to global time
                    for seg in chunk_segments:
                        seg['start'] += chunk['start']
                        seg['end'] += chunk['start']
                        seg['chunk_idx'] = chunk['idx']

                    all_segments.extend(chunk_segments)

                    logger.info(
                        f"Chunk {chunk['idx']+1} complete: {len(chunk_segments)} segments"
                    )

                except Exception as e:
                    logger.error(f"Failed to process chunk {chunk['idx']}: {e}")
                    # Continue with other chunks

        # Merge overlapping segments
        logger.info(f"Merging {len(all_segments)} segments from {len(chunks)} chunks...")
        merged_segments = self._merge_segments(all_segments, chunks)

        logger.info(f"✅ Chunked diarization complete: {len(merged_segments)} segments")

        return merged_segments

    def _merge_segments(
        self,
        segments: List[Dict[str, Any]],
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Merge segments from overlapping chunks

        Handles:
        - Duplicate segments in overlap regions
        - Speaker label consistency across chunks
        - Segment deduplication

        Args:
            segments: All segments from all chunks (with chunk_idx)
            chunks: List of chunk metadata

        Returns:
            Merged and deduplicated segments
        """
        if not segments:
            return []

        # Sort by start time
        segments = sorted(segments, key=lambda s: s['start'])

        # Relabel speakers for consistency across chunks
        # Strategy: Map speaker IDs from each chunk to global IDs
        segments = self._relabel_speakers_global(segments)

        # Remove duplicates in overlap regions
        merged = []
        for seg in segments:
            # Check if this segment overlaps significantly with last merged segment
            if merged:
                last = merged[-1]
                overlap_start = max(seg['start'], last['start'])
                overlap_end = min(seg['end'], last['end'])
                overlap_duration = max(0, overlap_end - overlap_start)

                # If >50% overlap with same speaker, skip duplicate
                seg_duration = seg['end'] - seg['start']
                if (overlap_duration / seg_duration > 0.5 and
                    seg['speaker'] == last['speaker']):
                    # Extend last segment if this one is longer
                    if seg['end'] > last['end']:
                        last['end'] = seg['end']
                        last['duration'] = last['end'] - last['start']
                    continue

            merged.append(seg)

        return merged

    def _relabel_speakers_global(
        self,
        segments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Relabel speaker IDs for consistency across chunks

        Simple strategy: Assign global speaker labels (A, B, C, ...) based
        on first appearance order.

        Args:
            segments: Segments with chunk-local speaker IDs

        Returns:
            Segments with global speaker labels
        """
        # Map (chunk_idx, local_speaker) -> global_speaker
        speaker_map = {}
        global_speaker_idx = 0

        for seg in segments:
            chunk_idx = seg.get('chunk_idx', 0)
            local_speaker = seg.get('speaker_id', seg.get('speaker', 'Unknown'))

            key = (chunk_idx, local_speaker)

            if key not in speaker_map:
                # Assign new global speaker label
                global_label = chr(65 + global_speaker_idx)  # A, B, C, ...
                speaker_map[key] = f"Speaker {global_label}"
                global_speaker_idx += 1

            # Update segment with global speaker
            seg['speaker'] = speaker_map[key]

        logger.debug(f"Mapped {len(speaker_map)} chunk-local speakers to {global_speaker_idx} global speakers")

        return segments


def get_chunked_diarizer(
    diarizer,
    chunk_duration: float = 900.0,
    overlap: float = 30.0,
    auto_threshold: float = 1800.0
) -> ChunkedDiarizer:
    """
    Factory function to create ChunkedDiarizer

    Args:
        diarizer: SpeakerDiarizer instance
        chunk_duration: Chunk size in seconds (default: 15 min)
        overlap: Overlap between chunks (default: 30s)
        auto_threshold: Auto-chunk threshold (default: 30 min)

    Returns:
        ChunkedDiarizer instance
    """
    return ChunkedDiarizer(
        diarizer=diarizer,
        chunk_duration=chunk_duration,
        overlap=overlap,
        auto_chunk_threshold=auto_threshold
    )