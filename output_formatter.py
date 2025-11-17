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

try:
    from quality_validator import QualityValidator
    QUALITY_VALIDATOR_AVAILABLE = True
except ImportError:
    QUALITY_VALIDATOR_AVAILABLE = False


class SpeakerConfig:
    """
    Configuration for speaker labeling in transcripts

    Modes:
    - 'names': Use actual names (e.g., "Dr. Schmidt", "Patient Maria")
    - 'letters': Use letters (e.g., "Speaker A", "Speaker B")
    - 'anonymous': Use generic roles (e.g., "Therapeut", "Patient")
    - 'custom': Use custom mapping dict
    """

    MODE_NAMES = 'names'
    MODE_LETTERS = 'letters'
    MODE_ANONYMOUS = 'anonymous'
    MODE_CUSTOM = 'custom'

    def __init__(
        self,
        mode: str = MODE_ANONYMOUS,
        custom_mapping: Optional[Dict[str, str]] = None,
        default_labels: Optional[Dict[str, str]] = None
    ):
        """
        Initialize speaker configuration

        Args:
            mode: Labeling mode (names/letters/anonymous/custom)
            custom_mapping: Dict mapping speaker IDs to custom labels (for MODE_CUSTOM)
            default_labels: Dict with default role names (e.g., {'SPEAKER_00': 'Therapeut'})
        """
        self.mode = mode
        self.custom_mapping = custom_mapping or {}
        self.default_labels = default_labels or {}

        # Letter sequence for MODE_LETTERS
        self.letter_sequence = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self._speaker_to_letter = {}  # Cache for consistent letter assignment

    def get_speaker_label(self, speaker_id: Optional[str]) -> str:
        """
        Get formatted speaker label based on configuration

        Args:
            speaker_id: Speaker identifier (e.g., "SPEAKER_00", "Patient", None)

        Returns:
            Formatted label (e.g., "Therapeut", "Speaker A", "Unknown")
        """
        # Handle None/empty
        if not speaker_id:
            return "Unknown"

        # Check custom mapping first (highest priority)
        if self.mode == self.MODE_CUSTOM and speaker_id in self.custom_mapping:
            return self.custom_mapping[speaker_id]

        # Check default labels
        if speaker_id in self.default_labels:
            return self.default_labels[speaker_id]

        # Apply mode-specific formatting
        if self.mode == self.MODE_NAMES:
            # Use speaker_id directly (assumes it's already a name)
            return speaker_id

        elif self.mode == self.MODE_LETTERS:
            # Assign consistent letter to this speaker
            if speaker_id not in self._speaker_to_letter:
                index = len(self._speaker_to_letter)
                if index < len(self.letter_sequence):
                    self._speaker_to_letter[speaker_id] = self.letter_sequence[index]
                else:
                    # Fallback for >26 speakers
                    self._speaker_to_letter[speaker_id] = f"{index + 1}"

            letter = self._speaker_to_letter[speaker_id]
            return f"Speaker {letter}"

        elif self.mode == self.MODE_ANONYMOUS:
            # Generic role-based labels
            # Try to infer role from speaker_id patterns
            speaker_lower = speaker_id.lower()

            if 'patient' in speaker_lower or 'klient' in speaker_lower:
                return "Patient"
            elif 'therap' in speaker_lower or 'doctor' in speaker_lower or 'dr' in speaker_lower:
                return "Therapeut"
            elif 'speaker_00' in speaker_lower:
                return "Therapeut"  # Convention: first speaker is therapist
            elif 'speaker_01' in speaker_lower:
                return "Patient"
            else:
                # Unknown role - use letter as fallback
                if speaker_id not in self._speaker_to_letter:
                    index = len(self._speaker_to_letter)
                    if index < len(self.letter_sequence):
                        self._speaker_to_letter[speaker_id] = self.letter_sequence[index]
                    else:
                        self._speaker_to_letter[speaker_id] = f"{index + 1}"

                letter = self._speaker_to_letter[speaker_id]
                return f"Speaker {letter}"

        else:
            # Fallback: return speaker_id as-is
            return speaker_id


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
        pause_threshold: float = 1000.0,  # milliseconds
        speaker_config: Optional[SpeakerConfig] = None
    ):
        """
        Initialize output formatter

        Args:
            tempo_threshold: % deviation from baseline to mark tempo changes
            pitch_threshold: % deviation from baseline to mark pitch changes
            energy_threshold: % deviation from baseline to mark energy changes
            pause_threshold: Pause duration in ms to mark significant pauses
            speaker_config: Configuration for speaker labeling (defaults to anonymous mode)
        """
        self.tempo_threshold = tempo_threshold
        self.pitch_threshold = pitch_threshold
        self.energy_threshold = energy_threshold
        self.pause_threshold = pause_threshold
        self.speaker_config = speaker_config or SpeakerConfig()

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
        generate_csv: bool = True,
        generate_enhanced_html: bool = True,
        generate_quality_report: bool = True
    ) -> Dict[str, Optional[Path]]:
        """
        Generate ALL output formats: Markdown, JSON, HTML, PDF, Enhanced HTML, Quality Report

        Args:
            transcription_result: Result from transcribe_with_whisper
            audio_filename: Name of the audio file
            output_path: Base output path (without extension)
            include_prosody_markers: Whether to include prosody markers
            generate_html: Whether to generate standard HTML (legacy)
            generate_pdf: Whether to generate PDF
            generate_csv: Whether to generate CSV
            generate_enhanced_html: Whether to generate enhanced therapeutic HTML
            generate_quality_report: Whether to generate quality validation report

        Returns:
            Dict with paths: {'markdown': Path, 'json': Path, 'html': Path,
                             'html_enhanced': Path, 'pdf': Path, 'csv': Path, 'quality_report': Path}
        """
        # Generate Markdown + JSON
        files = self.format_transcript(
            transcription_result,
            audio_filename,
            output_path,
            include_prosody_markers
        )

        # Generate enhanced HTML (new therapeutic format)
        if generate_enhanced_html:
            html_enhanced_path = self.format_html_enhanced(
                transcription_result,
                audio_filename,
                output_path
            )
            files['html_enhanced'] = html_enhanced_path
        else:
            files['html_enhanced'] = None

        # Generate standard HTML + PDF if requested (legacy)
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

        # Generate quality report (automatic validation)
        if generate_quality_report and QUALITY_VALIDATOR_AVAILABLE:
            quality_report_path = self.generate_quality_report(
                transcription_result,
                output_path
            )
            files['quality_report'] = quality_report_path
        else:
            files['quality_report'] = None

        return files

    def generate_quality_report(
        self,
        transcription_result: Dict[str, Any],
        output_path: Path
    ) -> Path:
        """
        Generate quality validation report

        Args:
            transcription_result: Result from transcribe_with_whisper
            output_path: Base output path (without extension)

        Returns:
            Path to quality report JSON file
        """
        # Prepare data for validation
        segments = transcription_result.get('segments', [])
        prosody_features = transcription_result.get('prosody_features', [])
        confidence_scores = transcription_result.get('confidence_scores', {})

        # Build transcript JSON for validator
        transcript_json = {
            "meta": {
                "file": str(output_path.name),
                "duration_seconds": segments[-1].get('end', 0.0) if segments else 0.0,
                "model": transcription_result.get('model', 'unknown')
            },
            "segments": [
                {
                    "id": i,
                    "speaker": seg.get('speaker', None),
                    "text": seg.get('text', '').strip(),
                    "confidence": confidence_scores.get('segments', [])[i].get('confidence', 0.0)
                    if i < len(confidence_scores.get('segments', [])) else 0.0,
                    "ato_markers": seg.get('ato_markers', [])
                }
                for i, seg in enumerate(segments)
            ]
        }

        # Build prosody JSON
        prosody_json = None
        if prosody_features:
            prosody_json = {
                "segments": prosody_features
            }

        # Run validation
        validator = QualityValidator()
        issues = validator.validate_transcript(transcript_json, prosody_json)

        # Generate report
        quality_report_path = output_path.with_suffix('.quality_report.json')
        report = validator.generate_quality_report(issues, quality_report_path)

        # Also print to console for immediate feedback
        validator.print_quality_report(issues)

        return quality_report_path

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
        """Generate annotated Markdown transcript with therapeutic format"""

        lines = []

        # Header
        lines.append(f"# Transkription: {audio_filename}")
        lines.append(f"\n*Erstellt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        # Overall statistics
        overall_conf = confidence_scores.get('overall_confidence', 0.0)
        total_segments = len(segments)

        # Get speaker statistics
        speakers = set()
        for seg in segments:
            speaker_id = seg.get('speaker')
            if speaker_id:
                speakers.add(self.speaker_config.get_speaker_label(speaker_id))

        lines.append(f"## Übersicht\n")
        lines.append(f"- **Gesamt-Konfidenz:** {overall_conf:.1%}")
        lines.append(f"- **Segmente:** {total_segments}")
        if speakers:
            lines.append(f"- **Sprecher:** {', '.join(sorted(speakers))}")

        if prosody_baseline:
            lines.append(f"\n### Prosodische Baseline")
            lines.append(f"- **Tempo:** {prosody_baseline.get('tempo_wpm_mean', 0):.1f} WPM")
            lines.append(f"- **Tonhöhe:** {prosody_baseline.get('pitch_mean_hz', 0):.1f} Hz")
            lines.append(f"- **Energie:** {prosody_baseline.get('energy_rms_mean', 0):.4f}")

        lines.append(f"\n---\n")

        # Segments with new therapeutic format
        lines.append(f"## Transkript\n")

        for i, segment in enumerate(segments):
            # Get prosody for this segment
            prosody = None
            if i < len(prosody_features):
                prosody = prosody_features[i]

            # Get confidence for this segment
            confidence = 0.0
            if i < len(confidence_scores.get('segments', [])):
                confidence = confidence_scores.get('segments', [])[i].get('confidence', 0.0)

            # Format utterance with new therapeutic layout
            utterance = self._format_utterance_markdown(
                segment=segment,
                prosody=prosody,
                confidence=confidence,
                index=i,
                include_markers=include_prosody_markers
            )

            lines.append(utterance)

        # Footer with legend
        if include_prosody_markers:
            lines.append("\n---\n")
            lines.append("### Legende\n")
            lines.append("- **Prosody Marker**: ↑/↓ zeigen Abweichungen von der Baseline")
            lines.append("  - Tempo: ±20% | Tonhöhe: ±15% | Energie: ±25% | Pause: >1s")
            lines.append("- **Konfidenz**: Transkriptionsqualität (⚠️ wenn <70%)")
            lines.append("- **Überlappung**: Mehrere Sprecher gleichzeitig")

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

    def _format_utterance_markdown(
        self,
        segment: Dict[str, Any],
        prosody: Optional[Dict[str, Any]],
        confidence: float,
        index: int,
        include_markers: bool = True
    ) -> str:
        """
        Format single utterance with speaker header and metadata sidebar

        Returns therapeutic-friendly format:
        ### **Speaker** | 00:05-00:12

        Text content here.

        > **Metadaten:**
        > 📊 **Prosody**: Details
        > 🎭 **Emotion**: Details
        > 🔍 **Marker**: Details
        """
        start = segment.get('start', 0.0)
        end = segment.get('end', 0.0)
        text = segment.get('text', '').strip()
        speaker_id = segment.get('speaker', None)
        has_overlap = segment.get('has_overlap', False)

        # Get formatted speaker label
        speaker_label = self.speaker_config.get_speaker_label(speaker_id)

        # Format timestamp
        timestamp = self._format_timestamp(start, end)

        # Build utterance
        lines = []

        # Header: ### **Speaker** | 00:05-00:12
        lines.append(f"### **{speaker_label}** | {timestamp}\n")

        # Text content (clean, no inline markers)
        lines.append(text)

        # Metadata sidebar (if markers enabled)
        if include_markers:
            metadata = self._format_metadata_section(
                prosody=prosody,
                confidence=confidence,
                has_overlap=has_overlap,
                overlap_duration=segment.get('overlap_duration', 0.0),
                markers=segment.get('ato_markers', [])
            )

            if metadata:
                lines.append(f"\n{metadata}")

        lines.append("\n---\n")

        return "\n".join(lines)

    def _format_metadata_section(
        self,
        prosody: Optional[Dict[str, Any]],
        confidence: float,
        has_overlap: bool,
        overlap_duration: float,
        markers: List[str]
    ) -> str:
        """
        Format metadata sidebar with prosody, emotion, and markers

        Returns:
        > **Metadaten:**
        > 📊 **Prosody**: Energie ↑ (+49%), Tempo ↓ (-7.9%)
        > 🎭 **Confidence**: 89%
        > 🔍 **Marker**: ATO_QUESTION_OPEN, ATO_THEME_SLEEP
        """
        metadata_lines = []

        # Prosody section
        if prosody:
            prosody_items = []

            # Energy
            energy_dev = prosody.get('energy_deviation_pct', 0.0)
            if energy_dev is not None and abs(energy_dev) > self.energy_threshold:
                arrow = "↑" if energy_dev > 0 else "↓"
                prosody_items.append(f"Energie {arrow} ({energy_dev:+.1f}%)")

            # Tempo
            tempo_dev = prosody.get('tempo_deviation_pct', 0.0)
            if tempo_dev is not None and abs(tempo_dev) > self.tempo_threshold:
                arrow = "↑" if tempo_dev > 0 else "↓"
                prosody_items.append(f"Tempo {arrow} ({tempo_dev:+.1f}%)")

            # Pitch
            pitch_dev = prosody.get('pitch_deviation_pct', 0.0)
            if pitch_dev is not None and abs(pitch_dev) > self.pitch_threshold:
                arrow = "↑" if pitch_dev > 0 else "↓"
                prosody_items.append(f"Tonhöhe {arrow} ({pitch_dev:+.1f}%)")

            # Pause
            pause_before = prosody.get('pause_before_ms', 0.0)
            if pause_before > self.pause_threshold:
                prosody_items.append(f"Pause ({pause_before:.0f}ms)")

            if prosody_items:
                metadata_lines.append(f"> 📊 **Prosody**: {', '.join(prosody_items)}")

        # Overlap
        if has_overlap:
            metadata_lines.append(f"> 🗣️ **Überlappung**: {overlap_duration:.1f}s gleichzeitiges Sprechen")

        # Confidence (if low)
        if confidence < 0.7:
            metadata_lines.append(f"> ⚠️ **Konfidenz**: {confidence:.0%} (niedrig)")

        # ATO Markers
        if markers:
            marker_str = ", ".join(markers)
            metadata_lines.append(f"> 🔍 **Marker**: {marker_str}")

        if not metadata_lines:
            return ""

        # Add header
        result = ["> **Metadaten:**"] + metadata_lines
        return "\n".join(result)

    def format_html_enhanced(
        self,
        transcription_result: Dict[str, Any],
        audio_filename: str,
        output_path: Path
    ) -> Path:
        """
        Generate enhanced HTML with color-coded speakers and hover tooltips

        Features:
        - Green for Patient, Blue for Therapeut (or customizable colors)
        - Hover tooltips for prosody/marker details
        - Clean, therapeutic-friendly layout
        - Responsive design

        Args:
            transcription_result: Result from transcribe_with_whisper
            audio_filename: Name of the audio file
            output_path: Base output path (without extension)

        Returns:
            Path to generated HTML file
        """
        segments = transcription_result.get('segments', [])
        prosody_features = transcription_result.get('prosody_features', [])
        prosody_baseline = transcription_result.get('prosody_baseline', None)
        confidence_scores = transcription_result.get('confidence_scores', {})

        html_path = output_path.with_name(f"{output_path.stem}_enhanced.html")

        # Build HTML
        html_parts = []

        # HTML Header with CSS
        html_parts.append("""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transkription: {filename}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}

        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}

        h1 {{
            margin: 0 0 10px 0;
            color: #2c3e50;
        }}

        .metadata {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}

        .overview {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}

        .overview h2 {{
            margin-top: 0;
            color: #34495e;
            font-size: 1.2em;
        }}

        .utterance {{
            background: white;
            padding: 25px;
            margin: 20px 0;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.08);
            border-left: 5px solid #bdc3c7;
            transition: all 0.3s ease;
        }}

        .utterance:hover {{
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
            transform: translateX(5px);
        }}

        /* Speaker-specific colors */
        .utterance.patient {{
            border-left-color: #27ae60;
        }}

        .utterance.therapeut {{
            border-left-color: #3498db;
        }}

        .utterance.speaker-a {{
            border-left-color: #9b59b6;
        }}

        .utterance.speaker-b {{
            border-left-color: #e74c3c;
        }}

        .utterance-header {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #ecf0f1;
        }}

        .speaker-label {{
            font-weight: bold;
            font-size: 1.1em;
        }}

        .speaker-label.patient {{
            color: #27ae60;
        }}

        .speaker-label.therapeut {{
            color: #3498db;
        }}

        .speaker-label.speaker-a {{
            color: #9b59b6;
        }}

        .speaker-label.speaker-b {{
            color: #e74c3c;
        }}

        .timestamp {{
            color: #95a5a6;
            font-size: 0.9em;
            font-family: 'Courier New', monospace;
        }}

        .text-content {{
            font-size: 1.05em;
            margin: 15px 0;
            line-height: 1.8;
        }}

        .metadata-box {{
            background: #f8f9fa;
            border-left: 3px solid #3498db;
            padding: 12px 15px;
            margin-top: 15px;
            border-radius: 5px;
            font-size: 0.9em;
        }}

        .metadata-box .label {{
            font-weight: bold;
            margin-right: 8px;
        }}

        .metadata-row {{
            margin: 5px 0;
        }}

        .prosody-marker {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            margin-right: 5px;
        }}

        .prosody-up {{
            background: #ffe5e5;
            color: #c0392b;
        }}

        .prosody-down {{
            background: #e5f2ff;
            color: #2980b9;
        }}

        .ato-marker {{
            display: inline-block;
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            margin: 3px 3px 3px 0;
            font-family: 'Courier New', monospace;
        }}

        .legend {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-top: 30px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.08);
        }}

        .legend h3 {{
            margin-top: 0;
            color: #2c3e50;
        }}

        .legend ul {{
            list-style: none;
            padding-left: 0;
        }}

        .legend li {{
            padding: 5px 0;
        }}

        .color-badge {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 3px;
            vertical-align: middle;
            margin-right: 8px;
        }}

        .badge-patient {{ background: #27ae60; }}
        .badge-therapeut {{ background: #3498db; }}
        .badge-speaker-a {{ background: #9b59b6; }}
        .badge-speaker-b {{ background: #e74c3c; }}
    </style>
</head>
<body>
""".format(filename=audio_filename))

        # Header
        overall_conf = confidence_scores.get('overall_confidence', 0.0)
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        html_parts.append(f"""
    <div class="header">
        <h1>Transkription: {audio_filename}</h1>
        <div class="metadata">Erstellt: {created_at}</div>
    </div>
""")

        # Overview
        # Get unique speakers
        speakers = set()
        for seg in segments:
            speaker_id = seg.get('speaker')
            if speaker_id:
                speakers.add(self.speaker_config.get_speaker_label(speaker_id))

        html_parts.append(f"""
    <div class="overview">
        <h2>Übersicht</h2>
        <ul>
            <li><strong>Gesamt-Konfidenz:</strong> {overall_conf:.1%}</li>
            <li><strong>Segmente:</strong> {len(segments)}</li>""")

        if speakers:
            html_parts.append(f"""
            <li><strong>Sprecher:</strong> {', '.join(sorted(speakers))}</li>""")

        if prosody_baseline:
            html_parts.append(f"""
            <li><strong>Prosodische Baseline:</strong>
                Tempo: {prosody_baseline.get('tempo_wpm_mean', 0):.1f} WPM |
                Tonhöhe: {prosody_baseline.get('pitch_mean_hz', 0):.1f} Hz |
                Energie: {prosody_baseline.get('energy_rms_mean', 0):.4f}
            </li>""")

        html_parts.append("""
        </ul>
    </div>

    <div class="transcript">
""")

        # Utterances
        for i, segment in enumerate(segments):
            speaker_id = segment.get('speaker')
            speaker_label = self.speaker_config.get_speaker_label(speaker_id)
            speaker_class = speaker_label.lower().replace(' ', '-')

            start = segment.get('start', 0.0)
            end = segment.get('end', 0.0)
            text = segment.get('text', '').strip()

            timestamp = self._format_timestamp(start, end)

            # Get prosody
            prosody = None
            if i < len(prosody_features):
                prosody = prosody_features[i]

            # Get confidence
            confidence = 0.0
            if i < len(confidence_scores.get('segments', [])):
                confidence = confidence_scores.get('segments', [])[i].get('confidence', 0.0)

            # Build utterance HTML
            html_parts.append(f"""
        <div class="utterance {speaker_class}">
            <div class="utterance-header">
                <span class="speaker-label {speaker_class}">{speaker_label}</span>
                <span class="timestamp">{timestamp}</span>
            </div>
            <div class="text-content">{text}</div>
""")

            # Metadata box
            has_metadata = False
            metadata_html = []

            if prosody:
                prosody_items = self._get_prosody_html_items(prosody)
                if prosody_items:
                    has_metadata = True
                    metadata_html.append(f"""
                <div class="metadata-row">
                    <span class="label">📊 Prosody:</span> {' '.join(prosody_items)}
                </div>""")

            # Overlap
            if segment.get('has_overlap', False):
                has_metadata = True
                overlap_duration = segment.get('overlap_duration', 0.0)
                metadata_html.append(f"""
                <div class="metadata-row">
                    <span class="label">🗣️ Überlappung:</span> {overlap_duration:.1f}s gleichzeitiges Sprechen
                </div>""")

            # Low confidence warning
            if confidence < 0.7:
                has_metadata = True
                metadata_html.append(f"""
                <div class="metadata-row">
                    <span class="label">⚠️ Konfidenz:</span> {confidence:.0%} (niedrig)
                </div>""")

            # ATO Markers
            ato_markers = segment.get('ato_markers', [])
            if ato_markers:
                has_metadata = True
                markers_html = ''.join([f'<span class="ato-marker">{m}</span>' for m in ato_markers])
                metadata_html.append(f"""
                <div class="metadata-row">
                    <span class="label">🔍 Marker:</span><br>{markers_html}
                </div>""")

            if has_metadata:
                html_parts.append('            <div class="metadata-box">')
                html_parts.extend(metadata_html)
                html_parts.append('            </div>')

            html_parts.append('        </div>')

        # Close transcript div
        html_parts.append('    </div>')

        # Legend
        html_parts.append("""
    <div class="legend">
        <h3>Legende</h3>
        <ul>
            <li><span class="color-badge badge-patient"></span> <strong>Patient</strong></li>
            <li><span class="color-badge badge-therapeut"></span> <strong>Therapeut</strong></li>
            <li><strong>Prosody Marker:</strong> ↑/↓ zeigen Abweichungen von der Baseline (Tempo: ±20% | Tonhöhe: ±15% | Energie: ±25%)</li>
            <li><strong>Konfidenz:</strong> Transkriptionsqualität (⚠️ wenn <70%)</li>
            <li><strong>Überlappung:</strong> Mehrere Sprecher gleichzeitig</li>
        </ul>
    </div>
""")

        # Close HTML
        html_parts.append("""
</body>
</html>
""")

        # Write file
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(''.join(html_parts))

        return html_path

    def _get_prosody_html_items(self, prosody: Dict[str, Any]) -> List[str]:
        """Generate HTML prosody markers"""
        items = []

        # Energy
        energy_dev = prosody.get('energy_deviation_pct', 0.0)
        if energy_dev is not None and abs(energy_dev) > self.energy_threshold:
            arrow = "↑" if energy_dev > 0 else "↓"
            css_class = "prosody-up" if energy_dev > 0 else "prosody-down"
            items.append(f'<span class="prosody-marker {css_class}">Energie {arrow} ({energy_dev:+.1f}%)</span>')

        # Tempo
        tempo_dev = prosody.get('tempo_deviation_pct', 0.0)
        if tempo_dev is not None and abs(tempo_dev) > self.tempo_threshold:
            arrow = "↑" if tempo_dev > 0 else "↓"
            css_class = "prosody-up" if tempo_dev > 0 else "prosody-down"
            items.append(f'<span class="prosody-marker {css_class}">Tempo {arrow} ({tempo_dev:+.1f}%)</span>')

        # Pitch
        pitch_dev = prosody.get('pitch_deviation_pct', 0.0)
        if pitch_dev is not None and abs(pitch_dev) > self.pitch_threshold:
            arrow = "↑" if pitch_dev > 0 else "↓"
            css_class = "prosody-up" if pitch_dev > 0 else "prosody-down"
            items.append(f'<span class="prosody-marker {css_class}">Tonhöhe {arrow} ({pitch_dev:+.1f}%)</span>')

        # Pause
        pause_before = prosody.get('pause_before_ms', 0.0)
        if pause_before > self.pause_threshold:
            items.append(f'<span class="prosody-marker">Pause ({pause_before:.0f}ms)</span>')

        return items


def format_ato_markers(markers: List[str], confidence: Dict[str, float] = None) -> str:
    """Format ATO markers with optional confidence scores."""
    if not markers:
        return ""

    if confidence:
        formatted = []
        for marker in markers:
            conf = confidence.get(marker, 0)
            formatted.append(f"{marker} ({conf:.0%})")
        return " | ".join(formatted)
    else:
        return " | ".join(markers)


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
