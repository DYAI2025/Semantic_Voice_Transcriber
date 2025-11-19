#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML Formatter - Professional therapeutic transcript layout

Features:
- Color-coded speaker blocks
- Colored prosody markers
- Emotional turning points highlighted
- PDF export via WeasyPrint
- Responsive design
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import tempfile

try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    print("⚠️ WeasyPrint nicht installiert. PDF-Export deaktiviert.")


class HTMLFormatter:
    """
    Generates professional HTML reports with color-coded speakers,
    prosody markers, and emotional highlighting
    """

    # Speaker color palette (professional, accessible)
    SPEAKER_COLORS = [
        {"bg": "#E3F2FD", "border": "#1976D2", "name": "Blau"},      # Speaker A - Blue
        {"bg": "#F3E5F5", "border": "#7B1FA2", "name": "Lila"},      # Speaker B - Purple
        {"bg": "#E8F5E9", "border": "#388E3C", "name": "Grün"},      # Speaker C - Green
        {"bg": "#FFF3E0", "border": "#F57C00", "name": "Orange"},    # Speaker D - Orange
        {"bg": "#FCE4EC", "border": "#C2185B", "name": "Pink"},      # Speaker E - Pink
        {"bg": "#E0F2F1", "border": "#00796B", "name": "Türkis"},    # Speaker F - Teal
    ]

    # Prosody marker colors
    MARKER_COLORS = {
        "TEMPO↑": {"color": "#D32F2F", "bg": "#FFEBEE", "label": "Schnell"},
        "TEMPO↓": {"color": "#1976D2", "bg": "#E3F2FD", "label": "Langsam"},
        "PITCH↑": {"color": "#F57C00", "bg": "#FFF3E0", "label": "Hoch"},
        "PITCH↓": {"color": "#7B1FA2", "bg": "#F3E5F5", "label": "Tief"},
        "ENERGY↑": {"color": "#388E3C", "bg": "#E8F5E9", "label": "Laut"},
        "ENERGY↓": {"color": "#5D4037", "bg": "#EFEBE9", "label": "Leise"},
        "PAUSE": {"color": "#455A64", "bg": "#ECEFF1", "label": "Pause"},
        "ÜBERLAPPUNG": {"color": "#E91E63", "bg": "#FCE4EC", "label": "Überlappung"},
    }

    def __init__(self):
        self.speaker_assignments = {}  # Track which speaker gets which color

    def generate_html(
        self,
        transcription_result: Dict[str, Any],
        audio_filename: str,
        output_path: Path
    ) -> Path:
        """
        Generate professional HTML report

        Args:
            transcription_result: Result with segments, prosody, speaker_labels
            audio_filename: Original audio filename
            output_path: Base output path (without extension)

        Returns:
            Path to generated HTML file
        """
        # Extract data
        segments = transcription_result.get('segments', [])
        prosody_features = transcription_result.get('prosody_features', [])
        prosody_baseline = transcription_result.get('prosody_baseline', None)
        confidence_scores = transcription_result.get('confidence_scores', {})
        speaker_labels = transcription_result.get('speaker_labels', None)

        # Assign speaker colors
        if speaker_labels:
            unique_speakers = sorted(set(speaker_labels))
            for i, speaker in enumerate(unique_speakers):
                self.speaker_assignments[speaker] = self.SPEAKER_COLORS[i % len(self.SPEAKER_COLORS)]

        # Generate HTML
        html = self._generate_html_content(
            audio_filename,
            segments,
            prosody_features,
            prosody_baseline,
            confidence_scores,
            speaker_labels
        )

        # Write to file
        html_path = output_path.with_suffix('.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return html_path

    def generate_pdf(
        self,
        transcription_result: Dict[str, Any],
        audio_filename: str,
        output_path: Path
    ) -> Optional[Path]:
        """
        Generate professional PDF report from HTML

        Args:
            transcription_result: Result with segments, prosody, speaker_labels
            audio_filename: Original audio filename
            output_path: Base output path (without extension)

        Returns:
            Path to generated PDF file, or None if WeasyPrint not available
        """
        if not WEASYPRINT_AVAILABLE:
            print("❌ WeasyPrint nicht verfügbar. PDF-Export übersprungen.")
            return None

        try:
            # First generate HTML
            html_path = self.generate_html(transcription_result, audio_filename, output_path)

            # Convert HTML to PDF
            pdf_path = output_path.with_suffix('.pdf')

            # Generate PDF with WeasyPrint
            HTML(filename=str(html_path)).write_pdf(
                str(pdf_path),
                stylesheets=[],  # CSS is embedded in HTML
                presentational_hints=True
            )

            print(f"✅ PDF erstellt: {pdf_path}")
            return pdf_path

        except Exception as e:
            print(f"❌ PDF-Erstellung fehlgeschlagen: {e}")
            return None

    def generate_both(
        self,
        transcription_result: Dict[str, Any],
        audio_filename: str,
        output_path: Path
    ) -> Dict[str, Optional[Path]]:
        """
        Generate both HTML and PDF

        Returns:
            Dict with 'html' and 'pdf' paths
        """
        html_path = self.generate_html(transcription_result, audio_filename, output_path)

        pdf_path = None
        if WEASYPRINT_AVAILABLE:
            try:
                pdf_path = output_path.with_suffix('.pdf')
                HTML(filename=str(html_path)).write_pdf(str(pdf_path))
            except Exception as e:
                print(f"⚠️ PDF-Erstellung fehlgeschlagen: {e}")

        return {
            'html': html_path,
            'pdf': pdf_path
        }

    def _generate_html_content(
        self,
        audio_filename: str,
        segments: List[Dict],
        prosody_features: List[Dict],
        prosody_baseline: Optional[Dict],
        confidence_scores: Dict,
        speaker_labels: Optional[List[str]]
    ) -> str:
        """Generate complete HTML document"""

        html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transkript: {audio_filename}</title>
    {self._get_css_styles()}
</head>
<body>
    <div class="container">
        {self._generate_header(audio_filename, confidence_scores, prosody_baseline)}
        {self._generate_legend(speaker_labels)}
        {self._generate_transcript(segments, prosody_features, speaker_labels)}
        {self._generate_footer()}
    </div>
</body>
</html>"""

        return html

    def _get_css_styles(self) -> str:
        """Generate CSS styles"""
        return """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #212121;
            background: #FAFAFA;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        /* Header */
        .header {
            border-bottom: 3px solid #1976D2;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }

        .header h1 {
            color: #1976D2;
            font-size: 28px;
            margin-bottom: 10px;
        }

        .header .meta {
            color: #757575;
            font-size: 14px;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }

        .stat-card {
            background: #F5F5F5;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #1976D2;
        }

        .stat-card .label {
            color: #757575;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .stat-card .value {
            color: #212121;
            font-size: 20px;
            font-weight: bold;
            margin-top: 5px;
        }

        /* Legend */
        .legend {
            background: #F5F5F5;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 30px;
        }

        .legend h2 {
            font-size: 16px;
            margin-bottom: 15px;
            color: #424242;
        }

        .legend-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
        }

        .legend-color {
            width: 24px;
            height: 24px;
            border-radius: 4px;
            border: 2px solid;
        }

        /* Transcript */
        .transcript {
            margin-top: 30px;
        }

        .segment {
            margin-bottom: 20px;
            padding: 20px;
            border-radius: 6px;
            border-left: 5px solid;
            transition: transform 0.2s;
        }

        .segment:hover {
            transform: translateX(5px);
        }

        .segment-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            font-size: 13px;
            color: #757575;
        }

        .segment-speaker {
            font-weight: bold;
            font-size: 14px;
        }

        .segment-time {
            font-family: "Courier New", monospace;
        }

        .segment-text {
            font-size: 16px;
            line-height: 1.8;
            color: #212121;
            margin-bottom: 10px;
        }

        .segment-prosody {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 12px;
        }

        /* Prosody Markers */
        .marker {
            display: inline-flex;
            align-items: center;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            border: 1px solid;
            gap: 4px;
        }

        .marker-icon {
            font-size: 14px;
        }

        /* Prosody Details */
        .prosody-details {
            font-size: 12px;
            color: #616161;
            font-style: italic;
            margin-top: 8px;
            padding: 8px;
            background: rgba(0,0,0,0.02);
            border-radius: 4px;
        }

        /* Emotional Turning Points */
        .turning-point {
            border: 3px solid #FF6F00;
            box-shadow: 0 4px 12px rgba(255, 111, 0, 0.2);
            position: relative;
        }

        .turning-point::before {
            content: "⚠️ Emotionaler Wendepunkt";
            position: absolute;
            top: -12px;
            left: 20px;
            background: #FF6F00;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 0.5px;
        }

        /* Overlapped Speech */
        .overlap-segment {
            border-left: 4px solid #E91E63 !important;
            background: linear-gradient(90deg,
                rgba(233, 30, 99, 0.05) 0%,
                rgba(233, 30, 99, 0.02) 100%);
        }

        .overlap-badge {
            display: inline-block;
            background: #E91E63;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-left: 8px;
        }

        /* Footer */
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #E0E0E0;
            text-align: center;
            color: #9E9E9E;
            font-size: 12px;
        }

        /* Print styles */
        @media print {
            body {
                background: white;
                padding: 0;
            }

            .container {
                box-shadow: none;
            }

            .segment {
                page-break-inside: avoid;
            }
        }
    </style>
