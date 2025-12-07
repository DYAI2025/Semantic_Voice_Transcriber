#!/usr/bin/env python3
"""
Standalone GUI for Transcription Service with Speaker Detection

A lightweight, focused interface for testing transcription and speaker
separation capabilities without dependencies on the full SVT pipeline.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from pathlib import Path
from typing import Optional
import threading
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.transcription_service import (
    TranscriptionService,
    TranscriptionRequest,
    TranscriptionConfig,
    ModelProfile,
)


class TranscriptionGUI:
    """Standalone GUI for transcription service testing"""

    def __init__(self, root):
        self.root = root
        self.root.title("Transcription Service - Standalone GUI")
        self.root.geometry("1200x800")

        # Service instance
        self.config = TranscriptionConfig.from_env()
        self.service = None
        self.diarization_adapter = None

        # State
        self.audio_file = None
        self.transcription_result = None
        self.processing = False

        # Build UI
        self._create_menu()
        self._create_main_layout()
        self._create_status_bar()

        # Initialize service
        self._initialize_service()

    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Audio File...", command=self._select_audio_file)
        file_menu.add_separator()
        file_menu.add_command(label="Save Transcript...", command=self._save_transcript)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Configure HF Token", command=self._configure_hf_token)
        settings_menu.add_command(label="View Configuration", command=self._show_config)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _create_main_layout(self):
        """Create main application layout"""
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(2, weight=1)

        # Top section: File selection and settings
        self._create_file_section(main_container)

        # Middle section: Processing controls
        self._create_controls_section(main_container)

        # Bottom section: Results display
        self._create_results_section(main_container)

    def _create_file_section(self, parent):
        """Create file selection section"""
        file_frame = ttk.LabelFrame(parent, text="Audio File", padding="10")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)

        ttk.Label(file_frame, text="File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.file_entry = ttk.Entry(file_frame, width=60)
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(file_frame, text="Browse...", command=self._select_audio_file).grid(
            row=0, column=2, padx=5
        )

    def _create_controls_section(self, parent):
        """Create processing controls section"""
        controls_frame = ttk.LabelFrame(parent, text="Processing Options", padding="10")
        controls_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        controls_frame.columnconfigure(1, weight=1)

        # Model selection
        ttk.Label(controls_frame, text="Whisper Model:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5)
        )
        self.model_var = tk.StringVar(value="medium")
        model_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.model_var,
            values=["tiny", "base", "small", "medium", "large"],
            state="readonly",
            width=15,
        )
        model_combo.grid(row=0, column=1, sticky=tk.W, padx=5)

        # Language selection
        ttk.Label(controls_frame, text="Language:").grid(
            row=0, column=2, sticky=tk.W, padx=(20, 5)
        )
        self.language_var = tk.StringVar(value="de")
        lang_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.language_var,
            values=["de", "en", "fr", "es", "auto"],
            state="readonly",
            width=10,
        )
        lang_combo.grid(row=0, column=3, sticky=tk.W, padx=5)

        # Speaker diarization toggle
        self.diarization_var = tk.BooleanVar(value=True)
        diarization_check = ttk.Checkbutton(
            controls_frame,
            text="Enable Speaker Detection",
            variable=self.diarization_var,
            command=self._toggle_diarization,
        )
        diarization_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

        # Number of speakers
        ttk.Label(controls_frame, text="Number of Speakers:").grid(
            row=1, column=2, sticky=tk.W, padx=(20, 5), pady=(10, 0)
        )
        self.num_speakers_var = tk.StringVar(value="auto")
        num_speakers_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.num_speakers_var,
            values=["auto", "2", "3", "4", "5"],
            state="readonly",
            width=10,
        )
        num_speakers_combo.grid(row=1, column=3, sticky=tk.W, padx=5, pady=(10, 0))

        # Process button
        self.process_btn = ttk.Button(
            controls_frame,
            text="🎙️ Transcribe Audio",
            command=self._process_audio,
            style="Accent.TButton",
        )
        self.process_btn.grid(
            row=2, column=0, columnspan=4, pady=(15, 0), sticky=(tk.W, tk.E)
        )

        # Progress bar
        self.progress = ttk.Progressbar(
            controls_frame, mode="indeterminate", length=300
        )
        self.progress.grid(row=3, column=0, columnspan=4, pady=(10, 0), sticky=(tk.W, tk.E))

    def _create_results_section(self, parent):
        """Create results display section"""
        results_frame = ttk.LabelFrame(parent, text="Transcription Results", padding="10")
        results_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)

        # Metrics bar
        metrics_frame = ttk.Frame(results_frame)
        metrics_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        metrics_frame.columnconfigure(3, weight=1)

        ttk.Label(metrics_frame, text="Confidence:").grid(row=0, column=0, sticky=tk.W)
        self.confidence_label = ttk.Label(
            metrics_frame, text="N/A", font=("TkDefaultFont", 10, "bold")
        )
        self.confidence_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 20))

        ttk.Label(metrics_frame, text="Segments:").grid(row=0, column=2, sticky=tk.W)
        self.segments_label = ttk.Label(
            metrics_frame, text="0", font=("TkDefaultFont", 10, "bold")
        )
        self.segments_label.grid(row=0, column=3, sticky=tk.W, padx=(5, 20))

        ttk.Label(metrics_frame, text="Speakers:").grid(row=0, column=4, sticky=tk.W)
        self.speakers_label = ttk.Label(
            metrics_frame, text="N/A", font=("TkDefaultFont", 10, "bold")
        )
        self.speakers_label.grid(row=0, column=5, sticky=tk.W, padx=(5, 0))

        # Notebook for different views
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Tab 1: Full transcript
        transcript_tab = ttk.Frame(self.notebook)
        self.notebook.add(transcript_tab, text="Full Transcript")

        self.transcript_text = scrolledtext.ScrolledText(
            transcript_tab, wrap=tk.WORD, width=80, height=20, font=("Courier", 10)
        )
        self.transcript_text.pack(fill=tk.BOTH, expand=True)

        # Tab 2: Segments with speakers
        segments_tab = ttk.Frame(self.notebook)
        self.notebook.add(segments_tab, text="Segments (with Speakers)")

        # Create treeview for segments
        columns = ("Time", "Speaker", "Text", "Confidence")
        self.segments_tree = ttk.Treeview(
            segments_tab, columns=columns, show="headings", height=15
        )

        for col in columns:
            self.segments_tree.heading(col, text=col)

        self.segments_tree.column("Time", width=120, anchor=tk.W)
        self.segments_tree.column("Speaker", width=80, anchor=tk.CENTER)
        self.segments_tree.column("Text", width=600, anchor=tk.W)
        self.segments_tree.column("Confidence", width=100, anchor=tk.CENTER)

        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(
            segments_tab, orient=tk.VERTICAL, command=self.segments_tree.yview
        )
        self.segments_tree.configure(yscrollcommand=scrollbar.set)

        self.segments_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Tab 3: Quality report
        quality_tab = ttk.Frame(self.notebook)
        self.notebook.add(quality_tab, text="Quality Report")

        self.quality_text = scrolledtext.ScrolledText(
            quality_tab, wrap=tk.WORD, width=80, height=20, font=("Courier", 10)
        )
        self.quality_text.pack(fill=tk.BOTH, expand=True)

    def _create_status_bar(self):
        """Create status bar at bottom"""
        status_frame = ttk.Frame(self.root, relief=tk.SUNKEN)
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

        self.status_label = ttk.Label(status_frame, text="Ready", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Service status indicator
        self.service_status = ttk.Label(
            status_frame, text="⚫ Service Not Initialized", anchor=tk.E
        )
        self.service_status.pack(side=tk.RIGHT, padx=5)

    def _initialize_service(self):
        """Initialize transcription service"""
        try:
            self.service = TranscriptionService(self.config)
            self.service_status.config(text="🟢 Service Ready", foreground="green")
            self.status_label.config(text="Transcription service initialized successfully")
        except Exception as e:
            self.service_status.config(text="🔴 Service Error", foreground="red")
            self.status_label.config(text=f"Error initializing service: {e}")
            messagebox.showerror("Service Error", f"Failed to initialize service:\n{e}")

    def _toggle_diarization(self):
        """Toggle speaker diarization on/off"""
        if self.diarization_var.get():
            self._enable_diarization()
        else:
            self._disable_diarization()

    def _enable_diarization(self):
        """Enable speaker diarization"""
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            response = messagebox.askyesno(
                "HF Token Required",
                "Speaker detection requires a Hugging Face token.\n\n"
                "Do you want to configure it now?",
            )
            if response:
                self._configure_hf_token()
            else:
                self.diarization_var.set(False)
                return

        try:
            from svt_core.audio.diarization import SpeakerDiarizer

            class DiarizationAdapter:
                def __init__(self, hf_token):
                    self.diarizer = SpeakerDiarizer(hf_token=hf_token, device="cpu")

                def attach(self, raw_result, request):
                    try:
                        diarization = self.diarizer.diarize_audio(
                            str(request.audio_path),
                            num_speakers=self.num_speakers,
                        )

                        # Merge speaker labels with segments
                        for segment in raw_result.get("segments", []):
                            for spk_seg in diarization.get("segments", []):
                                if spk_seg["start"] <= segment["start"] < spk_seg["end"]:
                                    segment["speaker"] = spk_seg["speaker"]
                                    break

                        return diarization
                    except Exception as e:
                        print(f"Diarization error: {e}")
                        return None

            # Set num_speakers based on dropdown
            num_speakers = self.num_speakers_var.get()
            DiarizationAdapter.num_speakers = (
                num_speakers if num_speakers != "auto" else "auto"
            )

            self.diarization_adapter = DiarizationAdapter(hf_token)
            self.service = TranscriptionService(
                self.config, diarization_adapter=self.diarization_adapter
            )
            self.status_label.config(text="Speaker detection enabled")

        except ImportError as e:
            messagebox.showerror(
                "Missing Dependencies",
                f"Speaker detection requires pyannote.audio:\n{e}\n\n"
                "Install with: pip install pyannote.audio torch",
            )
            self.diarization_var.set(False)
        except Exception as e:
            messagebox.showerror("Diarization Error", f"Failed to enable diarization:\n{e}")
            self.diarization_var.set(False)

    def _disable_diarization(self):
        """Disable speaker diarization"""
        self.service = TranscriptionService(self.config)
        self.diarization_adapter = None
        self.status_label.config(text="Speaker detection disabled")

    def _select_audio_file(self):
        """Open file dialog to select audio file"""
        filetypes = (
            ("Audio Files", "*.opus *.m4a *.wav *.mp3 *.ogg"),
            ("All Files", "*.*"),
        )

        filename = filedialog.askopenfilename(
            title="Select Audio File",
            initialdir=self.config.input_dir,
            filetypes=filetypes,
        )

        if filename:
            self.audio_file = Path(filename)
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, str(self.audio_file))
            self.status_label.config(text=f"Selected: {self.audio_file.name}")

    def _process_audio(self):
        """Process audio file in background thread"""
        if not self.audio_file or not self.audio_file.exists():
            messagebox.showwarning("No File", "Please select an audio file first")
            return

        if self.processing:
            messagebox.showwarning("Processing", "Already processing. Please wait.")
            return

        # Start processing in background
        self.processing = True
        self.process_btn.config(state="disabled", text="Processing...")
        self.progress.start()
        self.status_label.config(text="Processing audio...")

        thread = threading.Thread(target=self._process_audio_thread, daemon=True)
        thread.start()

    def _process_audio_thread(self):
        """Background thread for audio processing"""
        try:
            # Create request
            request = TranscriptionRequest(
                audio_path=self.audio_file,
                language=self.language_var.get(),
                model_profile=ModelProfile(name=self.model_var.get()),
            )

            # Process
            response = self.service.transcribe(request)
            self.transcription_result = response

            # Update UI in main thread
            self.root.after(0, self._update_results, response)

        except Exception as e:
            self.root.after(0, self._show_error, str(e))
        finally:
            self.root.after(0, self._finish_processing)

    def _update_results(self, response):
        """Update UI with transcription results"""
        # Update metrics
        confidence = response.confidence_scores.get("overall_confidence", 0)
        self.confidence_label.config(
            text=f"{confidence:.1%}",
            foreground="green" if confidence > 0.8 else "orange" if confidence > 0.5 else "red",
        )

        total_segments = len(response.segments)
        self.segments_label.config(text=str(total_segments))

        # Count unique speakers
        speakers = set()
        for seg in response.segments:
            if "speaker" in seg and seg["speaker"]:
                speakers.add(seg["speaker"])

        if speakers:
            self.speakers_label.config(
                text=", ".join(sorted(speakers)), foreground="blue"
            )
        else:
            self.speakers_label.config(text="N/A", foreground="gray")

        # Update full transcript
        self.transcript_text.delete("1.0", tk.END)
        self.transcript_text.insert("1.0", response.text)

        # Update segments treeview
        self.segments_tree.delete(*self.segments_tree.get_children())
        for seg in response.segments:
            time_str = f"{seg['start']:.1f}s - {seg['end']:.1f}s"
            speaker = seg.get("speaker", "Unknown")
            text = seg.get("text", "").strip()
            conf = seg.get("confidence", 0)
            conf_str = f"{conf:.1%}" if conf else "N/A"

            # Color code by confidence
            tag = "high" if conf > 0.8 else "medium" if conf > 0.5 else "low"
            self.segments_tree.insert("", tk.END, values=(time_str, speaker, text, conf_str), tags=(tag,))

        # Configure tags for color coding
        self.segments_tree.tag_configure("high", foreground="green")
        self.segments_tree.tag_configure("medium", foreground="orange")
        self.segments_tree.tag_configure("low", foreground="red")

        # Update quality report
        self._update_quality_report(response)

        self.status_label.config(text="Transcription completed successfully")

    def _update_quality_report(self, response):
        """Generate and display quality report"""
        self.quality_text.delete("1.0", tk.END)

        report = []
        report.append("=" * 80)
        report.append("TRANSCRIPTION QUALITY REPORT")
        report.append("=" * 80)
        report.append("")

        # Overall metrics
        confidence_scores = response.confidence_scores
        report.append("OVERALL METRICS")
        report.append("-" * 80)
        report.append(f"Overall Confidence:      {confidence_scores['overall_confidence']:.1%}")
        report.append(f"Total Segments:          {confidence_scores['total_segments']}")
        report.append(
            f"Low Confidence Segments: {len(confidence_scores.get('low_confidence_segments', []))}"
        )
        report.append("")

        # Speaker information
        if response.extras and "diarization" in response.extras:
            diarization = response.extras["diarization"]
            if diarization:
                report.append("SPEAKER DETECTION")
                report.append("-" * 80)
                speakers = diarization.get("speakers", [])
                report.append(f"Speakers Detected:       {', '.join(speakers) if speakers else 'None'}")
                report.append(f"Total Segments:          {len(diarization.get('segments', []))}")
                report.append("")

        # Low confidence segments
        low_conf_segs = confidence_scores.get("low_confidence_segments", [])
        if low_conf_segs:
            report.append("LOW CONFIDENCE SEGMENTS")
            report.append("-" * 80)
            for seg in low_conf_segs[:10]:  # Show first 10
                report.append(
                    f"  [{seg['start']:.1f}s - {seg['end']:.1f}s] "
                    f"Confidence: {seg['confidence']:.1%}"
                )
                report.append(f"  Text: {seg['text']}")
                report.append("")
            if len(low_conf_segs) > 10:
                report.append(f"  ... and {len(low_conf_segs) - 10} more")
                report.append("")

        # Processing info
        report.append("PROCESSING INFORMATION")
        report.append("-" * 80)
        report.append(f"Model Used:              {self.model_var.get()}")
        report.append(f"Language:                {self.language_var.get()}")
        report.append(f"Speaker Detection:       {'Enabled' if self.diarization_var.get() else 'Disabled'}")
        report.append(f"Audio File:              {self.audio_file.name}")
        report.append(f"Timestamp:               {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        self.quality_text.insert("1.0", "\n".join(report))

    def _finish_processing(self):
        """Clean up after processing"""
        self.processing = False
        self.process_btn.config(state="normal", text="🎙️ Transcribe Audio")
        self.progress.stop()

    def _show_error(self, error_msg):
        """Show error message"""
        messagebox.showerror("Processing Error", f"Transcription failed:\n\n{error_msg}")
        self.status_label.config(text=f"Error: {error_msg}")

    def _save_transcript(self):
        """Save transcript to file"""
        if not self.transcription_result:
            messagebox.showwarning("No Transcript", "No transcript to save")
            return

        filename = filedialog.asksaveasfilename(
            title="Save Transcript",
            initialdir=self.config.output_dir,
            defaultextension=".txt",
            filetypes=(
                ("Text Files", "*.txt"),
                ("JSON Files", "*.json"),
                ("Markdown Files", "*.md"),
                ("All Files", "*.*"),
            ),
        )

        if filename:
            try:
                filepath = Path(filename)
                if filepath.suffix == ".json":
                    # Save as JSON
                    data = {
                        "text": self.transcription_result.text,
                        "segments": self.transcription_result.segments,
                        "confidence_scores": self.transcription_result.confidence_scores,
                        "extras": self.transcription_result.extras,
                    }
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    # Save as text/markdown
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(self.transcription_result.text)

                messagebox.showinfo("Saved", f"Transcript saved to:\n{filepath}")
                self.status_label.config(text=f"Saved to: {filepath.name}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save transcript:\n{e}")

    def _configure_hf_token(self):
        """Configure Hugging Face token"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Configure Hugging Face Token")
        dialog.geometry("500x250")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(
            dialog,
            text="Enter your Hugging Face token for speaker detection:",
            padding=10,
        ).pack()

        token_entry = ttk.Entry(dialog, width=60, show="*")
        token_entry.pack(padx=10, pady=10)

        # Show current token (masked)
        current_token = os.getenv("HF_TOKEN")
        if current_token:
            token_entry.insert(0, current_token)

        ttk.Label(
            dialog,
            text="Get your token at: https://huggingface.co/settings/tokens",
            foreground="blue",
            padding=5,
        ).pack()

        ttk.Label(
            dialog,
            text="Note: Token will be saved to .env file",
            font=("TkDefaultFont", 9, "italic"),
            padding=5,
        ).pack()

        def save_token():
            token = token_entry.get().strip()
            if token:
                # Save to .env file
                env_file = Path.cwd() / ".env"
                lines = []
                if env_file.exists():
                    with open(env_file, "r") as f:
                        lines = f.readlines()

                # Update or add HF_TOKEN
                found = False
                for i, line in enumerate(lines):
                    if line.startswith("HF_TOKEN="):
                        lines[i] = f"HF_TOKEN={token}\n"
                        found = True
                        break

                if not found:
                    lines.append(f"HF_TOKEN={token}\n")

                with open(env_file, "w") as f:
                    f.writelines(lines)

                os.environ["HF_TOKEN"] = token
                messagebox.showinfo("Success", "Hugging Face token saved successfully")
                dialog.destroy()
            else:
                messagebox.showwarning("Invalid Token", "Please enter a valid token")

        ttk.Button(dialog, text="Save Token", command=save_token).pack(pady=10)

    def _show_config(self):
        """Show current configuration"""
        config_text = f"""
Current Configuration:

Input Directory:  {self.config.input_dir}
Output Directory: {self.config.output_dir}
Log Directory:    {self.config.log_dir}
Cache Directory:  {self.config.cache_dir or 'Not set'}

Environment Variables:
HF_TOKEN:         {'Set' if os.getenv('HF_TOKEN') else 'Not set'}
SVT_BASE_PATH:    {os.getenv('SVT_BASE_PATH', 'Not set')}

Service Status:
Diarization:      {'Enabled' if self.diarization_adapter else 'Disabled'}
"""
        messagebox.showinfo("Configuration", config_text)

    def _show_about(self):
        """Show about dialog"""
        about_text = """
Transcription Service - Standalone GUI
Version 1.0.0

A lightweight interface for testing transcription and speaker
separation capabilities using OpenAI Whisper and pyannote.audio.

Features:
• Pure speech-to-text transcription
• Optional speaker detection and separation
• Confidence scoring per segment
• Quality metrics and reporting
• Multiple export formats

Maintained by: SVT Development Team
        """
        messagebox.showinfo("About", about_text)


def main():
    """Main entry point"""
    root = tk.Tk()

    # Set theme (if available)
    try:
        style = ttk.Style()
        style.theme_use("clam")  # Modern theme
    except:
        pass

    app = TranscriptionGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
