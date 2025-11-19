"""
MVP TransSemantic Integration Module

Connects all enhanced components into a complete transcription pipeline:
1. Whisper large-v3 transcription
2. Speaker database management
3. Professional visualization (Markdown/HTML)
4. PDF generation

Future extensions:
- Speaker diarization integration
- Turning points detection
- Prosody analysis
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import uuid

from whisper_transcriber_v3 import WhisperTranscriberV3
from speaker_database import SpeakerDatabase
from speaker_visualizer_v2 import SpeakerVisualizerV2
from professional_pdf_generator import ProfessionalPDFGenerator

logger = logging.getLogger(__name__)


class MVPTranscriptionPipeline:
    """
    Complete MVP transcription pipeline

    Integrates:
    - Whisper large-v3 for transcription
    - Speaker database for persistence
    - Professional visualization
    - PDF generation
    """

    def __init__(
        self,
        model_size: str = "large-v3",
        db_path: str = "Memory/speaker_profiles.db",
        device: str = "auto"
    ):
        """
        Initialize MVP pipeline

        Args:
            model_size: Whisper model size
            db_path: Path to speaker database
            device: 'cpu', 'cuda', or 'auto'
        """
        logger.info("🚀 Initializing MVP TransSemantic Pipeline")

        # Initialize components
        self.transcriber = WhisperTranscriberV3(
            model_size=model_size,
            device=device
        )

        self.db_path = db_path
        self.visualizer = SpeakerVisualizerV2()

        logger.info("✅ Pipeline initialized")

    def process_audio(
        self,
        audio_path: str,
        output_dir: str = "Output",
        speaker_assignments: Optional[Dict[str, str]] = None,
        generate_pdf: bool = True,
        generate_html: bool = True,
        language: str = "de"
    ) -> Dict:
        """
        Process audio file through complete pipeline

        Args:
            audio_path: Path to audio file
            output_dir: Where to save outputs
            speaker_assignments: Optional dict mapping segment index to speaker_id
                                If None, assumes single speaker (SPEAKER_00)
            generate_pdf: Whether to generate PDF report
            generate_html: Whether to generate HTML report
            language: Audio language code

        Returns:
            Dict with:
                - transcription: Whisper output
                - markdown_path: Path to Markdown file
                - html_path: Path to HTML file (if generated)
                - pdf_path: Path to PDF file (if generated)
                - speakers: Speaker information
                - session_id: Session identifier
        """
        audio_path = Path(audio_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        session_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = f"{timestamp}_{audio_path.stem}"

        logger.info(f"📝 Processing: {audio_path.name}")
        logger.info(f"   Session ID: {session_id}")

        # Step 1: Transcribe with Whisper large-v3
        logger.info("Step 1/5: Transcribing with Whisper large-v3...")
        transcription = self.transcriber.transcribe(
            str(audio_path),
            language=language
        )

        segments = transcription['segments']
        logger.info(f"   ✓ {len(segments)} segments transcribed")

        # Step 2: Assign speakers
        logger.info("Step 2/5: Assigning speakers...")

        if speaker_assignments is None:
            # Default: single speaker
            default_speaker_id = "SPEAKER_00"
            for seg in segments:
                seg['speaker_id'] = default_speaker_id
            logger.info(f"   ✓ All segments assigned to {default_speaker_id}")
        else:
            # Use provided assignments
            for i, seg in enumerate(segments):
                seg['speaker_id'] = speaker_assignments.get(i, "SPEAKER_00")
            logger.info(f"   ✓ {len(set(s['speaker_id'] for s in segments))} speakers assigned")

        # Step 3: Match/create speakers in database
        logger.info("Step 3/5: Managing speaker database...")

        with SpeakerDatabase(self.db_path) as db:
            # Create session record
            db.create_session(
                session_id=session_id,
                audio_file=str(audio_path),
                duration_seconds=transcription['metadata']['audio_duration'],
                quality_score=self._calculate_quality_score(segments)
            )

            # Get unique speakers from segments
            speaker_ids = set(seg['speaker_id'] for seg in segments)
            speakers = {}

            for speaker_id in speaker_ids:
                # Check if speaker exists
                speaker = db.get_speaker(speaker_id)

                if speaker is None:
                    # Create new speaker
                    logger.info(f"   Creating new speaker: {speaker_id}")
                    db.add_speaker(
                        speaker_id=speaker_id,
                        name=f"Speaker {speaker_id[-2:]}",  # e.g., "Speaker 00"
                    )
                    speaker = db.get_speaker(speaker_id)

                speakers[speaker_id] = speaker

                # Calculate speaker stats for this session
                speaker_segments = [s for s in segments if s['speaker_id'] == speaker_id]
                speaker_duration = sum(s['end'] - s['start'] for s in speaker_segments)

                # Add to session
                db.add_session_speaker(
                    session_id=session_id,
                    speaker_id=speaker_id,
                    duration_seconds=speaker_duration,
                    segment_count=len(speaker_segments)
                )

            # Add speaker names and colors to segments
            for seg in segments:
                speaker_id = seg['speaker_id']
                seg['speaker_name'] = speakers[speaker_id]['name']
                seg['color'] = speakers[speaker_id]['color']

            logger.info(f"   ✓ {len(speakers)} speaker profiles updated")

        # Step 4: Generate visualizations
        logger.info("Step 4/5: Generating visualizations...")

        # Prepare metadata
        metadata = {
            'title': 'TransSemantic Transcription Report',
            'audio_file': audio_path.name,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'duration': transcription['metadata']['audio_duration'],
            'model': transcription['metadata']['model'],
            'quality_score': self._calculate_quality_score(segments),
            'speakers': [
                {
                    **speakers[sid],
                    'segment_count': len([s for s in segments if s['speaker_id'] == sid]),
                    'duration': sum(s['end'] - s['start'] for s in segments if s['speaker_id'] == sid)
                }
                for sid in speakers
            ]
        }

        # Generate Markdown
        markdown_content = self.visualizer.format_markdown(segments)
        markdown_path = output_dir / f"{base_name}_transcript.md"
        markdown_path.write_text(markdown_content, encoding='utf-8')
        logger.info(f"   ✓ Markdown: {markdown_path}")

        result = {
            'transcription': transcription,
            'markdown_path': str(markdown_path),
            'speakers': speakers,
            'session_id': session_id
        }

        # Generate HTML (optional)
        if generate_html:
            html_content = self.visualizer.format_html(segments)
            html_path = output_dir / f"{base_name}_transcript.html"
            html_path.write_text(html_content, encoding='utf-8')
            logger.info(f"   ✓ HTML: {html_path}")
            result['html_path'] = str(html_path)

        # Step 5: Generate PDF (optional)
        if generate_pdf:
            logger.info("Step 5/5: Generating PDF report...")

            # Prepare metadata for PDF generation
            pdf_metadata = {
                'date': datetime.now(),
                'duration': transcription['metadata']['audio_duration'],
                'speakers': [
                    {
                        'name': speakers[sid]['name'],
                        'color': speakers[sid]['color'],
                        'total_duration': sum(s['end'] - s['start'] for s in segments if s['speaker_id'] == sid),
                        'segment_count': len([s for s in segments if s['speaker_id'] == sid])
                    }
                    for sid in speakers
                ],
                'quality': self._calculate_quality_score(segments),
                'model': 'Whisper large-v3',
                'turning_points_count': 0,  # TODO: Integrate turning points
                'turning_points': []  # TODO: Integrate turning points
            }

            pdf_path = output_dir / f"{base_name}_report.pdf"

            pdf_gen = ProfessionalPDFGenerator(str(pdf_path))
            pdf_gen.add_metadata_page(pdf_metadata)
            pdf_gen.add_transcript_page(segments)
            pdf_gen.generate()

            logger.info(f"   ✓ PDF: {pdf_path}")
            result['pdf_path'] = str(pdf_path)

        logger.info("✅ Pipeline complete!")
        logger.info(f"   Session: {session_id}")
        logger.info(f"   Duration: {metadata['duration']:.1f}s")
        logger.info(f"   Segments: {len(segments)}")
        logger.info(f"   Speakers: {len(speakers)}")
        logger.info(f"   Quality: {metadata['quality_score']*100:.1f}%")

        return result

    def _calculate_quality_score(self, segments: List[Dict]) -> float:
        """
        Calculate overall quality score from segments

        Args:
            segments: List of segment dicts with confidence scores

        Returns:
            Average confidence score (0-1)
        """
        if not segments:
            return 0.0

        confidences = [seg.get('confidence', 1.0) for seg in segments]
        return sum(confidences) / len(confidences)

    def get_pipeline_info(self) -> Dict:
        """Get information about the pipeline configuration"""
        return {
            'transcriber': self.transcriber.get_model_info(),
            'database': self.db_path,
            'version': 'MVP-v1.0'
        }


# Example usage and testing
if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    print("\n🎤 MVP TransSemantic Pipeline")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("\n💡 Usage: python3 mvp_integrator.py <audio_file> [speaker_count]")
        print("\nExample:")
        print("  python3 mvp_integrator.py audio.mp3")
        print("  python3 mvp_integrator.py audio.mp3 2")
        print("\nTests with sample data if no arguments provided:")

        # Create test with sample data
        print("\n📝 Running test with sample data...")

        # Use existing test audio if available
        test_files = list(Path("Eingang").rglob("*.opus"))
        test_files.extend(list(Path("Eingang").rglob("*.mp3")))
        test_files.extend(list(Path("Eingang").rglob("*.wav")))

        if test_files:
            audio_file = str(test_files[0])
            print(f"\n✓ Found test audio: {Path(audio_file).name}")

            # Initialize pipeline
            pipeline = MVPTranscriptionPipeline(
                model_size="base",  # Use smaller model for testing
                device="auto"
            )

            # Show pipeline info
            print("\n📊 Pipeline Configuration:")
            info = pipeline.get_pipeline_info()
            print(f"   Model: {info['transcriber']['model_size']}")
            print(f"   Device: {info['transcriber']['device']}")
            print(f"   Database: {info['database']}")
            print(f"   Version: {info['version']}")

            # Process audio
            print("\n🚀 Starting pipeline...")
            result = pipeline.process_audio(
                audio_path=audio_file,
                output_dir="Output",
                generate_pdf=True,
                generate_html=True
            )

            print("\n📦 Output Files:")
            print(f"   Markdown: {result['markdown_path']}")
            if 'html_path' in result:
                print(f"   HTML: {result['html_path']}")
            if 'pdf_path' in result:
                print(f"   PDF: {result['pdf_path']}")

        else:
            print("\n❌ No test audio files found in Eingang/")
            print("   Please provide an audio file as argument")

    else:
        # Process provided audio file
        audio_file = sys.argv[1]
        speaker_count = int(sys.argv[2]) if len(sys.argv) > 2 else 1

        if not Path(audio_file).exists():
            print(f"\n❌ Error: File not found: {audio_file}")
            sys.exit(1)

        # Initialize pipeline
        pipeline = MVPTranscriptionPipeline(
            model_size="large-v3",
            device="auto"
        )

        # Show pipeline info
        print("\n📊 Pipeline Configuration:")
        info = pipeline.get_pipeline_info()
        for key, value in info.items():
            if isinstance(value, dict):
                print(f"\n{key}:")
                for k, v in value.items():
                    print(f"  {k}: {v}")
            else:
                print(f"{key}: {value}")

        print("\n🚀 Starting pipeline...")
        print(f"   Audio: {Path(audio_file).name}")
        print(f"   Expected speakers: {speaker_count}")

        # For multi-speaker, we'll need diarization
        # For now, default to single speaker
        result = pipeline.process_audio(
            audio_path=audio_file,
            output_dir="Output",
            generate_pdf=True,
            generate_html=True
        )

        print("\n✅ Processing complete!")
        print(f"\n📦 Output Files:")
        print(f"   Markdown: {result['markdown_path']}")
        if 'html_path' in result:
            print(f"   HTML: {result['html_path']}")
        if 'pdf_path' in result:
            print(f"   PDF: {result['pdf_path']}")

        print(f"\n📊 Statistics:")
        trans = result['transcription']
        print(f"   Segments: {len(trans['segments'])}")
        print(f"   Duration: {trans['metadata']['audio_duration']:.1f}s")
        print(f"   Processing time: {trans['metadata']['processing_time']:.1f}s")
        print(f"   Real-time factor: {trans['metadata']['real_time_factor']:.1f}x")
        print(f"   Speakers: {len(result['speakers'])}")