"""

    def _generate_header(
        self,
        audio_filename: str,
        confidence_scores: Dict,
        prosody_baseline: Optional[Dict]
    ) -> str:
        """Generate header section"""

        overall_conf = confidence_scores.get('overall_confidence', 0.0)
        total_segments = confidence_scores.get('total_segments', 0)

        baseline_html = ""
        if prosody_baseline:
            baseline_html = f"""
            <div class="stat-card">
                <div class="label">Tempo Baseline</div>
                <div class="value">{prosody_baseline.get('tempo_wpm_mean', 0):.1f} WPM</div>
            </div>
            <div class="stat-card">
                <div class="label">Tonhöhe Baseline</div>
                <div class="value">{prosody_baseline.get('pitch_mean_hz', 0):.1f} Hz</div>
            </div>
            <div class="stat-card">
                <div class="label">Energie Baseline</div>
                <div class="value">{prosody_baseline.get('energy_rms_mean', 0):.4f}</div>
            </div>
"""

        return f"""
        <div class="header">
            <h1>📄 Therapeutisches Transkript</h1>
            <div class="meta">
                <strong>Datei:</strong> {audio_filename}<br>
                <strong>Erstellt:</strong> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
            </div>

            <div class="stats">
                <div class="stat-card">
                    <div class="label">Gesamt-Konfidenz</div>
                    <div class="value">{overall_conf:.1%}</div>
                </div>
                <div class="stat-card">
                    <div class="label">Segmente</div>
                    <div class="value">{total_segments}</div>
                </div>
                {baseline_html}
            </div>
        </div>
