"""
Enhanced Speaker Visualization V2

Professional formatting for speaker-separated transcripts:
- Markdown output with icons, dividers, blockquotes
- HTML output with colors, proper styling
- Clear speaker distinction with visual hierarchy
- Confidence indicators for low-confidence segments
- Turning point highlighting
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SpeakerVisualizerV2:
    """Professional speaker visualization for transcripts"""

    # Speaker icons
    SPEAKER_ICONS = {
        0: "👤", 1: "👨", 2: "👩", 3: "🧑", 4: "👴",
        5: "👵", 6: "🧔", 7: "👨‍⚕️", 8: "👩‍⚕️", 9: "🧑‍💼"
    }

    # Confidence level emojis
    CONFIDENCE_INDICATORS = {
        'very_high': '✓',
        'high': '✓',
        'medium': '~',
        'low': '?',
        'very_low': '⚠'
    }

    def __init__(self):
        """Initialize visualizer"""
        logger.info("Speaker Visualizer V2 initialized")

    def format_markdown(
        self,
        segments: List[Dict],
        speakers: Dict[str, Dict],
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Format transcript as professional Markdown

        Args:
            segments: List of segment dicts with speaker, text, timestamps, confidence
            speakers: Dict mapping speaker_id to speaker info (name, color, icon_index)
            metadata: Optional metadata (audio_file, date, duration, quality_score)

        Returns:
            Formatted Markdown string
        """
        output = []

        # Header
        output.append("# Transcription Report")
        output.append("")

        # Metadata section
        if metadata:
            output.append("## Session Information")
            output.append("")

            if 'audio_file' in metadata:
                output.append(f"**Audio File:** `{metadata['audio_file']}`")

            if 'date' in metadata:
                output.append(f"**Date:** {metadata['date']}")

            if 'duration' in metadata:
                duration = metadata['duration']
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                output.append(f"**Duration:** {minutes}m {seconds}s")

            if 'model' in metadata:
                output.append(f"**Model:** {metadata['model']}")

            if 'quality_score' in metadata:
                quality = metadata['quality_score']
                quality_pct = f"{quality*100:.1f}%"
                output.append(f"**Quality Score:** {quality_pct}")

            if 'speakers' in metadata:
                speaker_count = len(metadata['speakers'])
                output.append(f"**Speakers:** {speaker_count}")

            output.append("")

        # Speaker legend
        if speakers:
            output.append("## Speakers")
            output.append("")

            for speaker_id, speaker_info in speakers.items():
                name = speaker_info.get('name', f'Speaker {speaker_id}')
                icon_index = speaker_info.get('icon_index', 0)
                icon = self.SPEAKER_ICONS.get(icon_index, '👤')
                color = speaker_info.get('color', '#4A90E2')

                output.append(f"- {icon} **{name}** ({speaker_id}) `{color}`")

            output.append("")

        # Transcript
        output.append("## Transcript")
        output.append("")

        last_speaker = None

        for seg in segments:
            speaker_id = seg.get('speaker', 'UNKNOWN')
            speaker_info = speakers.get(speaker_id, {})

            # Speaker change - add divider and header
            if speaker_id != last_speaker:
                if last_speaker is not None:
                    output.append("")
                    output.append("---")
                    output.append("")

                # Speaker name with icon
                name = speaker_info.get('name', f'Speaker {speaker_id}')
                icon_index = speaker_info.get('icon_index', 0)
                icon = self.SPEAKER_ICONS.get(icon_index, '👤')

                output.append(f"### {icon} {name}")
                output.append("")

                last_speaker = speaker_id

            # Timestamp
            start_time = seg.get('start', 0)
            end_time = seg.get('end', 0)
            timestamp_str = f"**`[{self._format_timestamp(start_time)} - {self._format_timestamp(end_time)}]`**"

            # Confidence indicator
            confidence = seg.get('confidence', 1.0)
            confidence_level = seg.get('confidence_level', 'high')
            indicator = self.CONFIDENCE_INDICATORS.get(confidence_level, '~')

            if confidence < 0.7:
                timestamp_str += f" {indicator} *({confidence:.2f})*"

            output.append(timestamp_str)
            output.append("")

            # Text as blockquote
            text = seg.get('text', '').strip()

            # Mark low confidence inline
            if confidence < 0.5:
                text = f"*[UNSICHER: {confidence:.2f}]* {text}"

            output.append(f"> {text}")
            output.append("")

            # Turning point annotation
            if seg.get('is_turning_point', False):
                tp_data = seg.get('turning_point_data', {})
                output.append(self._format_turning_point_md(tp_data))
                output.append("")

        return "\n".join(output)

    def format_html(
        self,
        segments: List[Dict],
        speakers: Dict[str, Dict],
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Format transcript as styled HTML

        Args:
            segments: List of segment dicts
            speakers: Dict mapping speaker_id to speaker info
            metadata: Optional metadata

        Returns:
            HTML string with inline CSS
        """
        output = []

        # HTML header with CSS
        output.append('<!DOCTYPE html>')
        output.append('<html lang="de">')
        output.append('<head>')
        output.append('    <meta charset="UTF-8">')
        output.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        output.append('    <title>Transcription Report</title>')
        output.append(self._get_css())
        output.append('</head>')
        output.append('<body>')

        # Main container
        output.append('<div class="container">')

        # Header
        output.append('    <h1 class="title">Transcription Report</h1>')

        # Metadata
        if metadata:
            output.append('    <div class="metadata">')
            output.append('        <h2>Session Information</h2>')
            output.append('        <table>')

            if 'audio_file' in metadata:
                output.append(f'            <tr><td><strong>Audio File:</strong></td><td><code>{metadata["audio_file"]}</code></td></tr>')

            if 'date' in metadata:
                output.append(f'            <tr><td><strong>Date:</strong></td><td>{metadata["date"]}</td></tr>')

            if 'duration' in metadata:
                duration = metadata['duration']
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                output.append(f'            <tr><td><strong>Duration:</strong></td><td>{minutes}m {seconds}s</td></tr>')

            if 'model' in metadata:
                output.append(f'            <tr><td><strong>Model:</strong></td><td>{metadata["model"]}</td></tr>')

            if 'quality_score' in metadata:
                quality = metadata['quality_score']
                quality_pct = f"{quality*100:.1f}%"
                output.append(f'            <tr><td><strong>Quality:</strong></td><td>{quality_pct}</td></tr>')

            output.append('        </table>')
            output.append('    </div>')

        # Speaker legend
        if speakers:
            output.append('    <div class="speakers">')
            output.append('        <h2>Speakers</h2>')
            output.append('        <ul>')

            for speaker_id, speaker_info in speakers.items():
                name = speaker_info.get('name', f'Speaker {speaker_id}')
                icon_index = speaker_info.get('icon_index', 0)
                icon = self.SPEAKER_ICONS.get(icon_index, '👤')
                color = speaker_info.get('color', '#4A90E2')

                output.append(f'            <li><span class="speaker-icon">{icon}</span> <strong>{name}</strong> <span class="color-badge" style="background-color: {color};"></span></li>')

            output.append('        </ul>')
            output.append('    </div>')

        # Transcript
        output.append('    <div class="transcript">')
        output.append('        <h2>Transcript</h2>')

        last_speaker = None

        for seg in segments:
            speaker_id = seg.get('speaker', 'UNKNOWN')
            speaker_info = speakers.get(speaker_id, {})

            # Speaker change
            if speaker_id != last_speaker:
                if last_speaker is not None:
                    output.append('            </div>')  # Close previous speaker block
                    output.append('            <hr class="speaker-divider">')

                # New speaker block
                name = speaker_info.get('name', f'Speaker {speaker_id}')
                icon_index = speaker_info.get('icon_index', 0)
                icon = self.SPEAKER_ICONS.get(icon_index, '👤')
                color = speaker_info.get('color', '#4A90E2')

                output.append(f'            <div class="speaker-block" style="border-left-color: {color};">')
                output.append(f'                <h3 class="speaker-name" style="color: {color};">{icon} {name}</h3>')

                last_speaker = speaker_id

            # Segment
            start_time = seg.get('start', 0)
            end_time = seg.get('end', 0)
            confidence = seg.get('confidence', 1.0)
            confidence_level = seg.get('confidence_level', 'high')
            text = seg.get('text', '').strip()

            timestamp_str = f"{self._format_timestamp(start_time)} - {self._format_timestamp(end_time)}"

            # Confidence class
            conf_class = 'high-confidence' if confidence >= 0.7 else 'low-confidence'

            output.append(f'                <div class="segment {conf_class}">')
            output.append(f'                    <div class="timestamp">[{timestamp_str}]')

            # Confidence indicator
            indicator = self.CONFIDENCE_INDICATORS.get(confidence_level, '~')
            if confidence < 0.7:
                output.append(f' <span class="confidence-indicator">{indicator} ({confidence:.2f})</span>')

            output.append('                    </div>')

            # Text
            if confidence < 0.5:
                text = f'<span class="unsure">[UNSICHER: {confidence:.2f}]</span> {text}'

            output.append(f'                    <div class="text">{text}</div>')

            # Turning point
            if seg.get('is_turning_point', False):
                tp_data = seg.get('turning_point_data', {})
                output.append(self._format_turning_point_html(tp_data))

            output.append('                </div>')  # Close segment

        # Close last speaker block
        if last_speaker is not None:
            output.append('            </div>')  # Close speaker block

        output.append('    </div>')  # Close transcript
        output.append('</div>')  # Close container
        output.append('</body>')
        output.append('</html>')

        return "\n".join(output)

    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds as MM:SS or HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    def _format_turning_point_md(self, tp_data: Dict) -> str:
        """Format turning point for Markdown"""
        lines = []
        lines.append("🔄 **TURNING POINT DETECTED**")
        lines.append("")

        if 'cosd_score' in tp_data:
            lines.append(f"- CoSD Score: `{tp_data['cosd_score']:.3f}`")

        if 'pitch_change' in tp_data:
            lines.append(f"- Pitch Change: `{tp_data['pitch_change']:+.1f}%`")

        if 'tempo_change' in tp_data:
            lines.append(f"- Tempo Change: `{tp_data['tempo_change']:+.1f}%`")

        if 'energy_change' in tp_data:
            lines.append(f"- Energy Change: `{tp_data['energy_change']:+.1f}%`")

        if 'semantic_markers' in tp_data and tp_data['semantic_markers']:
            markers = ', '.join(f"`{m}`" for m in tp_data['semantic_markers'])
            lines.append(f"- Semantic Markers: {markers}")

        if 'reason' in tp_data:
            lines.append("")
            lines.append(f"*{tp_data['reason']}*")

        return "\n".join(lines)

    def _format_turning_point_html(self, tp_data: Dict) -> str:
        """Format turning point for HTML"""
        lines = []
        lines.append('                    <div class="turning-point">')
        lines.append('                        <div class="tp-title">🔄 TURNING POINT DETECTED</div>')
        lines.append('                        <ul class="tp-evidence">')

        if 'cosd_score' in tp_data:
            lines.append(f'                            <li>CoSD Score: <code>{tp_data["cosd_score"]:.3f}</code></li>')

        if 'pitch_change' in tp_data:
            lines.append(f'                            <li>Pitch Change: <code>{tp_data["pitch_change"]:+.1f}%</code></li>')

        if 'tempo_change' in tp_data:
            lines.append(f'                            <li>Tempo Change: <code>{tp_data["tempo_change"]:+.1f}%</code></li>')

        if 'energy_change' in tp_data:
            lines.append(f'                            <li>Energy Change: <code>{tp_data["energy_change"]:+.1f}%</code></li>')

        if 'semantic_markers' in tp_data and tp_data['semantic_markers']:
            markers = ', '.join(f'<code>{m}</code>' for m in tp_data['semantic_markers'])
            lines.append(f'                            <li>Semantic Markers: {markers}</li>')

        lines.append('                        </ul>')

        if 'reason' in tp_data:
            lines.append(f'                        <div class="tp-reason">{tp_data["reason"]}</div>')

        lines.append('                    </div>')

        return "\n".join(lines)

    def _get_css(self) -> str:
        """Get CSS styles for HTML output"""
        return '''    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            padding: 20px;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .title {
            color: #2C3E50;
            margin-bottom: 30px;
            font-size: 2em;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }

        h2 {
            color: #34495E;
            margin: 30px 0 15px 0;
            font-size: 1.5em;
        }

        .metadata table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }

        .metadata td {
            padding: 8px;
            border-bottom: 1px solid #ecf0f1;
        }

        .metadata td:first-child {
            width: 150px;
            text-align: right;
            padding-right: 15px;
        }

        .speakers ul {
            list-style: none;
            margin: 15px 0;
        }

        .speakers li {
            padding: 10px;
            margin: 5px 0;
            background: #f8f9fa;
            border-radius: 4px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .speaker-icon {
            font-size: 1.3em;
        }

        .color-badge {
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 1px solid #ddd;
            margin-left: auto;
        }

        .transcript {
            margin-top: 30px;
        }

        .speaker-divider {
            margin: 30px 0;
            border: none;
            border-top: 2px solid #ecf0f1;
        }

        .speaker-block {
            margin: 20px 0;
            padding: 20px;
            border-left: 4px solid #3498db;
            background: #f8f9fa;
            border-radius: 4px;
        }

        .speaker-name {
            font-size: 1.3em;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .segment {
            margin: 15px 0;
            padding: 10px;
            background: white;
            border-radius: 4px;
        }

        .segment.low-confidence {
            background: #fff3e0;
            border-left: 3px solid #ff9800;
        }

        .timestamp {
            font-size: 0.85em;
            color: #7f8c8d;
            margin-bottom: 5px;
            font-family: 'Courier New', monospace;
        }

        .confidence-indicator {
            color: #e74c3c;
            font-weight: bold;
        }

        .text {
            padding: 5px 0;
            line-height: 1.6;
        }

        .unsure {
            color: #e74c3c;
            font-weight: bold;
            font-size: 0.9em;
        }

        .turning-point {
            margin-top: 15px;
            padding: 15px;
            background: #fff3e0;
            border: 2px solid #e74c3c;
            border-radius: 4px;
        }

        .tp-title {
            font-weight: bold;
            color: #e74c3c;
            margin-bottom: 10px;
            font-size: 1.1em;
        }

        .tp-evidence {
            list-style: none;
            padding-left: 20px;
            margin: 10px 0;
        }

        .tp-evidence li {
            margin: 5px 0;
        }

        .tp-evidence code {
            background: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }

        .tp-reason {
            margin-top: 10px;
            font-style: italic;
            color: #555;
        }

        code {
            background: #ecf0f1;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
    </style>'''


# Example usage
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    # Sample data
    speakers = {
        'SPEAKER_00': {
            'speaker_id': 'SPEAKER_00',
            'name': 'Dr. Schmidt',
            'color': '#4A90E2',
            'icon_index': 7
        },
        'SPEAKER_01': {
            'speaker_id': 'SPEAKER_01',
            'name': 'Patient A',
            'color': '#7B68EE',
            'icon_index': 3
        }
    }

    segments = [
        {
            'speaker': 'SPEAKER_00',
            'start': 0.0,
            'end': 5.2,
            'text': 'Guten Tag, wie geht es Ihnen heute?',
            'confidence': 0.95,
            'confidence_level': 'very_high'
        },
        {
            'speaker': 'SPEAKER_01',
            'start': 5.8,
            'end': 12.3,
            'text': 'Danke, mir geht es etwas besser als letzte Woche.',
            'confidence': 0.89,
            'confidence_level': 'high'
        },
        {
            'speaker': 'SPEAKER_00',
            'start': 13.0,
            'end': 18.5,
            'text': 'Das freut mich zu hören. Wenn ich fragen darf, was hat sich verändert?',
            'confidence': 0.92,
            'confidence_level': 'very_high',
            'is_turning_point': True,
            'turning_point_data': {
                'reason': 'Therapeutic inquiry opening - patient beginning to share personal progress',
                'cosd_score': 0.73,
                'pitch_change': 12.5,
                'tempo_change': -8.3,
                'energy_change': 15.2,
                'semantic_markers': ['wenn ich fragen darf', 'was hat sich verändert']
            }
        },
        {
            'speaker': 'SPEAKER_01',
            'start': 19.2,
            'end': 35.7,
            'text': 'Ich habe angefangen, die Atemübungen zu machen, die Sie mir empfohlen haben.',
            'confidence': 0.43,
            'confidence_level': 'low'
        }
    ]

    metadata = {
        'audio_file': 'session_2024_11_12.mp3',
        'date': '2024-11-12 14:30',
        'duration': 35.7,
        'model': 'large-v3',
        'quality_score': 0.87,
        'speakers': speakers.values()
    }

    # Test visualizer
    visualizer = SpeakerVisualizerV2()

    # Generate Markdown
    print("=" * 60)
    print("MARKDOWN OUTPUT")
    print("=" * 60)
    markdown = visualizer.format_markdown(segments, speakers, metadata)
    print(markdown)

    # Save Markdown
    with open('Output/test_transcript.md', 'w', encoding='utf-8') as f:
        f.write(markdown)
    print("\n✅ Markdown saved to: Output/test_transcript.md")

    # Generate HTML
    html = visualizer.format_html(segments, speakers, metadata)
    with open('Output/test_transcript.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("✅ HTML saved to: Output/test_transcript.html")
