#!/usr/bin/env python3
"""
SVT Local - Simple GUI for Therapists
Therapy Session Transcription with Speaker Separation

Requirements:
    pip install PySimpleGUI openai-whisper pyannote.audio torch librosa ffmpeg-python python-docx reportlab

Usage:
    python svt_local_gui.py
"""

import PySimpleGUI as sg
import os
import sys
import json
import threading
from datetime import datetime
from pathlib import Path

# Try to import SVT modules (graceful fallback)
SVT_AVAILABLE = False
try:
    from svt_core.audio import SpeakerDiarizer, AudioPreprocessor
    SVT_AVAILABLE = True
    print("✓ SVT Core modules loaded")
except ImportError as e:
    print(f"⚠ SVT modules not available: {e}")
    print("  Run: pip install -e .")

class SVTLocalGUI:
    def __init__(self):
        self.transcriber = None
        self.diarizer = None
        self.analyzer = None
        self.current_file = None
        self.results = {}
        
    def load_models(self):
        """Load ML models in background"""
        try:
            self.transcriber = Transcriber(model="medium")
            self.diarizer = SpeakerDiarizer()
            return True, "Modelle geladen"
        except Exception as e:
            return False, f"Fehler: {str(e)}"
    
    def transcribe_audio(self, audio_path, progress_callback):
        """Run full transcription pipeline"""
        try:
            # Step 1: Transcription
            progress_callback("Transkription läuft...", 10)
            transcript = self.transcriber.transcribe(audio_path)
            
            # Step 2: Speaker Diarization
            progress_callback("Sprecher werden erkannt...", 40)
            speakers = self.diarizer.diarize(audio_path)
            
            # Step 3: Combine
            progress_callback("Verbinde Ergebnisse...", 70)
            combined = self.combine_transcript_speakers(transcript, speakers)
            
            # Step 4: Analysis
            progress_callback("Analysiere Inhalt...", 90)
            analysis = self.analyzer.analyze(combined)
            
            progress_callback("Fertig!", 100)
            return {
                "transcript": combined,
                "analysis": analysis,
                "speakers": speakers
            }
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    def combine_transcript_speakers(self, transcript, speakers):
        """Merge whisper transcript with speaker diarization"""
        combined = []
        for segment in transcript.get("segments", []):
            combined.append({
                "start": segment.get("start", 0),
                "end": segment.get("end", 0),
                "text": segment.get("text", ""),
                "speaker": self.guess_speaker(segment, speakers)
            })
        return combined
    
    def guess_speaker(self, segment, speakers):
        """Guess speaker based on timing"""
        mid_time = (segment.get("start", 0) + segment.get("end", 0)) / 2
        for spk in speakers.get("speakers", []):
            if spk.get("start", 0) <= mid_time <= spk.get("end", 0):
                return spk.get("label", "Unknown")
        return "Unknown"
    
    def create_ui(self):
        """Create PySimpleGUI interface"""
        sg.theme("LightGreen")
        
        # Layout
        layout = [
            [sg.Text("🎤 SVT Local - Therapie Transkription", font=("Arial", 18, "bold"), justification="center")],
            [sg.HorizontalSeparator()],
            
            [sg.Frame("Audio auswählen", [
                [sg.Input(key="-FILE-", size=(50, 1), enable_events=True), 
                 sg.FileBrowse("Durchsuchen...", file_types=(("Audio Files", "*.mp3 *.wav *.m4a *.ogg *.flac"),))],
                [sg.Button("▶ Transkription starten", key="-TRANSCRIBE-", size=(25, 2), button_color=("white", "#28a745"))]
            ])],
            
            [sg.Frame("Fortschritt", [
                [sg.ProgressBar(100, orientation="h", size=(50, 20), key="-PROGRESS-")],
                [sg.Text("", key="-STATUS-", size=(60, 1))]
            ])],
            
            [sg.HorizontalSeparator()],
            
            [sg.Frame("Ergebnisse", [
                [sg.TabGroup([[
                    sg.Tab("📝 Transkript", [[sg.Multiline(key="-TRANSCRIPT-", size=(70, 15), disabled=True)]]),
                    sg.Tab("👥 Sprecher", [[sg.Multiline(key="-SPEAKERS-", size=(70, 15), disabled=True)]]),
                    sg.Tab("🧠 Analyse", [[sg.Multiline(key="-ANALYSIS-", size=(70, 15), disabled=True)]]),
                ]])]
            ])],
            
            [sg.HorizontalSeparator()],
            
            [sg.Frame("Export", [
                [sg.Button("📄 PDF exportieren", key="-EXPORT-PDF-", size=(20, 1)),
                 sg.Button("📄 DOCX exportieren", key="-EXPORT-DOCX-", size=(20, 1)),
                 sg.Button("📄 JSON exportieren", key="-EXPORT-JSON-", size=(20, 1))],
                [sg.Input(key="-EXPORT-FOLDER-", size=(50, 1)), 
                 sg.FolderBrowse("Speicherort...", key="-EXPORT-BROWSE-")]
            ])],
            
            [sg.HorizontalSeparator()],
            
            [sg.Text("Status: Bereit | Modelle: Nicht geladen", key="-MODEL-STATUS-", font=("Arial", 10))],
            [sg.Button("⚙️ Modelle laden", key="-LOAD-MODELS-", size=(20, 1))]
        ]
        
        return sg.Window("SVT Local - Therapie Transkription", layout, finalize=True, size=(800, 700))
    
    def run(self):
        """Main event loop"""
        window, values = self.create_ui(), None
        
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, "Exit"):
                break
            
            # Load models
            if event == "-LOAD-MODELS-":
                window["-STATUS-"].update("Lade Modelle...")
                window["-PROGRESS-"].update(0)
                success, msg = self.load_models()
                if success:
                    window["-MODEL-STATUS-"].update("Status: Bereit | Modelle: Geladen")
                    window["-STATUS-"].update("✓ Modelle bereit")
                else:
                    window["-STATUS-"].update(f"✗ {msg}")
            
            # File selected
            if event == "-FILE-":
                self.current_file = values["-FILE-"]
                window["-STATUS-"].update(f"Datei: {os.path.basename(self.current_file)}")
            
            # Start transcription
            if event == "-TRANSCRIBE-":
                if not self.current_file or not os.path.exists(self.current_file):
                    window["-STATUS-"].update("✗ Bitte zuerst Audio-Datei auswählen")
                    continue
                if not self.transcriber:
                    window["-STATUS-"].update("✗ Bitte zuerst Modelle laden")
                    continue
                
                # Run in background
                window["-TRANSCRIBE-"].update(disabled=True)
                threading.Thread(target=self.transcribe_thread, args=(window, values), daemon=True).start()
            
            # Export handlers
            if event == "-EXPORT-PDF-":
                self.export_pdf(values)
            if event == "-EXPORT-DOCX-":
                self.export_docx(values)
            if event == "-EXPORT-JSON-":
                self.export_json(values)
        
        window.close()
    
    def transcribe_thread(self, window, values):
        """Run transcription in thread with progress updates"""
        try:
            self.results = self.transcribe_audio(
                self.current_file,
                lambda msg, prog: window.write_event_value("-PROGRESS-UPDATE-", (msg, prog))
            )
            
            # Update UI when done
            window.write_event_value("-TRANSCRIPT-DONE-", self.results)
            
        except Exception as e:
            window.write_event_value("-ERROR-", str(e))
    
    def export_pdf(self, values):
        """Export to PDF"""
        if not self.results:
            return
        # Implementation would use reportlab
        sg.popup("PDF Export", f"Ergebnisse in {values['-EXPORT-FOLDER-'] or 'current dir'} speichern")
    
    def export_docx(self, values):
        """Export to DOCX"""
        if not self.results:
            return
        sg.popup("DOCX Export", f"Ergebnisse in {values['-EXPORT-FOLDER-'] or 'current dir'} speichern")
    
    def export_json(self, values):
        """Export to JSON"""
        if not self.results:
            return
        folder = values["-EXPORT-FOLDER-"] or "."
        output = os.path.join(folder, f"svt_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(output, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        sg.popup("✓ JSON Export", f"Gespeichert: {output}")


if __name__ == "__main__":
    app = SVTLocalGUI()
    app.run()