"""

    def _generate_legend(self, speaker_labels: Optional[List[str]]) -> str:
        """Generate legend section"""

        # Speaker legend
        speaker_legend = ""
        if speaker_labels and self.speaker_assignments:
            speaker_items = []
            for speaker, colors in self.speaker_assignments.items():
                speaker_items.append(f"""
                <div class="legend-item">
                    <div class="legend-color" style="background: {colors['bg']}; border-color: {colors['border']};"></div>
                    <span>{speaker}</span>
                </div>
                """)
            speaker_legend = "".join(speaker_items)

        # Marker legend
        marker_items = []
        for marker, colors in self.MARKER_COLORS.items():
            marker_items.append(f"""
            <div class="legend-item">
                <div class="marker" style="color: {colors['color']}; background: {colors['bg']}; border-color: {colors['color']};">
                    {marker}
                </div>
                <span>{colors['label']}</span>
            </div>
            """)
        marker_legend = "".join(marker_items)

        return f"""
        <div class="legend">
            <h2>🎨 Legende</h2>
            <div class="legend-grid">
                {speaker_legend}
            </div>
            <h2 style="margin-top: 20px;">🎵 Prosody-Marker</h2>
            <div class="legend-grid">
                {marker_legend}
            </div>
        </div>
"""

    def _generate_transcript(
        self,
        segments: List[Dict],
        prosody_features: List[Dict],
        speaker_labels: Optional[List[str]]
    ) -> str:
        """Generate transcript section"""

        segments_html = []

        for i, segment in enumerate(segments):
            start = segment.get('start', 0.0)
            end = segment.get('end', 0.0)
            text = segment.get('text', '').strip()
            has_overlap = segment.get('has_overlap', False)
            overlap_duration = segment.get('overlap_duration', 0.0)

            # Get speaker
            speaker = "Sprecher"
            speaker_color = {"bg": "#F5F5F5", "border": "#9E9E9E"}
            if speaker_labels and i < len(speaker_labels):
                speaker = speaker_labels[i]
                speaker_color = self.speaker_assignments.get(speaker, speaker_color)

            # Get prosody
            prosody = None
            if i < len(prosody_features):
                prosody = prosody_features[i]

            # Check if emotional turning point
            is_turning_point = self._is_emotional_turning_point(prosody)
            turning_point_class = " turning-point" if is_turning_point else ""

            # Check for overlap
            overlap_class = " overlap-segment" if has_overlap else ""

            # Format timestamp
            timestamp = self._format_timestamp(start, end)

            # Generate overlap badge
            overlap_badge = ""
            if has_overlap:
                overlap_badge = f'<span class="overlap-badge">⚠ Überlappung {overlap_duration:.1f}s</span>'

            # Generate prosody markers
            markers_html = ""
            prosody_details = ""
            if prosody:
                markers_html = self._generate_prosody_markers(prosody)
                prosody_details = self._generate_prosody_details(prosody)

            segment_html = f"""
            <div class="segment{turning_point_class}{overlap_class}" style="background: {speaker_color['bg']}; border-left-color: {speaker_color['border']};">
                <div class="segment-header">
                    <span class="segment-speaker" style="color: {speaker_color['border']};">{speaker}</span>
                    <span class="segment-time">{timestamp}</span>
                    {overlap_badge}
                </div>
                <div class="segment-text">{text}</div>
                {markers_html}
                {prosody_details}
            </div>
            """
            segments_html.append(segment_html)

        return f"""
        <div class="transcript">
            <h2 style="margin-bottom: 20px; color: #424242;">📝 Transkript</h2>
            {"".join(segments_html)}
        </div>
