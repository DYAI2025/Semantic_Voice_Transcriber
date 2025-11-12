"""
Professional PDF Generator for Therapeutic Transcriptions
Includes turning points visualization with scientific evidence
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, HRFlowable
)
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

class ProfessionalPDFGenerator:
    """Generate professional PDF reports for transcriptions"""

    def __init__(self, output_path: str):
        self.output_path = output_path
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        self.styles = self._create_styles()
        self.story = []

    def _create_styles(self) -> Dict:
        """Create paragraph styles"""
        styles = getSampleStyleSheet()

        custom_styles = {
            'Title': ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=24,
                textColor=colors.HexColor('#2C3E50'),
                spaceAfter=30,
                alignment=TA_CENTER
            ),
            'Heading1': ParagraphStyle(
                'CustomHeading1',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#34495E'),
                spaceAfter=12
            ),
            'Normal': ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=11,
                leading=16
            ),
            'SpeakerName': ParagraphStyle(
                'SpeakerName',
                fontSize=12,
                fontName='Helvetica-Bold',
                spaceAfter=6
            ),
            'TurningPoint': ParagraphStyle(
                'TurningPoint',
                fontSize=10,
                textColor=colors.HexColor('#E74C3C'),
                fontName='Helvetica-Bold',
                leftIndent=15
            )
        }

        return custom_styles

    def add_metadata_page(self, metadata: Dict):
        """Add metadata summary page"""
        # Title
        self.story.append(Paragraph(
            "THERAPEUTIC TRANSCRIPTION REPORT",
            self.styles['Title']
        ))
        self.story.append(Spacer(1, 1*cm))

        # Metadata table
        self.story.append(Paragraph("📋 METADATA", self.styles['Heading1']))
        self.story.append(Spacer(1, 0.3*cm))

        metadata_table = [
            ["Date:", metadata.get('date', datetime.now()).strftime("%d.%m.%Y %H:%M")],
            ["Duration:", self._format_duration(metadata.get('duration', 0))],
            ["Speakers:", f"{len(metadata.get('speakers', []))} detected"],
            ["Overall Quality:", f"{metadata.get('quality', 0.0):.0%}"],
            ["Model:", metadata.get('model', 'Whisper large-v3')],
            ["Turning Points:", str(metadata.get('turning_points_count', 0))]
        ]

        t = Table(metadata_table, colWidths=[4*cm, 12*cm])
        t.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        self.story.append(t)
        self.story.append(Spacer(1, 1*cm))

        # Turning points summary
        if metadata.get('turning_points_count', 0) > 0:
            self.story.append(Paragraph(
                "🔄 KEY TURNING POINTS SUMMARY",
                self.styles['Heading1']
            ))
            self.story.append(Spacer(1, 0.3*cm))

            tp_list = metadata.get('turning_points', [])
            for i, tp in enumerate(tp_list[:5], 1):
                time_str = self._format_time(tp.get('timestamp', 0))
                tp_type = tp.get('type', 'unknown').replace('_', ' ').title()
                confidence = tp.get('confidence', 0.0)

                tp_text = f"{i}. [{time_str}] <b>{tp_type}</b> (Confidence: {confidence:.0%})"
                self.story.append(Paragraph(tp_text, self.styles['TurningPoint']))

        self.story.append(PageBreak())

    def add_transcript_page(self, segments: List[Dict]):
        """Add transcript with speaker visualization"""
        self.story.append(Paragraph(
            "💬 FULL TRANSCRIPT",
            self.styles['Heading1']
        ))
        self.story.append(Spacer(1, 0.5*cm))

        previous_speaker = None

        for seg in segments:
            speaker_id = seg.get('speaker_id', 'unknown')
            speaker_name = seg.get('speaker_name', f'Speaker {speaker_id}')
            speaker_color = seg.get('color', '#4A90E2')
            text = seg['text']
            start = seg['start']
            end = seg['end']
            confidence = seg.get('confidence', 1.0)

            # Add divider if speaker changed
            if speaker_id != previous_speaker and previous_speaker is not None:
                self.story.append(HRFlowable(
                    width="100%",
                    thickness=1,
                    color=colors.HexColor('#BDC3C7'),
                    spaceAfter=0.3*cm
                ))

            # Speaker header
            icon = self._get_speaker_icon(hash(speaker_id) % 8)
            time_str = f"[{self._format_time(start)} - {self._format_time(end)}]"

            header_data = [[
                Paragraph(f"{icon} <b>{speaker_name}</b>", self.styles['SpeakerName']),
                Paragraph(time_str, self.styles['Normal'])
            ]]

            header_table = Table(header_data, colWidths=[12*cm, 5*cm])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(speaker_color + '20')),
                ('LEFTPADDING', (0, 0), (0, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LINEBELOW', (0, 0), (-1, -1), 3, colors.HexColor(speaker_color)),
            ]))

            self.story.append(header_table)
            self.story.append(Spacer(1, 0.2*cm))

            # Text with confidence
            if confidence < 0.7:
                text_content = f"{text} <font color='#E67E22'>[⚠️ Low confidence: {confidence:.0%}]</font>"
            else:
                text_content = text

            self.story.append(Paragraph(text_content, self.styles['Normal']))

            # Turning point box if present
            if seg.get('has_turning_point'):
                self._add_turning_point_box(seg['turning_point'])

            self.story.append(Spacer(1, 0.3*cm))
            previous_speaker = speaker_id

    def _add_turning_point_box(self, tp: Dict):
        """Add highlighted box for turning point with prosody evidence"""
        tp_type = tp.get('type', 'unknown').replace('_', ' ').title()
        confidence = tp.get('confidence', 0.0)

        # Header
        header = f"🔄 <b>TURNING POINT: {tp_type}</b> (Confidence: {confidence:.0%})"
        self.story.append(Paragraph(header, self.styles['TurningPoint']))

        # Prosody evidence table
        prosody = tp.get('prosody_evidence', {})
        if prosody:
            evidence_data = [
                ["📊 Prosody Evidence:", ""],
                ["• Pitch:", f"+{prosody.get('pitch_change', 0):.1f}% ({prosody.get('pitch_from', 0):.1f} → {prosody.get('pitch_to', 0):.1f} Hz)"],
                ["• Tempo:", f"+{prosody.get('tempo_change', 0):.1f}% ({prosody.get('tempo_from', 0):.1f} → {prosody.get('tempo_to', 0):.1f} WPM)"],
                ["• Energy:", f"+{prosody.get('energy_change', 0):.1f}% ({prosody.get('energy_from', 0):.4f} → {prosody.get('energy_to', 0):.4f})"],
                ["• CoSD Score:", f"{prosody.get('cosd_score', 0):.2f} (threshold: {prosody.get('cosd_threshold', 0.6):.2f})"]
            ]

            evidence_table = Table(evidence_data, colWidths=[4*cm, 12*cm])
            evidence_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFF9E6')),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#F39C12')),
            ]))

            self.story.append(Spacer(1, 0.2*cm))
            self.story.append(evidence_table)

    def _get_speaker_icon(self, index: int) -> str:
        """Get emoji icon for speaker"""
        icons = ["👤", "👨", "👩", "🧑", "👴", "👵", "🧔", "👱"]
        return icons[index % len(icons)]

    def _format_duration(self, seconds: float) -> str:
        """Format duration as MM:SS"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"

    def _format_time(self, seconds: float) -> str:
        """Format timestamp as MM:SS"""
        return self._format_duration(seconds)

    def generate(self):
        """Build the PDF document"""
        self.doc.build(self.story)
        print(f"✅ PDF generated: {self.output_path}")

