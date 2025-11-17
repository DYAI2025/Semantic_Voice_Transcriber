#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATO Marker Integration - Adds semantic markers to transcript segments

Integrates ATOMarkerDetector with transcription pipeline to automatically
detect and annotate therapeutic markers in transcript text.
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import ATO Marker Detector
try:
    from ato_marker_detector import ATOMarkerDetector
    ATO_DETECTOR_AVAILABLE = True
except ImportError:
    ATO_DETECTOR_AVAILABLE = False

logger = logging.getLogger(__name__)


class ATOMarkerIntegration:
    """Integrates ATO marker detection into transcription pipeline"""

    def __init__(
        self,
        use_curated: bool = True,
        confidence_threshold: float = 0.6,
        max_markers_per_segment: int = 5
    ):
        """
        Initialize ATO marker integration

        Args:
            use_curated: Use curated high-quality marker set (recommended)
            confidence_threshold: Minimum confidence to include marker (0.0-1.0)
            max_markers_per_segment: Maximum markers to annotate per segment
        """
        self.use_curated = use_curated
        self.confidence_threshold = confidence_threshold
        self.max_markers_per_segment = max_markers_per_segment
        self.detector = None

        if not ATO_DETECTOR_AVAILABLE:
            logger.warning("ATOMarkerDetector not available - markers will not be detected")
            return

        try:
            self.detector = ATOMarkerDetector(use_curated=use_curated)
            logger.info(f"ATO Marker Integration initialized (curated={use_curated}, threshold={confidence_threshold})")
        except Exception as e:
            logger.error(f"Failed to initialize ATO Marker Detector: {e}")
            self.detector = None

    def is_available(self) -> bool:
        """Check if ATO marker detection is available"""
        return self.detector is not None

    def add_markers_to_segments(
        self,
        segments: List[Dict[str, Any]],
        combine_adjacent: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Add ATO markers to transcript segments

        Args:
            segments: List of transcript segments with 'text' field
            combine_adjacent: If True, combine text from adjacent segments for better detection

        Returns:
            Segments with added 'ato_markers' field (list of marker IDs)
        """
        if not self.is_available():
            logger.debug("ATO marker detection not available - returning segments unchanged")
            # Add empty marker lists to maintain consistency
            for segment in segments:
                if 'ato_markers' not in segment:
                    segment['ato_markers'] = []
            return segments

        logger.info(f"Detecting ATO markers in {len(segments)} segments...")

        for i, segment in enumerate(segments):
            # Get text to analyze
            text = segment.get('text', '').strip()
            if not text:
                segment['ato_markers'] = []
                continue

            # Optionally combine with adjacent segments for better context
            if combine_adjacent:
                context_text = self._get_context_text(segments, i, context_size=1)
            else:
                context_text = text

            # Detect markers
            detected = self.detector.detect_markers(
                context_text,
                confidence_threshold=self.confidence_threshold
            )

            # Extract top marker IDs
            marker_ids = [
                m['marker_id']
                for m in detected[:self.max_markers_per_segment]
            ]

            # Store marker IDs and full detection data
            segment['ato_markers'] = marker_ids
            segment['ato_marker_details'] = detected[:self.max_markers_per_segment]

            if marker_ids:
                logger.debug(f"Segment {i}: {len(marker_ids)} markers - {marker_ids}")

        total_markers = sum(len(s.get('ato_markers', [])) for s in segments)
        logger.info(f"✅ ATO marker detection complete: {total_markers} markers across {len(segments)} segments")

        return segments

    def _get_context_text(
        self,
        segments: List[Dict[str, Any]],
        index: int,
        context_size: int = 1
    ) -> str:
        """
        Get text with surrounding context for better marker detection

        Args:
            segments: All segments
            index: Index of target segment
            context_size: Number of segments before/after to include

        Returns:
            Combined text with context
        """
        start_idx = max(0, index - context_size)
        end_idx = min(len(segments), index + context_size + 1)

        context_segments = segments[start_idx:end_idx]
        texts = [s.get('text', '').strip() for s in context_segments if s.get('text', '').strip()]

        return ' '.join(texts)

    def get_marker_summary(
        self,
        segments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate summary statistics of detected markers

        Args:
            segments: Segments with ato_markers

        Returns:
            Dict with marker frequencies and categories
        """
        if not self.is_available():
            return {'total': 0, 'unique': 0, 'frequencies': {}, 'categories': {}}

        from collections import Counter

        # Count all markers
        all_markers = []
        for segment in segments:
            all_markers.extend(segment.get('ato_markers', []))

        frequencies = dict(Counter(all_markers))

        # Get top markers
        top_markers = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)[:10]

        # Categorize markers
        categories = {}
        for marker_id in set(all_markers):
            if marker_id in self.detector.markers:
                tags = self.detector.markers[marker_id].get('tags', [])
                for tag in tags:
                    if tag not in categories:
                        categories[tag] = []
                    categories[tag].append(marker_id)

        return {
            'total': len(all_markers),
            'unique': len(frequencies),
            'frequencies': frequencies,
            'top_markers': top_markers,
            'categories': categories
        }


# Standalone test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test data
    test_segments = [
        {
            'id': 0,
            'start': 0.0,
            'end': 5.0,
            'text': 'Ich weiß nicht so recht... vielleicht morgen.',
            'speaker': 'Patient'
        },
        {
            'id': 1,
            'start': 5.5,
            'end': 10.0,
            'text': 'Das macht mich wütend und gleichzeitig traurig.',
            'speaker': 'Patient'
        },
        {
            'id': 2,
            'start': 10.5,
            'end': 15.0,
            'text': 'Können Sie mir mehr darüber erzählen?',
            'speaker': 'Therapeut'
        }
    ]

    # Initialize integration
    integration = ATOMarkerIntegration(use_curated=True, confidence_threshold=0.5)

    if integration.is_available():
        print("\n=== ATO Marker Integration Test ===\n")

        # Add markers
        annotated_segments = integration.add_markers_to_segments(test_segments)

        # Print results
        for seg in annotated_segments:
            print(f"\nSegment {seg['id']}: {seg['speaker']}")
            print(f"  Text: {seg['text']}")
            print(f"  Markers: {seg.get('ato_markers', [])}")

            details = seg.get('ato_marker_details', [])
            for marker in details:
                print(f"    - {marker['marker_id']}: {marker['description']} (confidence: {marker['confidence']:.2f})")

        # Summary
        summary = integration.get_marker_summary(annotated_segments)
        print(f"\n=== Summary ===")
        print(f"Total markers: {summary['total']}")
        print(f"Unique markers: {summary['unique']}")
        print(f"Top markers: {summary['top_markers']}")

        print("\n✅ Test complete\n")
    else:
        print("❌ ATO Marker Detector not available")
