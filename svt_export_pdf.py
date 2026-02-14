#!/usr/bin/env python3
"""
SVT Export - PDF Generation for Therapy Transcriptions
Professional PDF output with speaker separation

Requirements:
    pip install reportlab

Usage:
    from svt_export_pdf import generate_pdf
    generate_pdf(transcript_data, "/output/therapie_bericht.pdf")
"""

from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path


def generate_pdf(
    transcript_data: List[Dict[str, Any]],
    output_path: str,
    title: str = "Therapie Transkription",
    patient_name: str = "",
    therapist_name: str = "",
    session_date: str = "",
    include_analysis: bool = True,
    analysis_text: str = ""
) -> str:
    """
    Generate a professional PDF from transcription data.
    
    Args:
        transcript_data: List of transcript segments with speaker/text
        output_path: Path to save PDF
        title: Report title
        patient_name: Patient name (optional)
        therapist_name: Therapist name (optional)
        session_date: Session date (optional)
        include_analysis: Include analysis section
        analysis_text: Analysis content (optional)
    
    Returns:
        Path to generated PDF
    """
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
    
    # Create document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#2d3748")
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor("#4299e1")
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        leading=16,
        alignment=TA_JUSTIFY
    )
    
    speaker_style = ParagraphStyle(
        'Speaker',
        parent=styles['Heading4'],
        fontSize=12,
        spaceAfter=4,
        textColor=colors.HexColor("#4299e1"),
        fontName='Helvetica-Bold'
    )
    
    timestamp_style = ParagraphStyle(
        'Timestamp',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor("#a0aec0"),
        spaceAfter=8
    )
    
    # Build story
    story = []
    
    # Header
    story.append(Paragraph("🎤 SVT Local", ParagraphStyle(
        'Logo',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor("#a0aec0"),
        alignment=TA_CENTER
    )))
    story.append(Spacer(1, 20))
    
    # Title
    story.append(Paragraph(title, title_style))
    
    # Metadata
    metadata = []
    if patient_name:
        metadata.append(f"Patient: {patient_name}")
    if therapist_name:
        metadata.append(f"Therapeut: {therapist_name}")
    if session_date:
        metadata.append(f"Datum: {session_date}")
    metadata.append(f"Erstellt: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    
    for line in metadata:
        story.append(Paragraph(line, ParagraphStyle(
            'Meta',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor("#718096"),
            spaceAfter=4
        )))
    
    story.append(Spacer(1, 30))
    
    # Summary Table
    summary_data = []
    
    # Calculate stats
    total_duration = 0
    total_words = 0
    speaker_times = {}
    
    for seg in transcript_data:
        duration = seg.get("end", 0) - seg.get("start", 0)
        total_duration += duration
        
        text = seg.get("text", "")
        words = len(text.split()) if text else 0
        total_words += words
        
        speaker = seg.get("speaker", "Unknown")
        if speaker not in speaker_times:
            speaker_times[speaker] = {"duration": 0, "words": 0, "segments": 0}
        speaker_times[speaker]["duration"] += duration
        speaker_times[speaker]["words"] += words
        speaker_times[speaker]["segments"] += 1
    
    summary_data.append(["Metrik", "Wert"])
    summary_data.append["Gesamtdauer", f"{int(total_duration // 60)}:{int(total_duration % 60):02d}"]
    summary_data.append(["Gesamtwörter", str(total_words)])
    summary_data.append(["Segmente", str(len(transcript_data))])
    summary_data.append(["Sprecher", str(len(speaker_times))])
    
    for spk, data in speaker_times.items():
        summary_data.append([
            f"{spk} Zeit",
            f"{int(data['duration'] // 60)}:{int(data['duration'] % 60):02d}"
        ])
    
    # Create summary table
    summary_table = Table(summary_data, colWidths=[2.5*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4299e1")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f7fafc")),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 30))
    
    # Divider
    story.append(Paragraph("─" * 50, ParagraphStyle(
        'Divider',
        parent=styles['Normal'],
        textColor=colors.HexColor("#e2e8f0"),
        alignment=TA_CENTER
    )))
    story.append(Spacer(1, 20))
    
    # Transkript
    story.append(Paragraph("📝 Transkript", heading_style))
    
    current_speaker = None
    for seg in transcript_data:
        speaker = seg.get("speaker", "Unknown")
        text = seg.get("text", "")
        start = seg.get("start", 0)
        end = seg.get("end", 0)
        
        # New speaker header
        if speaker != current_speaker:
            story.append(Paragraph(f"👤 {speaker}", speaker_style))
            current_speaker = speaker
        
        # Timestamp
        timestamp = f"{int(start // 60)}:{int(start % 60):02d} - {int(end // 60)}:{int(end % 60):02d}"
        story.append(Paragraph(f"({timestamp})", timestamp_style))
        
        # Text
        story.append(Paragraph(text, body_style))
        story.append(Spacer(1, 10))
    
    # Analysis Section
    if include_analysis and analysis_text:
        story.append(PageBreak())
        story.append(Paragraph("🧠 Analyse", heading_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph(analysis_text, body_style))
    
    # Footer
    story.append(PageBreak())
    story.append(Spacer(1, 20))
    story.append(Paragraph("─" * 50, ParagraphStyle(
        'Divider',
        parent=styles['Normal'],
        textColor=colors.HexColor("#e2e8f0"),
        alignment=TA_CENTER
    )))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Generiert von SVT Local | Therapie Transkription",
        ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor("#a0aec0"),
            alignment=TA_CENTER
        )
    ))
    
    # Build PDF
    doc.build(story)
    
    return output_path


