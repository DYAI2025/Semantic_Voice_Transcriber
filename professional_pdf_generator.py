"""
Professional PDF Generator for TransSemantic Transcriptions

Generates publication-quality PDF reports with:
- Metadata page (date, duration, speakers, quality metrics)
- Speaker-colored transcript with icons and dividers
- Turning Points visualization with prosody evidence
- Professional layout and typography
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether, Flowable
)
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

logger = logging.getLogger(__name__)


class ProfessionalPDFGenerator:
    """Generate professional PDF reports for transcriptions"""

    # Color palette for speakers (hex to RGB)
    SPEAKER_COLORS = {
        '#4A90E2': (74/255, 144/255, 226/255),   # Blue
        '#7B68EE': (123/255, 104/255, 238/255),  # Purple
        '#50C878': (80/255, 200/255, 120/255),   # Green
        '#FF6B6B': (255/255, 107/255, 107/255),  # Red
        '#FFA500': (255/255, 165/255, 0/255),    # Orange
        '#20B2AA': (32/255, 178/255, 170/255),   # Teal
        '#FF69B4': (255/255, 105/255, 180/255),  # Pink
        '#FFD700': (255/255, 215/255, 0/255),    # Gold
    }

    # Speaker icons
    SPEAKER_ICONS = {
        0: "👤", 1: "👨", 2: "👩", 3: "🧑", 4: "👴",
        5: "👵", 6: "🧔", 7: "👨‍⚕️", 8: "👩‍⚕️"
    }

    def __init__(self, output_path: str, page_size=A4):
        """
        Initialize PDF generator

        Args:
            output_path: Where to save PDF
            page_size: Paper size (default: A4)
        """
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        self.page_size = page_size
        self.width, self.height = page_size

        # Story holds all document elements
        self.story = []

        # Create document
        self.doc = SimpleDocTemplate(
            str(self.output_path),
            pagesize=page_size,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
        )

        # Initialize styles
        self._init_styles()

        logger.info(f"Initialized PDF generator: {self.output_path}")

    def _init_styles(self):
        """Initialize text styles"""
        self.styles = getSampleStyleSheet()

        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))

        # Speaker name style
        self.styles.add(ParagraphStyle(
            name='SpeakerName',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            spaceAfter=6,
            textColor=colors.HexColor('#2C3E50')
        ))

        # Transcript text
        self.styles.add(ParagraphStyle(
            name='TranscriptText',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            spaceAfter=12
        ))

        # Turning point style
        self.styles.add(ParagraphStyle(
            name='TurningPoint',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#E74C3C'),
            fontName='Helvetica-Bold',
            spaceAfter=8,
            spaceBefore=8
        ))

        # Metadata style
        self.styles.add(ParagraphStyle(
            name='Metadata',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            fontName='Helvetica'
        ))

        # Timestamp style
        self.styles.add(ParagraphStyle(
            name='Timestamp',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#7F8C8D'),
            fontName='Helvetica'
        ))

    def add_metadata_page(self, metadata: Dict):
        """
        Add metadata cover page

        Args:
            metadata: Dict with keys:
                - title: Report title
                - audio_file: Source audio filename
                - date: Processing date
                - duration: Audio duration in seconds
                - speakers: List of speaker dicts
                - model: Whisper model used
                - quality_score: Overall quality (0-1)
        """
        # Title
        title = metadata.get('title', 'TransSemantic Transcription Report')
        self.story.append(Paragraph(title, self.styles['CustomTitle']))
        self.story.append(Spacer(1, 0.5*inch))

        # Create metadata table
        data = []

        # Audio file
        if 'audio_file' in metadata:
            data.append(['Audio File:', metadata['audio_file']])

        # Date
        date_str = metadata.get('date', datetime.now().strftime('%Y-%m-%d %H:%M'))
        data.append(['Processing Date:', date_str])

        # Duration
        if 'duration' in metadata:
            duration = metadata['duration']
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            data.append(['Duration:', f'{minutes}m {seconds}s'])

        # Model
        if 'model' in metadata:
            data.append(['Whisper Model:', metadata['model']])

        # Quality score
        if 'quality_score' in metadata:
            quality = metadata['quality_score']
            quality_pct = f"{quality*100:.1f}%"
            quality_level = (
                "Excellent" if quality >= 0.9 else
                "Very Good" if quality >= 0.8 else
                "Good" if quality >= 0.7 else
                "Fair" if quality >= 0.6 else
                "Poor"
            )
            data.append(['Quality Score:', f'{quality_pct} ({quality_level})'])

        # Number of speakers
        speakers = metadata.get('speakers', [])
        data.append(['Speakers Detected:', str(len(speakers))])

        # Create table
        table = Table(data, colWidths=[3*inch, 4*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#34495E')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 0.5*inch))

        # Speaker legend
        if speakers:
            self.story.append(Paragraph('Speaker Overview', self.styles['SectionHeading']))

            speaker_data = [['ID', 'Name', 'Color', 'Segments', 'Duration']]

            for speaker in speakers:
                speaker_id = speaker.get('speaker_id', 'N/A')
                name = speaker.get('name', f'Speaker {speaker_id}')
                color = speaker.get('color', '#4A90E2')
                segments = speaker.get('segment_count', 0)
                duration = speaker.get('duration', 0)

                duration_str = f"{int(duration//60)}m {int(duration%60)}s"

                # Color indicator (using background color)
                speaker_data.append([
                    speaker_id,
                    name,
                    '',  # Will be colored
                    str(segments),
                    duration_str
                ])

            speaker_table = Table(speaker_data, colWidths=[1*inch, 2*inch, 0.7*inch, 1*inch, 1.3*inch])

            # Style speaker table
            table_style = [
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
            ]

            # Add color to color column
            for i, speaker in enumerate(speakers, start=1):
                color_hex = speaker.get('color', '#4A90E2')
                rgb = self._hex_to_rgb(color_hex)
                table_style.append(('BACKGROUND', (2, i), (2, i), colors.Color(*rgb)))

            speaker_table.setStyle(TableStyle(table_style))

            self.story.append(speaker_table)

        # Page break after metadata
        self.story.append(PageBreak())

    def add_transcript_page(self, segments: List[Dict], speakers: Dict[str, Dict]):
        """
        Add transcript with speaker formatting

        Args:
            segments: List of segment dicts with:
                - speaker: Speaker ID
                - start: Start time
                - end: End time
                - text: Transcribed text
                - confidence: Confidence score (0-1)
            speakers: Dict mapping speaker_id to speaker info (name, color, icon_index)
        """
        self.story.append(Paragraph('Transcript', self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2*inch))

        last_speaker = None

        for seg in segments:
            speaker_id = seg.get('speaker', 'UNKNOWN')
            speaker_info = speakers.get(speaker_id, {})

            # Speaker change - add divider
            if speaker_id != last_speaker:
                if last_speaker is not None:
                    # Add divider line
                    self.story.append(Spacer(1, 0.15*inch))
                    self.story.append(HorizontalLine())
                    self.story.append(Spacer(1, 0.15*inch))

                # Speaker name with icon
                name = speaker_info.get('name', f'Speaker {speaker_id}')
                icon_index = speaker_info.get('icon_index', 0)
                icon = self.SPEAKER_ICONS.get(icon_index, '👤')
                color_hex = speaker_info.get('color', '#4A90E2')

                speaker_text = f'{icon} <b>{name}</b>'
                speaker_para = Paragraph(speaker_text, self.styles['SpeakerName'])

                # Create colored box for speaker using Table
                rgb = self._hex_to_rgb(color_hex)
                speaker_table = Table([[speaker_para]], colWidths=[self.width - 4*cm])
                speaker_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.Color(*rgb, alpha=0.15)),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))

                self.story.append(speaker_table)
                self.story.append(Spacer(1, 0.1*inch))

                last_speaker = speaker_id

            # Timestamp
            start_time = seg.get('start', 0)
            end_time = seg.get('end', 0)
            timestamp_str = f"[{self._format_timestamp(start_time)} - {self._format_timestamp(end_time)}]"

            timestamp = Paragraph(timestamp_str, self.styles['Timestamp'])
            self.story.append(timestamp)
            self.story.append(Spacer(1, 0.05*inch))

            # Text with confidence indicator
            text = seg.get('text', '').strip()
            confidence = seg.get('confidence', 1.0)

            # Add confidence indicator for low confidence
            if confidence < 0.7:
                text = f'{text} <font color="#E74C3C">[?]</font>'

            text_para = Paragraph(text, self.styles['TranscriptText'])
            self.story.append(text_para)

            # Check for turning point
            if seg.get('is_turning_point', False):
                self.story.append(Spacer(1, 0.1*inch))
                self._add_turning_point_box(seg.get('turning_point_data', {}))
                self.story.append(Spacer(1, 0.1*inch))

    def _add_turning_point_box(self, tp_data: Dict):
        """
        Add highlighted turning point box with prosody evidence

        Args:
            tp_data: Dict with turning point information:
                - reason: Why this is a turning point
                - cosd_score: CoSD score
                - pitch_change: Pitch change percentage
                - tempo_change: Tempo change percentage
                - energy_change: Energy change percentage
                - semantic_markers: List of detected markers
        """
        # Title
        title = Paragraph(
            '🔄 <b>Turning Point Detected</b>',
            self.styles['TurningPoint']
        )
        self.story.append(title)

        # Evidence table
        evidence_data = []

        if 'cosd_score' in tp_data:
            score = tp_data['cosd_score']
            evidence_data.append(['CoSD Score:', f'{score:.3f}'])

        if 'pitch_change' in tp_data:
            change = tp_data['pitch_change']
            evidence_data.append(['Pitch Change:', f'{change:+.1f}%'])

        if 'tempo_change' in tp_data:
            change = tp_data['tempo_change']
            evidence_data.append(['Tempo Change:', f'{change:+.1f}%'])

        if 'energy_change' in tp_data:
            change = tp_data['energy_change']
            evidence_data.append(['Energy Change:', f'{change:+.1f}%'])

        if 'semantic_markers' in tp_data and tp_data['semantic_markers']:
            markers = ', '.join(tp_data['semantic_markers'])
            evidence_data.append(['Semantic Markers:', markers])

        if evidence_data:
            evidence_table = Table(evidence_data, colWidths=[2*inch, 3*inch])
            evidence_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFF3E0')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E74C3C')),
            ]))

            self.story.append(evidence_table)

        # Reason
        if 'reason' in tp_data:
            reason_para = Paragraph(
                f'<i>{tp_data["reason"]}</i>',
                self.styles['Metadata']
            )
            self.story.append(Spacer(1, 0.05*inch))
            self.story.append(reason_para)

    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds as MM:SS or HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple (0-1 range)"""
        if hex_color in self.SPEAKER_COLORS:
            return self.SPEAKER_COLORS[hex_color]

        # Parse hex
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16) / 255
            g = int(hex_color[2:4], 16) / 255
            b = int(hex_color[4:6], 16) / 255
            return (r, g, b)

        return (0.5, 0.5, 0.5)  # Default gray

    def generate(self):
        """Build and save PDF"""
        try:
            self.doc.build(self.story)
            logger.info(f"✅ PDF generated: {self.output_path}")
            return str(self.output_path)
        except Exception as e:
            logger.error(f"❌ PDF generation failed: {e}")
            raise