"""

    def _generate_prosody_markers(self, prosody: Dict) -> str:
        """Generate prosody marker badges"""

        markers = []
        tempo_dev = prosody.get('tempo_deviation_pct', 0.0)
        pitch_dev = prosody.get('pitch_deviation_pct', 0.0)
        energy_dev = prosody.get('energy_deviation_pct', 0.0)
        pause_before = prosody.get('pause_before_ms', 0.0)

        # Tempo markers
        if tempo_dev is not None:
            if tempo_dev < -20:
                markers.append(self._create_marker("TEMPO↓", tempo_dev))
            elif tempo_dev > 20:
                markers.append(self._create_marker("TEMPO↑", tempo_dev))

        # Pitch markers
        if pitch_dev is not None:
            if pitch_dev < -15:
                markers.append(self._create_marker("PITCH↓", pitch_dev))
            elif pitch_dev > 15:
                markers.append(self._create_marker("PITCH↑", pitch_dev))

        # Energy markers
        if energy_dev is not None:
            if energy_dev < -25:
                markers.append(self._create_marker("ENERGY↓", energy_dev))
            elif energy_dev > 25:
                markers.append(self._create_marker("ENERGY↑", energy_dev))

        # Pause marker
        if pause_before > 1000:
            markers.append(self._create_marker("PAUSE", pause_before, is_pause=True))

        if markers:
            return f'<div class="segment-prosody">{"".join(markers)}</div>'
        return ""

    def _create_marker(self, marker_type: str, value: float, is_pause: bool = False) -> str:
        """Create colored marker badge"""

        colors = self.MARKER_COLORS.get(marker_type, {"color": "#000", "bg": "#FFF"})

        if is_pause:
            value_text = f"{value:.0f}ms"
        else:
            value_text = f"{value:+.1f}%"

        return f"""
        <span class="marker" style="color: {colors['color']}; background: {colors['bg']}; border-color: {colors['color']};">
            <span class="marker-icon">{marker_type}</span>
            <span>{value_text}</span>
        </span>
        """

    def _generate_prosody_details(self, prosody: Dict) -> str:
        """Generate detailed prosody information"""

        details = []

        tempo = prosody.get('tempo_wpm')
        if tempo:
            details.append(f"Tempo: {tempo:.1f} WPM")

        pitch = prosody.get('pitch_mean_hz')
        if pitch:
            details.append(f"Tonhöhe: {pitch:.1f} Hz")

        energy = prosody.get('energy_rms')
        if energy:
            details.append(f"Energie: {energy:.4f}")

        if details:
            return f'<div class="prosody-details">{" | ".join(details)}</div>'
        return ""

    def _is_emotional_turning_point(self, prosody: Optional[Dict]) -> bool:
        """
        Detect emotional turning points based on prosody

        Criteria: Strong deviation in multiple dimensions
        """
        if not prosody:
            return False

        # Count strong deviations
        strong_deviations = 0

        tempo_dev = prosody.get('tempo_deviation_pct', 0.0)
        if tempo_dev and abs(tempo_dev) > 30:
            strong_deviations += 1

        pitch_dev = prosody.get('pitch_deviation_pct', 0.0)
        if pitch_dev and abs(pitch_dev) > 25:
            strong_deviations += 1

        energy_dev = prosody.get('energy_deviation_pct', 0.0)
        if energy_dev and abs(energy_dev) > 40:
            strong_deviations += 1

        # Turning point if 2+ strong deviations
        return strong_deviations >= 2

    def _format_timestamp(self, start: float, end: float) -> str:
        """Format timestamp as MM:SS - MM:SS"""

        def seconds_to_mmss(seconds: float) -> str:
            mins = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{mins:02d}:{secs:02d}"

        return f"{seconds_to_mmss(start)} - {seconds_to_mmss(end)}"

    def _generate_footer(self) -> str:
        """Generate footer"""

        return """
        <div class="footer">
            <p>Generiert mit <strong>Semantic Voice Transcriber (SVT)</strong></p>
            <p>Prosodieanalyse • Emotionale Marker • DYAI Framework</p>
        </div>
