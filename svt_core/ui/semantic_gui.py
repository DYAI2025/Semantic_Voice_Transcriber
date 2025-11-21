#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Super Semantic GUI - Interaktive Oberfläche für die Magie ✨
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from pathlib import Path
from datetime import datetime
import logging
from super_semantic_processor import SuperSemanticProcessor

# Vordefinierte Marker-Sets und ihre Ordnernamen. Passen Sie die Pfade bei
# Bedarf an Ihre lokale Marker-Struktur an.
MARKER_SET_PATHS = {
    "All_Markers": "ALL_NEWMARKER01",
    "Meta_Message": "META_MESSAGE",
    "Relationship_Patterns": "RELATIONSHIP_PATTERNS",
    "Fraud": "FRAUD",
    "Trauma": "TRAUMA",
    "Love": "LOVE",
    "Authenticy": "AUTHENTICITY",
}

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SuperSemanticGUI:
    """GUI für den Super Semantic Processor"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🌟 Super Semantic Processor - Chat-Magie")
        self.root.geometry("900x700")
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Variablen
        self.whatsapp_path = tk.StringVar()
        self.transcript_path = tk.StringVar()
        self.output_path = tk.StringVar(value="super_semantic_output.json")
        self.marker_yaml = tk.StringVar()
        self.marker_focus = tk.StringVar(value=list(MARKER_SET_PATHS.keys())[0])
        self.processing = False
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Erstelle GUI-Elemente"""
        
        # Header
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.grid(row=0, column=0, sticky="ew")
        
        title = ttk.Label(
            header_frame, 
            text="🌟 Super Semantic Processor", 
            font=('Arial', 20, 'bold')
        )
        title.pack()
        
        subtitle = ttk.Label(
            header_frame,
            text="Verwandle deine Chats in semantische Kunstwerke",
            font=('Arial', 12)
        )
        subtitle.pack()
        
        # Hauptbereich
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=1, column=0, sticky="nsew")
        
        # Input-Sektion
        input_frame = ttk.LabelFrame(main_frame, text="📥 Eingabe-Dateien", padding="10")
        input_frame.pack(fill="x", pady=10)
        
        # WhatsApp Export
        wa_frame = ttk.Frame(input_frame)
        wa_frame.pack(fill="x", pady=5)
        
        ttk.Label(wa_frame, text="WhatsApp-Export:").pack(side="left", padx=5)
        ttk.Entry(wa_frame, textvariable=self.whatsapp_path, width=50).pack(side="left", padx=5)
        ttk.Button(
            wa_frame, 
            text="📁 Durchsuchen",
            command=self._browse_whatsapp
        ).pack(side="left")
        
        # Transkript-Ordner
        trans_frame = ttk.Frame(input_frame)
        trans_frame.pack(fill="x", pady=5)
        
        ttk.Label(trans_frame, text="Transkript-Ordner:").pack(side="left", padx=5)
        ttk.Entry(trans_frame, textvariable=self.transcript_path, width=50).pack(side="left", padx=5)
        ttk.Button(
            trans_frame, 
            text="📁 Durchsuchen",
            command=self._browse_transcripts
        ).pack(side="left")
        
        # Output-Sektion
        output_frame = ttk.LabelFrame(main_frame, text="💾 Ausgabe", padding="10")
        output_frame.pack(fill="x", pady=10)
        
        out_frame = ttk.Frame(output_frame)
        out_frame.pack(fill="x", pady=5)
        
        ttk.Label(out_frame, text="Ausgabe-Datei:").pack(side="left", padx=5)
        ttk.Entry(out_frame, textvariable=self.output_path, width=50).pack(side="left", padx=5)
        ttk.Button(
            out_frame, 
            text="📁 Speichern als",
            command=self._browse_output
        ).pack(side="left")
        
        # Optionen
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ Optionen", padding="10")
        options_frame.pack(fill="x", pady=10)

        self.use_markers = tk.BooleanVar(value=True)
        self.use_emotion = tk.BooleanVar(value=True)
        self.use_cosd = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(
            options_frame, 
            text="🏷️ FRAUSAR Marker verwenden",
            variable=self.use_markers
        ).pack(anchor="w")
        
        ttk.Checkbutton(
            options_frame, 
            text="🎭 Emotionale Analyse",
            variable=self.use_emotion
        ).pack(anchor="w")
        
        ttk.Checkbutton(
            options_frame,
            text="🌊 CoSD/MARSAP Drift-Analyse",
            variable=self.use_cosd
        ).pack(anchor="w")

        # Analyse-Fokus
        focus_frame = ttk.Frame(options_frame)
        focus_frame.pack(fill="x", pady=5)
        ttk.Label(focus_frame, text="Analyse-Fokus:").pack(side="left", padx=5)
        focus_combo = ttk.Combobox(
            focus_frame,
            textvariable=self.marker_focus,
            values=list(MARKER_SET_PATHS.keys()),
            state="readonly",
            width=30,
        )
        focus_combo.pack(side="left", padx=5)
        focus_combo.current(0)

        # Benutzerdefinierte Marker YAML
        yaml_frame = ttk.Frame(options_frame)
        yaml_frame.pack(fill="x", pady=5)
        ttk.Label(yaml_frame, text="Marker YAML:").pack(side="left", padx=5)
        ttk.Entry(yaml_frame, textvariable=self.marker_yaml, width=40).pack(side="left", padx=5)
        ttk.Button(
            yaml_frame,
            text="📁 Datei wählen",
            command=self._browse_marker_yaml
        ).pack(side="left")
        
        # Prozess-Button
        self.process_btn = ttk.Button(
            main_frame,
            text="✨ Magie starten!",
            command=self._start_processing,
            style="Accent.TButton"
        )
        self.process_btn.pack(pady=20)
        
        # Progress
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill="x", pady=5)
        
        # Log-Bereich
        log_frame = ttk.LabelFrame(main_frame, text="📋 Verarbeitungs-Log", padding="10")
        log_frame.pack(fill="both", expand=True, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill="both", expand=True)
        
        # Status-Bar
        self.status_var = tk.StringVar(value="Bereit")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken")
        status_bar.grid(row=2, column=0, sticky="ew")
        
        # Grid-Konfiguration
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        
    def _browse_whatsapp(self):
        """WhatsApp-Export auswählen"""
        filename = filedialog.askopenfilename(
            title="WhatsApp-Export auswählen",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.whatsapp_path.set(filename)
            
    def _browse_transcripts(self):
        """Transkript-Ordner auswählen"""
        dirname = filedialog.askdirectory(title="Transkript-Ordner auswählen")
        if dirname:
            self.transcript_path.set(dirname)
            
    def _browse_output(self):
        """Ausgabe-Datei festlegen"""
        filename = filedialog.asksaveasfilename(
            title="Ausgabe-Datei speichern als",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.output_path.set(filename)

    def _browse_marker_yaml(self):
        """Marker YAML-Datei auswählen"""
        filename = filedialog.askopenfilename(
            title="Marker YAML auswählen",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        if filename:
            self.marker_yaml.set(filename)
            
    def _log(self, message: str):
        """Füge Nachricht zum Log hinzu"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def _start_processing(self):
        """Starte Verarbeitung in separatem Thread"""
        if self.processing:
            messagebox.showwarning("Warnung", "Verarbeitung läuft bereits!")
            return
            
        # Validierung
        if not self.whatsapp_path.get() and not self.transcript_path.get():
            messagebox.showerror("Fehler", "Bitte mindestens eine Eingabe-Quelle wählen!")
            return
            
        if not self.output_path.get():
            messagebox.showerror("Fehler", "Bitte Ausgabe-Datei festlegen!")
            return
            
        # Starte Thread
        thread = threading.Thread(target=self._process)
        thread.daemon = True
        thread.start()
        
    def _process(self):
        """Führe Verarbeitung durch"""
        self.processing = True
        self.process_btn.config(state="disabled")
        self.progress.start()
        self.status_var.set("Verarbeitung läuft...")
        
        try:
            self._log("🚀 Starte Super Semantic Processing...")
            
            # Erstelle Processor
            yaml_path = self.marker_yaml.get() if self.use_markers.get() else None
            focus = MARKER_SET_PATHS.get(self.marker_focus.get())
            processor = SuperSemanticProcessor(
                marker_yaml_path=yaml_path,
                marker_set=focus,
            )
            
            # Verarbeite WhatsApp wenn vorhanden
            if self.whatsapp_path.get():
                wa_path = Path(self.whatsapp_path.get())
                if wa_path.exists():
                    self._log(f"📱 Verarbeite WhatsApp-Export: {wa_path.name}")
                    result = processor.process_whatsapp_export(wa_path)
                    self._log(f"✅ {result['processed']} WhatsApp-Nachrichten verarbeitet")
                else:
                    self._log("⚠️ WhatsApp-Export nicht gefunden!")
                    
            # Verarbeite Transkripte wenn vorhanden
            if self.transcript_path.get():
                trans_path = Path(self.transcript_path.get())
                if trans_path.exists():
                    self._log(f"🎤 Verarbeite Transkripte aus: {trans_path.name}")
                    result = processor.process_audio_transcripts(trans_path)
                    self._log(f"✅ {result['processed']} Audio-Transkripte verarbeitet")
                else:
                    self._log("⚠️ Transkript-Ordner nicht gefunden!")
                    
            # Generiere Output
            self._log("🔮 Analysiere semantische Strukturen...")
            output_path = Path(self.output_path.get())
            
            # Führe Analysen durch
            processor.analyze_relationships()
            self._log(f"🔗 {len(processor.relationships)} Beziehungen gefunden")
            
            processor.identify_semantic_threads()
            self._log(f"🧵 {len(processor.semantic_threads)} semantische Fäden identifiziert")
            
            processor.calculate_emotional_arc()
            if processor.emotional_arc:
                self._log(f"📈 Emotionaler Verlauf: {processor.emotional_arc.overall_trend}")
            
            # Generiere Datei
            self._log("💾 Erstelle Super-Semantic-File...")
            result = processor.generate_super_semantic_file(output_path)
            
            self._log("✨ FERTIG! Magie vollbracht!")
            self._log(f"📄 Ausgabe gespeichert: {output_path}")
            self._log(f"📄 Zusammenfassung: {output_path.with_suffix('.summary.md')}")
            
            # Zeige Statistiken
            stats = result['analysis_summary']
            self._log("\n📊 STATISTIKEN:")
            self._log(f"  - Nachrichten: {result['metadata']['total_messages']}")
            self._log(f"  - Marker gefunden: {stats['marker_statistics']['total_markers_found']}")
            self._log(f"  - Emotionale Valenz: {stats['emotional_statistics']['average_valence']:.2f}")
            self._log(f"  - Semantische Fäden: {stats['thread_statistics']['total_threads']}")
            
            self.status_var.set("✅ Erfolgreich abgeschlossen!")
            
            # Frage ob öffnen
            if messagebox.askyesno("Erfolg", "Verarbeitung abgeschlossen!\n\nMöchten Sie die Zusammenfassung öffnen?"):
                import webbrowser
                webbrowser.open(str(output_path.with_suffix('.summary.md')))
                
        except Exception as e:
            self._log(f"❌ FEHLER: {str(e)}")
            logger.exception("Fehler bei Verarbeitung")
            self.status_var.set("❌ Fehler aufgetreten")
            messagebox.showerror("Fehler", f"Fehler bei Verarbeitung:\n{str(e)}")
            
        finally:
            self.processing = False
            self.process_btn.config(state="normal")
            self.progress.stop()
            
    def run(self):
        """Starte GUI"""
        self.root.mainloop()


def main():
    """Hauptfunktion"""
    gui = SuperSemanticGUI()
    gui.run()


if __name__ == "__main__":
    main() 