# Custom Flowables

class HorizontalLine(Flowable):
    """Horizontal divider line"""

    def __init__(self, width=None, color=colors.HexColor('#BDC3C7'), thickness=1):
        Flowable.__init__(self)
        self._width = width
        self.color = color
        self.thickness = thickness

    def wrap(self, availWidth, availHeight):
        self.width = self._width or availWidth
        self.height = self.thickness
        return (self.width, self.height)

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 0, self.width, 0)


class ColoredBox(Flowable):
    """Colored background box for speaker names"""

    def __init__(self, content, color, padding=5):
        Flowable.__init__(self)
        self.content = content
        self.color = color
        self.padding = padding
        self.width = 0
        self.height = 0

    def wrap(self, availWidth, availHeight):
        content_width, content_height = self.content.wrap(availWidth - 2*self.padding, availHeight)
        self.width = content_width + 2*self.padding
        self.height = content_height + 2*self.padding
        return (self.width, self.height)

    def draw(self):
        # Draw colored background
        self.canv.setFillColor(colors.Color(*self.color, alpha=0.15))
        self.canv.rect(
            0, 0,
            self.width, self.height,
            stroke=0, fill=1
        )

        # Draw content
        self.content.drawOn(self.canv, self.padding, self.padding)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Sample data
    metadata = {
        'title': 'Therapeutic Session Transcript',
        'audio_file': 'session_2024_11_12.mp3',
        'date': '2024-11-12 14:30',
        'duration': 1847.5,  # ~30 minutes
        'model': 'large-v3',
        'quality_score': 0.87,
        'speakers': [
            {
                'speaker_id': 'SPEAKER_00',
                'name': 'Dr. Schmidt',
                'color': '#4A90E2',
                'icon_index': 7,
                'segment_count': 45,
                'duration': 923.2
            },
            {
                'speaker_id': 'SPEAKER_01',
                'name': 'Patient A',
                'color': '#7B68EE',
                'icon_index': 3,
                'segment_count': 42,
                'duration': 924.3
            }
        ]
    }

    speakers_dict = {
        'SPEAKER_00': metadata['speakers'][0],
        'SPEAKER_01': metadata['speakers'][1]
    }

    segments = [
        {
            'speaker': 'SPEAKER_00',
            'start': 0.0,
            'end': 5.2,
            'text': 'Guten Tag, wie geht es Ihnen heute?',
            'confidence': 0.95
        },
        {
            'speaker': 'SPEAKER_01',
            'start': 5.8,
            'end': 12.3,
            'text': 'Danke, mir geht es etwas besser als letzte Woche.',
            'confidence': 0.89
        },
        {
            'speaker': 'SPEAKER_00',
            'start': 13.0,
            'end': 18.5,
            'text': 'Das freut mich zu hören. Wenn ich fragen darf, was hat sich verändert?',
            'confidence': 0.92,
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
            'text': 'Ich habe angefangen, die Atemübungen zu machen, die Sie mir empfohlen haben. Das hilft mir wirklich, besonders in stressigen Momenten.',
            'confidence': 0.88
        }
    ]

    # Generate PDF
    pdf_gen = ProfessionalPDFGenerator('Output/test_report.pdf')
    pdf_gen.add_metadata_page(metadata)
    pdf_gen.add_transcript_page(segments, speakers_dict)
    pdf_path = pdf_gen.generate()

    print(f"\n✅ PDF generated: {pdf_path}")