# Usage example
if __name__ == "__main__":
    # Create test PDF
    pdf = ProfessionalPDFGenerator("test_output.pdf")

    # Add metadata
    pdf.add_metadata_page({
        'date': datetime.now(),
        'duration': 2745,
        'speakers': [
            {'name': 'Dr. Schmidt'},
            {'name': 'Patient A'}
        ],
        'quality': 0.87,
        'model': 'Whisper large-v3',
        'turning_points_count': 3,
        'turning_points': [
            {'timestamp': 225, 'type': 'cognitive_shift', 'confidence': 0.89},
            {'timestamp': 750, 'type': 'emotional_peak', 'confidence': 0.92}
        ]
    })

    # Add transcript
    segments = [
        {
            'speaker_id': 'SPEAKER_00',
            'speaker_name': 'Dr. Schmidt',
            'color': '#4A90E2',
            'start': 0.0,
            'end': 5.2,
            'text': 'Guten Tag. Wie geht es Ihnen heute?',
            'confidence': 0.95
        },
        {
            'speaker_id': 'SPEAKER_01',
            'speaker_name': 'Patient A',
            'color': '#7B68EE',
            'start': 5.2,
            'end': 12.5,
            'text': 'Ich denke, wir sollten das Projekt anders angehen.',
            'confidence': 0.88,
            'has_turning_point': True,
            'turning_point': {
                'type': 'cognitive_shift',
                'confidence': 0.89,
                'prosody_evidence': {
                    'pitch_change': 23,
                    'pitch_from': 148,
                    'pitch_to': 182,
                    'tempo_change': 35,
                    'tempo_from': 120,
                    'tempo_to': 162,
                    'energy_change': 42,
                    'energy_from': 0.045,
                    'energy_to': 0.064,
                    'cosd_score': 0.73,
                    'cosd_threshold': 0.6
                }
            }
        }
    ]

    pdf.add_transcript_page(segments)
    pdf.generate()