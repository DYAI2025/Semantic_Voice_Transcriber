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

        # Speaker selection frame
        speaker_frame = ttk.LabelFrame(self.root, text="Sprecher-Auswahl", padding="10")
        speaker_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)

        ttk.Label(speaker_frame, text="Zu verarbeitende Sprecher:").grid(row=0, column=0, sticky=tk.W, pady=5)

        self.speaker_listbox = tk.Listbox(speaker_frame, selectmode=tk.MULTIPLE, height=5, width=60)
        self.speaker_listbox.grid(row=1, column=0, columnspan=2, pady=5, padx=5)

        ttk.Button(speaker_frame, text="Sprecher aktualisieren", command=self._refresh_speakers).grid(row=2, column=0, pady=5)
        ttk.Button(speaker_frame, text="Alle auswählen", command=self._select_all_speakers).grid(row=2, column=1, pady=5)

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

        # Initial speaker refresh
        self._refresh_speakers()

    def _browse_input_dir(self):
        """Browse for input directory"""
        directory = filedialog.askdirectory(initialdir=self.input_dir)
        if directory:
            self.input_dir_var.set(directory)
            self._refresh_speakers()

    def _browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(initialdir=self.output_dir)
        if directory:
            self.output_dir_var.set(directory)

    def _refresh_speakers(self):
        """Refresh list of available speakers from input directory"""
        self.speaker_listbox.delete(0, tk.END)

        input_path = Path(self.input_dir_var.get())
        if not input_path.exists():
            self._log("⚠️ Eingabe-Ordner existiert nicht")
            return

        # Find all subdirectories (speakers)
        speakers = [d.name for d in input_path.iterdir() if d.is_dir()]
        speakers.sort()

        for speaker in speakers:
            self.speaker_listbox.insert(tk.END, speaker)

        # Select Zoe by default (priority)
        if "Zoe" in speakers or "zoe" in speakers:
            idx = speakers.index("Zoe") if "Zoe" in speakers else speakers.index("zoe")
            self.speaker_listbox.selection_set(idx)

        self._log(f"✓ {len(speakers)} Sprecher gefunden")

    def _select_all_speakers(self):
        """Select all speakers in listbox"""
        self.speaker_listbox.selection_set(0, tk.END)

    def _start_transcription(self):
        """Start transcription in background thread"""
        # Validate inputs
        input_dir = Path(self.input_dir_var.get())
        output_dir = Path(self.output_dir_var.get())

        if not input_dir.exists():
            messagebox.showerror("Fehler", "Eingabe-Ordner existiert nicht")
            return

        selected_indices = self.speaker_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warnung", "Bitte wähle mindestens einen Sprecher aus")
            return

        selected_speakers = [self.speaker_listbox.get(i) for i in selected_indices]

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Disable start button, enable stop
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_processing = True

        # Collect settings
        settings = {
            'input_dir': input_dir,
            'output_dir': output_dir,
            'memory_dir': self.memory_dir,
            'speakers': selected_speakers,
            'model': self.model_var.get(),
            'language': self.language_var.get(),
            'confidence_threshold': self.confidence_var.get(),
            'enable_emotion': self.emotion_var.get(),
            'enable_prosody': self.prosody_var.get(),
            'enable_memory': self.memory_var.get()
        }

        # Start processing thread
        self.processing_thread = threading.Thread(
            target=self._process_transcriptions,
            args=(settings,),
            daemon=True
        )
        self.processing_thread.start()

    def _stop_transcription(self):
        """Stop transcription"""
        self.is_processing = False
        self._log("⏹ Stoppe Verarbeitung...")

    def _process_transcriptions(self, settings: Dict[str, Any]):
        """Process transcriptions (runs in background thread)"""
        try:
            total_files = 0
            processed_files = 0

            # Count total files
            for speaker in settings['speakers']:
                speaker_dir = settings['input_dir'] / speaker
                audio_files = list(speaker_dir.glob("*.opus")) + list(speaker_dir.glob("*.wav"))
                total_files += len(audio_files)

            self.progress_queue.put(('status', f"Verarbeite {total_files} Dateien..."))

            # Process each speaker
            for speaker in settings['speakers']:
                if not self.is_processing:
                    break

                speaker_dir = settings['input_dir'] / speaker
                audio_files = list(speaker_dir.glob("*.opus")) + list(speaker_dir.glob("*.wav"))

                self.progress_queue.put(('log', f"\n📁 Verarbeite Sprecher: {speaker}"))

                for audio_file in audio_files:
                    if not self.is_processing:
                        break

                    self.progress_queue.put(('log', f"  🎤 {audio_file.name}"))

                    try:
                        # Transcribe
                        result = v4.transcribe_with_whisper(
                            str(audio_file),
                            model_size=settings['model'],
                            language=settings['language']
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
