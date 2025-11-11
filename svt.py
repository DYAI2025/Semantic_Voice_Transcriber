#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Semantic Voice Transcriber (SVT) - Professional one-click workflow
High-quality transcription with prosody analysis, emotion detection, and confidence scoring
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
import queue
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import auto_transcriber_v4_emotion as v4
from audio_quality_analyzer import AudioQualityAnalyzer
from audio_preprocessor import AudioPreprocessor
from output_formatter import OutputFormatter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemanticVoiceTranscriberGUI:
    """Professional GUI for semantic voice transcription with prosody analysis"""

    def __init__(self, root):
        self.root = root
        self.root.title("Semantic Voice Transcriber (SVT)")
        self.root.geometry("900x700")

        # Progress queue for thread communication
        self.progress_queue = queue.Queue()
        self.processing_thread = None
        self.is_processing = False

        # Default paths
        self.input_dir = Path("Eingang")
        self.output_dir = Path("Transkripte_LLM")
        self.memory_dir = Path("Memory")

        # Intelligent pipeline components
        self.quality_analyzer = AudioQualityAnalyzer()
        self.audio_preprocessor = AudioPreprocessor()
        self.output_formatter = OutputFormatter()

        self._create_widgets()
        self._check_progress_queue()

    def _create_widgets(self):
        """Create all GUI widgets"""

        # Title
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        title_label = ttk.Label(
            title_frame,
            text="🎤 Semantic Voice Transcriber",
            font=("Helvetica", 18, "bold")
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            title_frame,
            text="Deep Voice Analysis · Prosody · Emotion · Semantic Markers",
            font=("Helvetica", 10)
        )
        subtitle_label.pack()

        # Configuration frame
        config_frame = ttk.LabelFrame(self.root, text="Konfiguration", padding="10")
        config_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)

        # Input directory
        ttk.Label(config_frame, text="Eingabe-Ordner:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_dir_var = tk.StringVar(value=str(self.input_dir))
        ttk.Entry(config_frame, textvariable=self.input_dir_var, width=50).grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(config_frame, text="Durchsuchen...", command=self._browse_input_dir).grid(row=0, column=2, pady=5)

        # Output directory
        ttk.Label(config_frame, text="Ausgabe-Ordner:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_dir_var = tk.StringVar(value=str(self.output_dir))
        ttk.Entry(config_frame, textvariable=self.output_dir_var, width=50).grid(row=1, column=1, pady=5, padx=5)
        ttk.Button(config_frame, text="Durchsuchen...", command=self._browse_output_dir).grid(row=1, column=2, pady=5)

        # Quality settings frame
        quality_frame = ttk.LabelFrame(self.root, text="Qualitäts-Einstellungen", padding="10")
        quality_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)

        # Whisper model selection
        ttk.Label(quality_frame, text="Whisper-Modell:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar(value="medium")
        model_combo = ttk.Combobox(
            quality_frame,
            textvariable=self.model_var,
            values=["tiny", "base", "small", "medium", "large"],
            state="readonly",
            width=15
        )
        model_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)

        ttk.Label(quality_frame, text="(medium empfohlen für Therapie)").grid(row=0, column=2, sticky=tk.W, pady=5)

        # Language
        ttk.Label(quality_frame, text="Sprache:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.language_var = tk.StringVar(value="de")
        lang_combo = ttk.Combobox(
            quality_frame,
            textvariable=self.language_var,
            values=["de", "en", "auto"],
            state="readonly",
            width=15
        )
        lang_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)

        # Confidence threshold
        ttk.Label(quality_frame, text="Confidence-Schwellwert:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.confidence_var = tk.DoubleVar(value=0.5)
        confidence_spin = ttk.Spinbox(
            quality_frame,
            from_=0.1,
            to=0.9,
            increment=0.1,
            textvariable=self.confidence_var,
            width=15
        )
        confidence_spin.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(quality_frame, text="(niedrigere Werte = mehr Warnungen)").grid(row=2, column=2, sticky=tk.W, pady=5)

        # Intelligent Pipeline toggle
        ttk.Label(quality_frame, text="Intelligente Pipeline:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.intelligent_pipeline_var = tk.BooleanVar(value=True)
        intelligent_checkbox = ttk.Checkbutton(
            quality_frame,
            text="Auto-Qualitätsanalyse & Preprocessing aktivieren",
            variable=self.intelligent_pipeline_var
        )
        intelligent_checkbox.grid(row=3, column=1, columnspan=2, sticky=tk.W, pady=5, padx=5)

        ttk.Label(
            quality_frame,
            text="(Analysiert Audio-Qualität und wählt optimale Einstellungen)",
            font=("Helvetica", 9, "italic")
        ).grid(row=4, column=1, columnspan=2, sticky=tk.W, padx=5)

        # Feature toggles frame
        features_frame = ttk.LabelFrame(self.root, text="Features", padding="10")
        features_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)

        self.emotion_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            features_frame,
            text="Emotions-Analyse aktivieren",
            variable=self.emotion_var
        ).grid(row=0, column=0, sticky=tk.W, pady=2)

        self.prosody_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            features_frame,
            text="Prosody-Extraktion aktivieren (Voice-Marker 2.0)",
            variable=self.prosody_var
        ).grid(row=1, column=0, sticky=tk.W, pady=2)

        self.memory_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            features_frame,
            text="Memory-Profile aktualisieren",
            variable=self.memory_var
        ).grid(row=2, column=0, sticky=tk.W, pady=2)

        # Audio file selection frame
        file_frame = ttk.LabelFrame(self.root, text="Audio-Dateien", padding="10")
        file_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)

        ttk.Label(file_frame, text="Audio-Dateien auswählen:").grid(row=0, column=0, sticky=tk.W, pady=5)

        self.file_listbox = tk.Listbox(file_frame, selectmode=tk.MULTIPLE, height=8, width=80)
        self.file_listbox.grid(row=1, column=0, columnspan=2, pady=5, padx=5)

        # Scrollbar for file listbox
        scrollbar = ttk.Scrollbar(file_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        ttk.Button(file_frame, text="🔄 Dateien aktualisieren", command=self._refresh_files).grid(row=2, column=0, pady=5, sticky=tk.W)
        ttk.Button(file_frame, text="✓ Alle auswählen", command=self._select_all_files).grid(row=2, column=1, pady=5, sticky=tk.W)

        # Control buttons frame
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)

        self.start_button = ttk.Button(
            control_frame,
            text="🚀 Transkription starten",
            command=self._start_transcription,
            style="Accent.TButton"
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(
            control_frame,
            text="⏹ Stoppen",
            command=self._stop_transcription,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.test_button = ttk.Button(
            control_frame,
            text="🧪 Quick Test (erste Datei)",
            command=self._run_quick_test
        )
        self.test_button.pack(side=tk.LEFT, padx=5)

        self.prosody_test_button = ttk.Button(
            control_frame,
            text="🎵 Prosody Test (30s)",
            command=self._run_prosody_test
        )
        self.prosody_test_button.pack(side=tk.LEFT, padx=5)

        # Progress frame
        progress_frame = ttk.LabelFrame(self.root, text="Fortschritt", padding="10")
        progress_frame.grid(row=6, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=5)

        self.status_label = ttk.Label(progress_frame, text="Bereit")
        self.status_label.pack(pady=5)

        # Log output
        log_frame = ttk.LabelFrame(self.root, text="Log", padding="10")
        log_frame.grid(row=7, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(7, weight=1)

        # Initial file refresh
        self.audio_files = []  # Initialize audio files list
        self._refresh_files()

    def _browse_input_dir(self):
        """Browse for input directory"""
        directory = filedialog.askdirectory(initialdir=self.input_dir)
        if directory:
            self.input_dir_var.set(directory)
            self._refresh_files()

    def _browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(initialdir=self.output_dir)
        if directory:
            self.output_dir_var.set(directory)

    def _refresh_files(self):
        """Refresh list of available audio files from input directory"""
        self.file_listbox.delete(0, tk.END)
        self.audio_files = []  # Store full paths

        input_path = Path(self.input_dir_var.get())
        if not input_path.exists():
            self._log("⚠️ Eingabe-Ordner existiert nicht")
            return

        # Find all audio files recursively
        audio_extensions = ['*.m4a', '*.opus', '*.wav', '*.mp3', '*.flac', '*.ogg']
        for ext in audio_extensions:
            self.audio_files.extend(input_path.rglob(ext))

        self.audio_files.sort()

        for audio_file in self.audio_files:
            # Display relative path for better readability
            relative_path = audio_file.relative_to(input_path)
            display_name = f"{relative_path} ({audio_file.stat().st_size / 1024 / 1024:.1f} MB)"
            self.file_listbox.insert(tk.END, display_name)

        self._log(f"✓ {len(self.audio_files)} Audio-Dateien gefunden")

    def _select_all_files(self):
        """Select all audio files in listbox"""
        self.file_listbox.selection_set(0, tk.END)

    def _start_transcription(self):
        """Start transcription in background thread"""
        # Validate inputs
        output_dir = Path(self.output_dir_var.get())

        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warnung", "Bitte wähle mindestens eine Audio-Datei aus")
            return

        if not hasattr(self, 'audio_files') or not self.audio_files:
            messagebox.showerror("Fehler", "Keine Audio-Dateien gefunden. Klicke auf 'Dateien aktualisieren'")
            return

        selected_files = [self.audio_files[i] for i in selected_indices]

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Disable start button, enable stop
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.test_button.config(state=tk.DISABLED)
        self.is_processing = True

        # Collect settings
        settings = {
            'output_dir': output_dir,
            'memory_dir': self.memory_dir,
            'audio_files': selected_files,
            'model': self.model_var.get(),
            'language': self.language_var.get(),
            'confidence_threshold': self.confidence_var.get(),
            'enable_emotion': self.emotion_var.get(),
            'enable_prosody': self.prosody_var.get(),
            'enable_memory': self.memory_var.get(),
            'use_intelligent_pipeline': self.intelligent_pipeline_var.get()
        }

        self._log(f"\n{'='*60}")
        self._log(f"🚀 Starte Transkription von {len(selected_files)} Datei(en)")
        self._log(f"{'='*60}\n")

        # Start processing thread
        self.processing_thread = threading.Thread(
            target=self._process_transcriptions,
            args=(settings,),
            daemon=True
        )
        self.processing_thread.start()

    def _run_quick_test(self):
        """Run quick test transcription on first audio file"""
        input_dir = Path(self.input_dir_var.get())

        if not input_dir.exists():
            messagebox.showerror("Fehler", "Eingabe-Ordner existiert nicht")
            return

        # Find first audio file
        audio_files = (
            list(input_dir.glob("*.m4a")) +
            list(input_dir.glob("*.opus")) +
            list(input_dir.glob("*.wav")) +
            list(input_dir.glob("*.mp3"))
        )

        if not audio_files:
            messagebox.showwarning("Keine Dateien", "Keine Audio-Dateien im Eingabe-Ordner gefunden")
            return

        audio_file = audio_files[0]

        # Disable buttons during test
        self.test_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.DISABLED)

        self._log(f"\n{'='*60}")
        self._log("🧪 QUICK TEST TRANSKRIPTION")
        self._log(f"{'='*60}")
        self._log(f"📂 Datei: {audio_file.name}")
        self._log(f"📊 Größe: {audio_file.stat().st_size / 1024 / 1024:.1f} MB\n")

        # Start test in background thread
        test_thread = threading.Thread(
            target=self._run_quick_test_worker,
            args=(audio_file,),
            daemon=True
        )
        test_thread.start()

    def _run_quick_test_worker(self, audio_file: Path):
        """Worker thread for quick test transcription"""
        import time

        try:
            # Get settings
            use_intelligent = self.intelligent_pipeline_var.get()
            manual_model = self.model_var.get()
            language = self.language_var.get()

            if use_intelligent:
                self.progress_queue.put(('log', "🤖 Intelligente Pipeline aktiviert"))
                self.progress_queue.put(('log', "🔍 Analysiere Audio-Qualität..."))

                start_time = time.time()
                quality_metrics = self.quality_analyzer.analyze_audio_file(str(audio_file))
                analysis_time = time.time() - start_time
                quality_score = quality_metrics["quality_score"]

                self.progress_queue.put(('log', f"✅ Qualitäts-Analyse fertig ({analysis_time:.2f}s)"))
                self.progress_queue.put(('log', f"   📊 Qualität: {quality_score:.2f}"))
                self.progress_queue.put(('log', f"   📡 SNR: {quality_metrics['snr_db']:.1f} dB"))
                self.progress_queue.put(('log', f"   ⚡ Clipping: {quality_metrics['clipping_ratio']:.2%}"))
                self.progress_queue.put(('log', f"   🔇 Silence: {quality_metrics['silence_ratio']:.2%}"))
                self.progress_queue.put(('log', f"   ⏱️  Dauer: {quality_metrics['duration']:.1f}s\n"))

                # Model selection
                if quality_score < 0.4:
                    optimal_model = "large"
                    self.progress_queue.put(('log', "🎯 Niedrige Qualität → large Modell + aggressives Preprocessing"))
                elif quality_score < 0.6:
                    optimal_model = "medium"
                    self.progress_queue.put(('log', "🎯 Mittlere Qualität → medium Modell + moderates Preprocessing"))
                elif quality_score < 0.8:
                    optimal_model = "medium"
                    self.progress_queue.put(('log', "🎯 Gute Qualität → medium Modell + leichtes Preprocessing"))
                else:
                    optimal_model = "small"
                    self.progress_queue.put(('log', "🎯 Sehr gute Qualität → small Modell (schneller)"))
            else:
                self.progress_queue.put(('log', f"⚙️  Manuelle Einstellungen: {manual_model} Modell"))
                optimal_model = manual_model
                quality_score = None

            self.progress_queue.put(('log', f"\n🎤 Transkribiere mit {optimal_model} Modell..."))
            self.progress_queue.put(('log', "⏳ Dies kann einige Minuten dauern...\n"))

            start_time = time.time()
            result = v4.transcribe_with_whisper(
                str(audio_file),
                model_size=optimal_model,
                language=language,
                use_intelligent_pipeline=use_intelligent,
                quality_score=quality_score,
                quality_analyzer=self.quality_analyzer if use_intelligent else None,
                audio_preprocessor=self.audio_preprocessor if use_intelligent else None,
                extract_prosody=True  # Always extract for quick test
            )
            transcription_time = time.time() - start_time

            self.progress_queue.put(('log', f"✅ Transkription fertig!"))
            self.progress_queue.put(('log', f"⏱️  Zeit: {transcription_time:.1f}s ({transcription_time/60:.1f} min)"))
            self.progress_queue.put(('log', f"📝 Text-Länge: {len(result['text'])} Zeichen"))
            self.progress_queue.put(('log', f"📊 Segmente: {len(result.get('segments', []))}\n"))

            # Show first 500 characters
            text_preview = result['text'][:500]
            self.progress_queue.put(('log', "📄 Erste 500 Zeichen:"))
            self.progress_queue.put(('log', "-" * 50))
            self.progress_queue.put(('log', text_preview))
            if len(result['text']) > 500:
                self.progress_queue.put(('log', "..."))
            self.progress_queue.put(('log', "-" * 50))

            # Save to file
            output_dir = Path(self.output_dir_var.get())
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"quick_test_{audio_file.stem}.txt"
            output_file.write_text(result['text'], encoding='utf-8')

            self.progress_queue.put(('log', f"\n💾 Gespeichert: {output_file}"))

            if use_intelligent and quality_score is not None:
                audio_duration = quality_metrics['duration']
                rtf = (transcription_time + analysis_time) / audio_duration
                self.progress_queue.put(('log', f"📊 Real-Time Factor: {rtf:.2f}x"))

            self.progress_queue.put(('log', f"\n{'='*60}"))
            self.progress_queue.put(('log', "✅ QUICK TEST ABGESCHLOSSEN"))
            self.progress_queue.put(('log', f"{'='*60}\n"))

        except Exception as e:
            logger.error(f"Quick test error: {e}")
            self.progress_queue.put(('log', f"❌ Fehler: {e}"))

        finally:
            # Re-enable buttons
            self.progress_queue.put(('enable_buttons', None))

    def _run_prosody_test(self):
        """Run prosody pipeline test on first 30 seconds of first audio file"""
        input_dir = Path(self.input_dir_var.get())

        if not input_dir.exists():
            messagebox.showerror("Fehler", "Eingabe-Ordner existiert nicht")
            return

        # Find first audio file recursively
        audio_files = []
        for ext in ['*.m4a', '*.opus', '*.wav', '*.mp3', '*.flac']:
            audio_files.extend(list(input_dir.rglob(ext)))

        if not audio_files:
            messagebox.showwarning("Keine Dateien", "Keine Audio-Dateien im Eingabe-Ordner gefunden")
            return

        audio_file = sorted(audio_files)[0]

        # Disable buttons during test
        self.prosody_test_button.config(state=tk.DISABLED)
        self.test_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.DISABLED)

        self._log(f"\n{'='*60}")
        self._log("🎵 PROSODY PIPELINE TEST (30 Sekunden)")
        self._log(f"{'='*60}")
        self._log(f"📂 Datei: {audio_file.name}")
        self._log(f"📊 Größe: {audio_file.stat().st_size / 1024 / 1024:.1f} MB\n")

        # Start test in background thread
        test_thread = threading.Thread(
            target=self._run_prosody_test_worker,
            args=(audio_file,),
            daemon=True
        )
        test_thread.start()

    def _run_prosody_test_worker(self, audio_file: Path):
        """Worker thread for prosody test using test_prosody_pipeline.py"""
        import time
        import librosa
        import soundfile as sf
        import tempfile

        try:
            duration_seconds = 30
            self.progress_queue.put(('log', f"⏱️  Extrahiere erste {duration_seconds} Sekunden...\n"))

            # Extract first 30 seconds
            audio, sr = librosa.load(str(audio_file), sr=16000, duration=duration_seconds)

            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_path = tmp_file.name
                sf.write(tmp_path, audio, sr)

            # Step 1: Quality Analysis
            self.progress_queue.put(('log', "🔍 STEP 1: Audio-Qualitätsanalyse..."))
            quality_metrics = self.quality_analyzer.analyze_audio_file(tmp_path)
            quality_score = quality_metrics['quality_score']

            self.progress_queue.put(('log', f"   Quality Score: {quality_score:.2f}"))
            self.progress_queue.put(('log', f"   SNR: {quality_metrics['snr_db']:.1f} dB"))
            self.progress_queue.put(('log', f"   Clipping: {quality_metrics['clipping_ratio']:.1%}"))
            self.progress_queue.put(('log', f"   Silence: {quality_metrics['silence_ratio']:.1%}\n"))

            # Step 2: Transcription with Prosody
            self.progress_queue.put(('log', "🎤 STEP 2: Whisper Transkription + Prosodieextraktion..."))

            start_time = time.time()
            result = v4.transcribe_with_whisper(
                tmp_path,
                model_size='small',
                language='de',
                use_intelligent_pipeline=False,
                extract_prosody=True
            )
            transcription_time = time.time() - start_time

            self.progress_queue.put(('log', f"   ✅ Transkription fertig in {transcription_time:.1f}s"))
            self.progress_queue.put(('log', f"   Text-Länge: {len(result['text'])} Zeichen"))
            self.progress_queue.put(('log', f"   Segmente: {len(result.get('segments', []))}"))
            self.progress_queue.put(('log', f"   Confidence: {result['confidence_scores']['overall_confidence']:.1%}\n"))

            # Step 3: Prosody Results
            prosody_features = result.get('prosody_features', [])
            prosody_baseline = result.get('prosody_baseline', None)

            if prosody_features:
                self.progress_queue.put(('log', "🎵 STEP 3: Prosodieanalyse-Ergebnisse"))
                self.progress_queue.put(('log', f"   Segmente mit Prosody: {len(prosody_features)}"))

                if prosody_baseline:
                    self.progress_queue.put(('log', f"\n   📊 Baseline:"))
                    self.progress_queue.put(('log', f"      Tempo: {prosody_baseline['tempo_wpm_mean']:.1f} WPM"))
                    self.progress_queue.put(('log', f"      Tonhöhe: {prosody_baseline['pitch_mean_hz']:.1f} Hz"))
                    self.progress_queue.put(('log', f"      Energie: {prosody_baseline['energy_rms_mean']:.4f}"))

                # Show first segment
                if len(prosody_features) > 0:
                    first = prosody_features[0]
                    self.progress_queue.put(('log', f"\n   🔬 Erstes Segment Beispiel:"))
                    self.progress_queue.put(('log', f"      Zeit: {first['start_time']:.1f}s - {first['end_time']:.1f}s"))
                    self.progress_queue.put(('log', f"      Tempo: {first.get('tempo_wpm', 0):.1f} WPM ({first.get('tempo_deviation_pct', 0):+.1f}%)"))
                    self.progress_queue.put(('log', f"      Tonhöhe: {first.get('pitch_mean_hz', 0):.1f} Hz ({first.get('pitch_deviation_pct', 0):+.1f}%)"))
                    self.progress_queue.put(('log', f"      Energie: {first.get('energy_rms', 0):.4f} ({first.get('energy_deviation_pct', 0):+.1f}%)\n"))

            # Step 4: Generate Outputs
            self.progress_queue.put(('log', "📝 STEP 4: Generiere Ausgaben..."))

            output_base = Path(self.output_dir_var.get()) / f"prosody_test_{audio_file.stem}"
            output_base.parent.mkdir(exist_ok=True)

            files = self.output_formatter.format_transcript(
                result,
                audio_file.name,
                output_base,
                include_prosody_markers=True
            )

            self.progress_queue.put(('log', f"   ✅ Ausgaben erstellt:"))
            self.progress_queue.put(('log', f"      📄 Markdown: {files['markdown'].name}"))
            self.progress_queue.put(('log', f"      📊 JSON: {files['json'].name}\n"))

            # Show markdown preview
            self.progress_queue.put(('log', "📄 Markdown Vorschau (erste 400 Zeichen):"))
            self.progress_queue.put(('log', "-" * 50))
            with open(files['markdown'], 'r', encoding='utf-8') as f:
                content = f.read()
                self.progress_queue.put(('log', content[:400] + "..."))
            self.progress_queue.put(('log', "-" * 50))

            # Cleanup
            Path(tmp_path).unlink(missing_ok=True)

            self.progress_queue.put(('log', f"\n{'='*60}"))
            self.progress_queue.put(('log', "✅ PROSODY TEST ABGESCHLOSSEN"))
            self.progress_queue.put(('log', f"{'='*60}\n"))

        except Exception as e:
            logger.error(f"Prosody test error: {e}", exc_info=True)
            self.progress_queue.put(('log', f"❌ Fehler: {e}"))

        finally:
            # Re-enable buttons
            self.progress_queue.put(('enable_buttons', None))

    def _stop_transcription(self):
        """Stop transcription"""
        self.is_processing = False
        self._log("⏹ Stoppe Verarbeitung...")

    def _process_transcriptions(self, settings: Dict[str, Any]):
        """Process transcriptions (runs in background thread)"""
        try:
            audio_files = settings['audio_files']
            total_files = len(audio_files)
            processed_files = 0

            self.progress_queue.put(('status', f"Verarbeite {total_files} Datei(en)..."))

            # Process each audio file
            for audio_file in audio_files:
                if not self.is_processing:
                    break

                self.progress_queue.put(('log', f"\n🎤 {audio_file.name} ({audio_file.stat().st_size / 1024 / 1024:.1f} MB)"))

                try:
                    # Intelligent Pipeline: Analyze quality first
                    use_intelligent = settings.get('use_intelligent_pipeline', False)
                    optimal_model = settings['model']
                    quality_score = None

                    if use_intelligent:
                        self.progress_queue.put(('log', f"    🔍 Analysiere Audio-Qualität..."))
                        quality_metrics = self.quality_analyzer.analyze_audio_file(str(audio_file))
                        quality_score = quality_metrics["quality_score"]

                        self.progress_queue.put(('log',
                            f"    📊 Qualität: {quality_score:.2f} | "
                            f"SNR: {quality_metrics['snr_db']:.1f}dB | "
                            f"Clipping: {quality_metrics['clipping_ratio']:.2%}"
                        ))

                        # Select optimal model based on quality
                        if quality_score < 0.4:
                            optimal_model = "large"
                            self.progress_queue.put(('log', "    🎯 Niedrige Qualität → large Modell + aggressives Preprocessing"))
                        elif quality_score < 0.6:
                            optimal_model = "medium"
                            self.progress_queue.put(('log', "    🎯 Mittlere Qualität → medium Modell + moderates Preprocessing"))
                        elif quality_score < 0.8:
                            optimal_model = "medium"
                            self.progress_queue.put(('log', "    🎯 Gute Qualität → medium Modell ohne Preprocessing"))
                        else:
                            optimal_model = "small"
                            self.progress_queue.put(('log', "    🎯 Sehr gute Qualität → small Modell (schneller)"))

                    # Transcribe
                    self.progress_queue.put(('log', f"    🎤 Transkribiere mit {optimal_model} Modell..."))

                    result = v4.transcribe_with_whisper(
                        str(audio_file),
                        model_size=optimal_model,
                        language=settings['language'],
                        use_intelligent_pipeline=use_intelligent,
                        quality_score=quality_score,
                        quality_analyzer=self.quality_analyzer if use_intelligent else None,
                        audio_preprocessor=self.audio_preprocessor if use_intelligent else None,
                        extract_prosody=settings.get('enable_prosody', False)
                    )

                    # Analyze emotion if enabled
                    emotion_data = None
                    if settings['enable_emotion']:
                        analyzer = v4.EmotionalAnalyzer(
                            confidence_threshold=settings['confidence_threshold']
                        )
                        emotion_data = analyzer.analyze_emotion(
                            result['text'],
                            audio_path=str(audio_file)
                        )

                    # Mark low confidence
                    marked_text = v4.mark_low_confidence_segments(result)

                    # Save transcript
                    # Extract speaker from folder structure or use filename
                    speaker = audio_file.parent.name if audio_file.parent.name != Path(self.input_dir_var.get()).name else "Unknown"
                    output_filename = f"{audio_file.stem}_transkript.md"
                    output_path = settings['output_dir'] / output_filename

                    self._save_transcript(
                        output_path,
                        audio_file,
                        speaker,
                        marked_text,
                        result,
                        emotion_data
                    )

                    # Update memory if enabled
                    if settings['enable_memory'] and emotion_data:
                        from build_memory_from_transcripts import update_speaker_memory
                        update_speaker_memory(
                            speaker,
                            {'text': result['text'], 'emotion': emotion_data},
                            settings['memory_dir']
                        )

                    processed_files += 1
                    progress = (processed_files / total_files) * 100
                    self.progress_queue.put(('progress', progress))

                    # Check confidence
                    overall_conf = result['confidence_scores']['overall_confidence']
                    if overall_conf < settings['confidence_threshold']:
                        self.progress_queue.put(('log', f"    ⚠️ Niedrige Confidence: {overall_conf:.2f}"))
                    else:
                        self.progress_queue.put(('log', f"    ✓ Confidence: {overall_conf:.2f}"))

                except Exception as e:
                    self.progress_queue.put(('log', f"    ❌ Fehler: {e}"))

            # Done
            if self.is_processing:
                self.progress_queue.put(('status', f"✓ Fertig! {processed_files}/{total_files} Dateien verarbeitet"))
                self.progress_queue.put(('log', f"\n✓ Verarbeitung abgeschlossen"))
            else:
                self.progress_queue.put(('status', "Verarbeitung gestoppt"))

        except Exception as e:
            self.progress_queue.put(('log', f"\n❌ Fehler: {e}"))
            self.progress_queue.put(('status', "Fehler aufgetreten"))

        finally:
            self.progress_queue.put(('done', None))

    def _save_transcript(self,
                        output_path: Path,
                        audio_file: Path,
                        speaker: str,
                        text: str,
                        result: Dict[str, Any],
                        emotion_data: Optional[Dict[str, Any]]):
        """Save transcript in therapeutic format"""

        # Check if prosody features are available
        has_prosody = (
            'prosody_features' in result and
            result['prosody_features'] and
            len(result['prosody_features']) > 0
        )

        if has_prosody:
            # Use new OutputFormatter for annotated Markdown + JSON sidecar
            try:
                # Remove .md extension from output_path for base path
                base_output_path = output_path.with_suffix('')

                files = self.output_formatter.format_transcript(
                    result,
                    audio_file.name,
                    base_output_path,
                    include_prosody_markers=True
                )

                logger.info(f"✅ Saved annotated transcript with prosody:")
                logger.info(f"   - Markdown: {files['markdown']}")
                logger.info(f"   - JSON: {files['json']}")

            except Exception as e:
                logger.error(f"Error using OutputFormatter: {e}")
                logger.info("Falling back to legacy format...")
                self._save_transcript_legacy(output_path, audio_file, speaker, text, result, emotion_data)

        else:
            # Use legacy format (backward compatibility)
            self._save_transcript_legacy(output_path, audio_file, speaker, text, result, emotion_data)

    def _save_transcript_legacy(self,
                        output_path: Path,
                        audio_file: Path,
                        speaker: str,
                        text: str,
                        result: Dict[str, Any],
                        emotion_data: Optional[Dict[str, Any]]):
        """Legacy transcript format (pre-prosody)"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# Therapeutisches Transkript\n\n")
            f.write(f"**Sprecher:** {speaker}\n")
            f.write(f"**Original-Datei:** {audio_file.name}\n")
            f.write(f"**Verarbeitet am:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Confidence:** {result['confidence_scores']['overall_confidence']:.2f}\n")

            if emotion_data:
                f.write(f"**Dominante Emotion:** {emotion_data.get('emotion', 'neutral')}\n")
                f.write(f"**Emotionale Valenz:** {emotion_data.get('valence', 0.0):.2f}\n")

                if 'prosody' in emotion_data and emotion_data['prosody']:
                    f.write(f"\n## Prosody-Merkmale\n")
                    prosody = emotion_data['prosody']
                    if 'pitch' in prosody:
                        f.write(f"- **Pitch:** {prosody['pitch'].get('mean', 0):.1f} Hz (±{prosody['pitch'].get('std', 0):.1f})\n")
                    if 'tempo' in prosody:
                        f.write(f"- **Tempo:** {prosody['tempo'].get('bpm', 0):.0f} BPM\n")
                        f.write(f"- **Sprechrate:** {prosody['tempo'].get('speech_rate', 0):.1f} Silben/Sek\n")
                    if 'energy' in prosody:
                        f.write(f"- **Energie:** {prosody['energy'].get('mean', 0):.3f}\n")

            # Low confidence warnings
            low_conf = result['confidence_scores']['low_confidence_segments']
            if low_conf:
                f.write(f"\n## ⚠️ Qualitäts-Hinweise\n")
                f.write(f"{len(low_conf)} Segment(e) mit niedriger Confidence erkannt.\n")
                f.write(f"Diese sind im Text mit [UNSICHER:score] markiert.\n")

            f.write(f"\n## Transkription\n\n")
            f.write(text)

    def _check_progress_queue(self):
        """Check progress queue and update GUI"""
        try:
            while True:
                msg_type, msg_data = self.progress_queue.get_nowait()

                if msg_type == 'status':
                    self.status_label.config(text=msg_data)
                elif msg_type == 'progress':
                    self.progress_var.set(msg_data)
                elif msg_type == 'log':
                    self._log(msg_data)
                elif msg_type == 'done':
                    self.start_button.config(state=tk.NORMAL)
                    self.stop_button.config(state=tk.DISABLED)
                    self.is_processing = False
                elif msg_type == 'enable_buttons':
                    self.start_button.config(state=tk.NORMAL)
                    self.test_button.config(state=tk.NORMAL)
                    self.prosody_test_button.config(state=tk.NORMAL)

        except queue.Empty:
            pass

        # Schedule next check
        self.root.after(100, self._check_progress_queue)

    def _log(self, message: str):
        """Add message to log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)


def main():
    """Main entry point"""
    root = tk.Tk()

    # Set theme
    style = ttk.Style()
    available_themes = style.theme_names()
    if 'clam' in available_themes:
        style.theme_use('clam')

    app = SemanticVoiceTranscriberGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