"""


def create_correlation_badge(marker_name: str, confidence: float) -> str:
    """Create HTML badge showing correlation confidence."""
    # Color based on confidence level
    if confidence >= 0.8:
        color = "#28a745"  # Green - high confidence
    elif confidence >= 0.6:
        color = "#ffc107"  # Yellow - medium confidence
    else:
        color = "#dc3545"  # Red - low confidence

    return f'''
    <span style="
        background-color: {color};
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.85em;
        margin: 0 2px;
    ">
        {marker_name} {confidence:.0%}
    </span>
    '''


# Standalone test
if __name__ == "__main__":
    # Create mock data
    mock_result = {
        'segments': [
            {'start': 5.26, 'end': 7.38, 'text': 'So, wir haben ja nicht so viel Zeit.'},
            {'start': 7.84, 'end': 8.72, 'text': 'Wolli, wir müssen sprechen.'},
            {'start': 19.36, 'end': 21.0, 'text': 'Wolli, we need to talk.'},
        ],
        'prosody_features': [
            {
                'start_time': 5.26,
                'end_time': 7.38,
                'tempo_wpm': 226.4,
                'tempo_deviation_pct': 20.6,
                'pitch_mean_hz': 226.0,
                'pitch_deviation_pct': 13.2,
                'energy_rms': 0.0836,
                'energy_deviation_pct': 5.5,
                'pause_before_ms': 0.0
            },
            {
                'start_time': 7.84,
                'end_time': 8.72,
                'tempo_wpm': 272.7,
                'tempo_deviation_pct': 45.3,
                'pitch_mean_hz': 211.2,
                'pitch_deviation_pct': 5.8,
                'energy_rms': 0.0763,
                'energy_deviation_pct': -3.7,
                'pause_before_ms': 460.0
            },
            {
                'start_time': 19.36,
                'end_time': 21.0,
                'tempo_wpm': 182.9,
                'tempo_deviation_pct': -2.5,
                'pitch_mean_hz': 168.7,
                'pitch_deviation_pct': -15.5,
                'energy_rms': 0.0497,
                'energy_deviation_pct': -37.3,
                'pause_before_ms': 10640.0
            }
        ],
        'prosody_baseline': {
            'tempo_wpm_mean': 187.7,
            'pitch_mean_hz': 199.7,
            'energy_rms_mean': 0.0792
        },
        'confidence_scores': {
            'overall_confidence': 0.529,
            'total_segments': 3
        },
        'speaker_labels': ['Therapeut', 'Therapeut', 'Patient']
    }

    formatter = HTMLFormatter()
    output_path = Path(tempfile.gettempdir()) / 'test_transcript'

    # Generate both HTML and PDF
    files = formatter.generate_both(mock_result, 'test.m4a', output_path)

    print(f"\n✅ Files generated:")
    print(f"  📄 HTML: {files['html']}")
    if files['pdf']:
        print(f"  📕 PDF: {files['pdf']}")
    print(f"\n🌐 Open in browser: file://{files['html']}")