def create_simple_report(
    transcript_data: List[Dict[str, Any]],
    output_path: str,
    patient_name: str = ""
) -> str:
    """
    Create a simple therapy report PDF.
    """
    session_date = datetime.now().strftime("%d.%m.%Y")
    
    # Generate analysis summary
    analysis = generate_analysis_summary(transcript_data)
    
    return generate_pdf(
        transcript_data=transcript_data,
        output_path=output_path,
        title="Therapie Transkription",
        patient_name=patient_name,
        session_date=session_date,
        include_analysis=True,
        analysis_text=analysis
    )


def generate_analysis_summary(transcript_data: List[Dict[str, Any]]) -> str:
    """
    Generate a simple analysis summary from transcript.
    """
    speaker_times = {}
    total_duration = 0
    
    for seg in transcript_data:
        duration = seg.get("end", 0) - seg.get("start", 0)
        total_duration += duration
        speaker = seg.get("speaker", "Unknown")
        
        if speaker not in speaker_times:
            speaker_times[speaker] = 0
        speaker_times[speaker] += duration
    
    # Build summary
    lines = []
    lines.append("Dieses Transkript wurde automatisch erstellt.")
    lines.append("")
    lines.append(f"**Gesamtdauer:** {int(total_duration // 60)} Minuten")
    lines.append("")
    lines.append("**Sprecheraufteilung:**")
    
    for spk, duration in sorted(speaker_times.items(), key=lambda x: -x[1]):
        pct = (duration / total_duration * 100) if total_duration > 0 else 0
        lines.append(f"- {spk}: {int(duration // 60)} Min ({pct:.1f}%)")
    
    lines.append("")
    lines.append("**Hinweis:**")
    lines.append("Dies ist eine automatische Transkription. Für therapeutische Zwecke")
    lines.append("empfehlen wir eine manuelle Überprüfung der Inhalte.")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Example usage
    example_data = [
        {"start": 0, "end": 30, "speaker": "Therapeut", "text": "Guten Tag, wie geht es Ihnen heute?"},
        {"start": 30, "end": 90, "speaker": "Patient", "text": "Naja, es geht so. Ich habe schlecht geschlafen."},
        {"start": 90, "end": 150, "speaker": "Therapeut", "text": "Erzählen Sie mir mehr darüber."},
    ]
    
    output = "/tmp/therapie_bericht.pdf"
    generate_pdf(example_data, output, patient_name="Max Mustermann")
    print(f"PDF erstellt: {output}")
