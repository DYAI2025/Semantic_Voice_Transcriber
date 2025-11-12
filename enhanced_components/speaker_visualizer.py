from typing import Dict, Optional, List
from datetime import datetime

class SpeakerVisualizer:
    """Enhanced speaker visualization for transcripts"""

    def __init__(self):
        """Initialize speaker visualizer with color palette"""
        self.speaker_colors = {}
        self.color_palette = [
            'blue', 'green', 'purple', 'orange', 'red', 'cyan', 'magenta', 'yellow'
        ]
        self.next_color_index = 0

    def get_speaker_color(self, speaker: str) -> str:
        """Get consistent color for a speaker

        Args:
            speaker: Speaker identifier

        Returns:
            Color name for the speaker
        """
        if speaker not in self.speaker_colors:
            if self.next_color_index < len(self.color_palette):
                self.speaker_colors[speaker] = self.color_palette[self.next_color_index]
                self.next_color_index += 1
            else:
                # Fallback if we run out of colors
                self.speaker_colors[speaker] = 'gray'

        return self.speaker_colors[speaker]

    def format_segment(self, segment: Dict,
                      include_confidence: bool = True,
                      include_timestamp: bool = True) -> str:
        """Format a transcript segment with enhanced visualization

        Args:
            segment: Segment dict with speaker, text, etc.
            include_confidence: Whether to show confidence score
            include_timestamp: Whether to show timestamp

        Returns:
            Formatted segment string
        """
        parts = []

        # Add timestamp if requested
        if include_timestamp and 'timestamp' in segment:
            parts.append(f"[{segment['timestamp']}]")

        # Add speaker with formatting
        speaker = segment.get('speaker', 'Unknown')
        color = self.get_speaker_color(speaker)

        # Add confidence if requested
        confidence_str = ""
        if include_confidence and 'confidence' in segment:
            conf = segment['confidence']
            if conf >= 0.9:
                confidence_str = " (confident: {:.2f})".format(conf)
            elif conf >= 0.7:
                confidence_str = " (likely: {:.2f})".format(conf)
            else:
                confidence_str = " (uncertain: {:.2f})".format(conf)

        parts.append(f"**{speaker}**{confidence_str}:")

        # Add indented text
        text = segment.get('text', '')
        parts.append(f"    {text}")

        return ' '.join(parts)

    def format_overlap(self, overlap_segments: List[Dict], duration: float) -> str:
        """Format overlapped speech segments

        Args:
            overlap_segments: List of overlapping segments
            duration: Duration of overlap in seconds

        Returns:
            Formatted overlap string
        """
        lines = [f"**[ÜBERLAPPUNG {duration:.1f}s]**"]

        for segment in overlap_segments:
            speaker = segment.get('speaker', 'Unknown')
            text = segment.get('text', '')
            lines.append(f"    {speaker[0]}: \"{text}\"")

        return '\n'.join(lines)

    def create_header(self, metadata: Dict) -> str:
        """Create enhanced transcript header

        Args:
            metadata: Metadata dict with file info, speakers, etc.

        Returns:
            Formatted header string
        """
        lines = []
        lines.append("# Transkript mit erweiterter Sprechererkennung")
        lines.append("")

        if 'original_file' in metadata:
            lines.append(f"**Original-Datei:** {metadata['original_file']}")

        if 'date_recorded' in metadata:
            lines.append(f"**Aufnahme am:** {metadata['date_recorded']}")

        if 'date_processed' in metadata:
            lines.append(f"**Verarbeitet am:** {metadata['date_processed']}")

        if 'speakers' in metadata:
            speakers_str = ', '.join([
                f"{s} ({self.get_speaker_color(s)})"
                for s in metadata['speakers']
            ])
            lines.append(f"**Sprecher:** {speakers_str}")

        if 'turning_points_detected' in metadata:
            lines.append(f"**Wendepunkte erkannt:** {metadata['turning_points_detected']}")

        lines.append("")
        lines.append("---")
        lines.append("")

        return '\n'.join(lines)

    def reset_colors(self):
        """Reset speaker color assignments"""
        self.speaker_colors = {}
        self.next_color_index = 0