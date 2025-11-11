#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Output Formatter - Generates annotated Markdown and JSON sidecar outputs

Creates:
1. Annotated Markdown for therapists (human-readable with markers)
2. JSON sidecar for system processing (structured prosody data)
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    from html_formatter import HTMLFormatter, WEASYPRINT_AVAILABLE
    HTML_FORMATTER_AVAILABLE = True
except ImportError:
    HTML_FORMATTER_AVAILABLE = False
    WEASYPRINT_AVAILABLE = False


class OutputFormatter:
    """
    Formats transcription results with prosody features into
    annotated Markdown and JSON outputs
    """

    def __init__(
        self,
        tempo_threshold: float = 20.0,  # % deviation to trigger marker
        pitch_threshold: float = 15.0,  # % deviation to trigger marker
        energy_threshold: float = 25.0,  # % deviation to trigger marker
        pause_threshold: float = 1000.0  # milliseconds
    ):
        """
        Initialize output formatter

        Args:
            tempo_threshold: % deviation from baseline to mark tempo changes
            pitch_threshold: % deviation from baseline to mark pitch changes
            energy_threshold: % deviation from baseline to mark energy changes
            pause_threshold: Pause duration in ms to mark significant pauses
        """
        self.tempo_threshold = tempo_threshold
        self.pitch_threshold = pitch_threshold
        self.energy_threshold = energy_threshold
        self.pause_threshold = pause_threshold

    def format_transcript(
        self,
        transcription_result: Dict[str, Any],
        audio_filename: str,
        output_path: Path,
        include_prosody_markers: bool = True
    ) -> Dict[str, Path]:
        """
        Format transcription with prosody features

        Args:
            transcription_result: Result from transcribe_with_whisper
            audio_filename: Name of the audio file
            output_path: Base output path (without extension)
            include_prosody_markers: Whether to include prosody markers in Markdown

        Returns:
            Dict with paths to created files: {'markdown': Path, 'json': Path}
        """
        # Extract data
        segments = transcription_result.get('segments', [])
        prosody_features = transcription_result.get('prosody_features', [])
        prosody_baseline = transcription_result.get('prosody_baseline', None)
        confidence_scores = transcription_result.get('confidence_scores', {})

        # Generate Markdown
        markdown_path = output_path.with_suffix('.md')
        markdown_content = self._generate_markdown(
            audio_filename,
            segments,
            prosody_features,
            prosody_baseline,
            confidence_scores,
            include_prosody_markers
        )

        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        # Generate JSON sidecar
        json_path = output_path.with_suffix('.prosody.json')
        json_data = self._generate_json_sidecar(
            audio_filename,
            segments,
            prosody_features,
            prosody_baseline,
            confidence_scores
        )

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        return {
            'markdown': markdown_path,
            'json': json_path
        }

    def format_all(
        self,
        transcription_result: Dict[str, Any],
        audio_filename: str,
        output_path: Path,
        include_prosody_markers: bool = True,
        generate_html: bool = True,
        generate_pdf: bool = True,
        generate_csv: bool = True
    ) -> Dict[str, Optional[Path]]:
        """
        Generate ALL output formats: Markdown, JSON, HTML, PDF

        Args:
            transcription_result: Result from transcribe_with_whisper
            audio_filename: Name of the audio file
            output_path: Base output path (without extension)
            include_prosody_markers: Whether to include prosody markers
            generate_html: Whether to generate HTML
            generate_pdf: Whether to generate PDF

        Returns:
            Dict with paths: {'markdown': Path, 'json': Path, 'html': Path, 'pdf': Path}
        """
        # Generate Markdown + JSON
        files = self.format_transcript(
            transcription_result,
            audio_filename,
            output_path,
            include_prosody_markers
        )

        # Generate HTML + PDF if requested
        if generate_html and HTML_FORMATTER_AVAILABLE:
            html_formatter = HTMLFormatter()

            # Generate HTML
            html_path = html_formatter.generate_html(
                transcription_result,
                audio_filename,
                output_path
            )
            files['html'] = html_path

            # Generate PDF
            if generate_pdf and WEASYPRINT_AVAILABLE:
                pdf_path = html_formatter.generate_pdf(
                    transcription_result,
                    audio_filename,
                    output_path
                )
                files['pdf'] = pdf_path
            else:
                files['pdf'] = None
        else:
            files['html'] = None
            files['pdf'] = None

        # Generate CSV if requested
        if generate_csv:
            csv_path = self.generate_csv(transcription_result, output_path)
            files['csv'] = csv_path
        else:
            files['csv'] = None

        return files

    def generate_csv(
        self,
        transcription_result: Dict[str, Any],
        output_path: Path
    ) -> Path:
        """
        Generate CSV export for data analysis

        Args:
            transcription_result: Result from transcribe_with_whisper
            output_path: Base output path (without extension)

        Returns:
            Path to CSV file
        """
        segments = transcription_result.get('segments', [])
        prosody_features = transcription_result.get('prosody_features', [])
        confidence_scores = transcription_result.get('confidence_scores', {})

        csv_path = output_path.with_suffix('.csv')

        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'index',
                'speaker',
                'start_time',
                'end_time',
                'duration',
                'text',
                'confidence',
                'has_overlap',
                'overlap_duration_s',
                'tempo_wpm',
                'tempo_deviation_pct',
                'pitch_mean_hz',
                'pitch_deviation_pct',
                'energy_rms',
                'energy_deviation_pct',
                'pause_before_ms',
                'jitter_local',
                'shimmer_local'
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for i, segment in enumerate(segments):
                row = {
                    'index': i,
                    'speaker': segment.get('speaker', ''),  # Get speaker from segment
                    'start_time': segment.get('start', 0.0),
                    'end_time': segment.get('end', 0.0),
                    'duration': segment.get('end', 0.0) - segment.get('start', 0.0),
                    'text': segment.get('text', '').strip(),
                    'confidence': confidence_scores.get('segments', [])[i].get('confidence', 0.0)
                    if i < len(confidence_scores.get('segments', [])) else 0.0,
                    'has_overlap': segment.get('has_overlap', False),
                    'overlap_duration_s': segment.get('overlap_duration', 0.0)
                }

                # Add prosody data if available
                if i < len(prosody_features):
                    prosody = prosody_features[i]
                    row.update({
                        'tempo_wpm': prosody.get('tempo_wpm', ''),
                        'tempo_deviation_pct': prosody.get('tempo_deviation_pct', ''),
                        'pitch_mean_hz': prosody.get('pitch_mean_hz', ''),
                        'pitch_deviation_pct': prosody.get('pitch_deviation_pct', ''),
                        'energy_rms': prosody.get('energy_rms', ''),
                        'energy_deviation_pct': prosody.get('energy_deviation_pct', ''),
                        'pause_before_ms': prosody.get('pause_before_ms', ''),
                        'jitter_local': prosody.get('jitter_local', ''),
                        'shimmer_local': prosody.get('shimmer_local', '')
                    })
                else:
                    # Fill with empty values
                    for field in ['tempo_wpm', 'tempo_deviation_pct', 'pitch_mean_hz',
                                  'pitch_deviation_pct', 'energy_rms', 'energy_deviation_pct',
                                  'pause_before_ms', 'jitter_local', 'shimmer_local']:
                        row[field] = ''

                writer.writerow(row)

        return csv_path

    def _generate_markdown(
        self,
        audio_filename: str,
        segments: List[Dict[str, Any]],
        prosody_features: List[Dict[str, Any]],
        prosody_baseline: Optional[Dict[str, Any]],
        confidence_scores: Dict[str, Any],
        include_prosody_markers: bool
    ) -> str:
        """Generate annotated Markdown transcript"""

        lines = []

        # Header
        lines.append(f"# Transkription: {audio_filename}")
        lines.append(f"\n*Erstellt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        # Overall statistics
        overall_conf = confidence_scores.get('overall_confidence', 0.0)
        total_segments = len(segments)

        lines.append(f"## Übersicht\n")
        lines.append(f"- **Gesamt-Konfidenz:** {overall_conf:.1%}")
        lines.append(f"- **Segmente:** {total_segments}")

        if prosody_baseline:
            lines.append(f"\n### Prosodische Baseline")
            lines.append(f"- **Tempo:** {prosody_baseline.get('tempo_wpm_mean', 0):.1f} WPM")
            lines.append(f"- **Tonhöhe:** {prosody_baseline.get('pitch_mean_hz', 0):.1f} Hz")
            lines.append(f"- **Energie:** {prosody_baseline.get('energy_rms_mean', 0):.4f}")

        lines.append(f"\n---\n")

        # Segments with prosody markers
        lines.append(f"## Transkript\n")

        for i, segment in enumerate(segments):
            start = segment.get('start', 0.0)
            end = segment.get('end', 0.0)
            text = segment.get('text', '').strip()
            speaker = segment.get('speaker', None)  # Get speaker label if available
            has_overlap = segment.get('has_overlap', False)  # Get overlap status

            # Get prosody for this segment
            prosody = None
            if i < len(prosody_features):
                prosody = prosody_features[i]

            # Format timestamp
            timestamp = self._format_timestamp(start, end)

            # Build segment line with speaker label
            if speaker:
                segment_line = f"**[{timestamp}] {speaker}:** {text}"
            else:
                segment_line = f"**[{timestamp}]** {text}"

            # Add prosody markers if available
            if include_prosody_markers and prosody:
                markers = self._generate_prosody_markers(prosody)
                if markers:
                    segment_line += f" {markers}"

            # Add overlap marker if detected
            if has_overlap:
                overlap_duration = segment.get('overlap_duration', 0.0)
                segment_line += f" `[ÜBERLAPPUNG {overlap_duration:.1f}s]`"

            lines.append(segment_line)

            # Add prosody details as sub-bullets (optional, for debugging)
            if prosody and include_prosody_markers:
                details = self._generate_prosody_details(prosody)
                if details:
                    lines.append(f"  *{details}*")

            lines.append("")  # Blank line between segments

        # Footer with legend
        if include_prosody_markers:
            lines.append("\n---\n")
            lines.append("### Legende\n")
            lines.append("- `[TEMPO↓]` = Langsames Sprechen (>20% unter Baseline)")
            lines.append("- `[TEMPO↑]` = Schnelles Sprechen (>20% über Baseline)")
            lines.append("- `[PITCH↓]` = Tiefe Stimme (>15% unter Baseline)")
            lines.append("- `[PITCH↑]` = Hohe Stimme (>15% über Baseline)")
            lines.append("- `[ENERGY↓]` = Leise (>25% unter Baseline)")
            lines.append("- `[ENERGY↑]` = Laut (>25% über Baseline)")
            lines.append("- `[PAUSE]` = Signifikante Pause (>1s)")
            lines.append("- `[ÜBERLAPPUNG]` = Mehrere Sprecher gleichzeitig")

        return "\n".join(lines)

    def _generate_json_sidecar(
        self,
        audio_filename: str,
        segments: List[Dict[str, Any]],
        prosody_features: List[Dict[str, Any]],
        prosody_baseline: Optional[Dict[str, Any]],
        confidence_scores: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate structured JSON sidecar"""

        return {
            "metadata": {
                "audio_file": audio_filename,
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "total_segments": len(segments)
            },
            "baseline": prosody_baseline,
            "overall_confidence": confidence_scores.get('overall_confidence', 0.0),
            "segments": [
                {
                    "index": i,
                    "speaker": seg.get('speaker', None),  # Speaker label
                    "start": seg.get('start', 0.0),
                    "end": seg.get('end', 0.0),
                    "text": seg.get('text', '').strip(),
                    "confidence": confidence_scores.get('segments', [])[i].get('confidence', 0.0)
                    if i < len(confidence_scores.get('segments', [])) else 0.0,
                    "prosody": prosody_features[i] if i < len(prosody_features) else None,
                    "has_overlap": seg.get('has_overlap', False),
                    "overlap_duration": seg.get('overlap_duration', 0.0)
                }
                for i, seg in enumerate(segments)
            ]
        }

    def _generate_prosody_markers(self, prosody: Dict[str, Any]) -> str:
        """Generate inline prosody markers for a segment"""

        markers = []

        # Tempo markers
        tempo_dev = prosody.get('tempo_deviation_pct', 0.0)
        if tempo_dev is not None:
            if tempo_dev < -self.tempo_threshold:
                markers.append("`[TEMPO↓]`")
            elif tempo_dev > self.tempo_threshold:
                markers.append("`[TEMPO↑]`")

        # Pitch markers
        pitch_dev = prosody.get('pitch_deviation_pct', 0.0)
        if pitch_dev is not None:
            if pitch_dev < -self.pitch_threshold:
                markers.append("`[PITCH↓]`")
            elif pitch_dev > self.pitch_threshold:
                markers.append("`[PITCH↑]`")

        # Energy markers
        energy_dev = prosody.get('energy_deviation_pct', 0.0)
        if energy_dev is not None:
            if energy_dev < -self.energy_threshold:
                markers.append("`[ENERGY↓]`")
            elif energy_dev > self.energy_threshold:
                markers.append("`[ENERGY↑]`")

        # Pause marker
        pause_before = prosody.get('pause_before_ms', 0.0)
        if pause_before > self.pause_threshold:
            markers.append("`[PAUSE]`")

        return " ".join(markers)

    def _generate_prosody_details(self, prosody: Dict[str, Any]) -> str:
        """Generate detailed prosody information"""

        details = []

        tempo = prosody.get('tempo_wpm')
        if tempo:
            tempo_dev = prosody.get('tempo_deviation_pct', 0.0)
            details.append(f"Tempo: {tempo:.1f} WPM ({tempo_dev:+.1f}%)")

        pitch = prosody.get('pitch_mean_hz')
        if pitch:
            pitch_dev = prosody.get('pitch_deviation_pct', 0.0)
            details.append(f"Tonhöhe: {pitch:.1f} Hz ({pitch_dev:+.1f}%)")

        energy = prosody.get('energy_rms')
        if energy:
            energy_dev = prosody.get('energy_deviation_pct', 0.0)
            details.append(f"Energie: {energy:.4f} ({energy_dev:+.1f}%)")

        return " | ".join(details)

    def _format_timestamp(self, start: float, end: float) -> str:
        """Format timestamp as MM:SS - MM:SS"""

        def seconds_to_mmss(seconds: float) -> str:
            mins = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{mins:02d}:{secs:02d}"

        return f"{seconds_to_mmss(start)} - {seconds_to_mmss(end)}"


# Standalone test
if __name__ == "__main__":
    # Example usage
    formatter = OutputFormatter()

    # Mock transcription result
    result = {
        'text': 'Dies ist ein Test.',
        'segments': [
            {'start': 0.0, 'end': 3.5, 'text': 'Dies ist ein Test'},
            {'start': 4.0, 'end': 7.2, 'text': 'mit Prosodiemerkmalen'}
        ],
        'prosody_features': [
            {
                'start_time': 0.0,
                'end_time': 3.5,
                'tempo_wpm': 120.0,
                'tempo_deviation_pct': -25.0,
                'pitch_mean_hz': 150.0,
                'pitch_deviation_pct': 10.0,
                'energy_rms': 0.05,
                'energy_deviation_pct': -30.0,
                'pause_before_ms': 0.0
            },
            {
                'start_time': 4.0,
                'end_time': 7.2,
                'tempo_wpm': 180.0,
                'tempo_deviation_pct': 25.0,
                'pitch_mean_hz': 200.0,
                'pitch_deviation_pct': 20.0,
                'energy_rms': 0.15,
                'energy_deviation_pct': 40.0,
                'pause_before_ms': 500.0
            }
        ],
        'prosody_baseline': {
            'tempo_wpm_mean': 150.0,
            'pitch_mean_hz': 175.0,
            'energy_rms_mean': 0.10
        },
        'confidence_scores': {
            'overall_confidence': 0.92,
            'segments': [
                {'confidence': 0.95},
                {'confidence': 0.89}
            ]
        }
    }

    output_path = Path('/tmp/test_transcript')
    files = formatter.format_transcript(result, 'test.m4a', output_path)

    print(f"✅ Created files:")
    print(f"  - Markdown: {files['markdown']}")
    print(f"  - JSON: {files['json']}")

    # Show markdown content
    print(f"\n--- Markdown Preview ---")
    with open(files['markdown'], 'r', encoding='utf-8') as f:
        print(f.read())
