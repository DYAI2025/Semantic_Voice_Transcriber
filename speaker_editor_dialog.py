"""
Speaker Editor GUI Dialog
Allows users to edit speaker names and colors
"""

import tkinter as tk
from tkinter import colorchooser, messagebox, ttk
from typing import List, Dict, Callable
import sys
import os

# Add the project root to the path to import speaker_database
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class SpeakerEditorDialog(tk.Toplevel):
    """Dialog for editing speaker names and colors"""

    def __init__(self, parent, speakers: List[Dict], db, callback: Callable = None):
        """
        Initialize speaker editor

        Args:
            parent: Parent window
            speakers: List of speaker dicts with keys: speaker_id, name, color
            db: SpeakerDatabase instance (or similar interface)
            callback: Function to call when changes are saved
        """
        super().__init__(parent)
        self.title("Speaker bearbeiten")
        self.geometry("600x400")

        self.speakers = speakers
        self.db = db
        self.callback = callback

        self._create_widgets()

    def _create_widgets(self):
        """Create GUI elements"""
        # Header
        header = tk.Label(
            self,
            text="👥 Speaker bearbeiten",
            font=('Helvetica', 16, 'bold')
        )
        header.pack(pady=10)

        # Instructions
        instructions = tk.Label(
            self,
            text="Klicken Sie auf die Farbe um sie zu ändern",
            font=('Helvetica', 10)
        )
        instructions.pack(pady=5)

        # Create main frame with canvas and scrollbar
        main_frame = tk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Canvas for scrolling
        self.canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create entry for each speaker in the scrollable frame
        self.name_vars = []
        self.color_buttons = []

        for i, speaker in enumerate(self.speakers):
            frame = tk.Frame(self.scrollable_frame)
            frame.pack(fill='x', pady=5)

            # Speaker label
            label = tk.Label(
                frame,
                text=f"Speaker {i+1}:",
                width=10,
                anchor='w'
            )
            label.pack(side='left', padx=5)

            # Name entry
            name_var = tk.StringVar(value=speaker.get('name', f'Speaker {speaker.get("speaker_id", f" {i+1}")}'))
            self.name_vars.append(name_var)

            entry = tk.Entry(frame, textvariable=name_var, width=30)
            entry.pack(side='left', padx=5)

            # Color button
            color = speaker.get('color', '#4A90E2')
            color_btn = tk.Button(
                frame,
                text='   ',
                bg=color,
                width=3,
                command=lambda idx=i: self._pick_color(idx)
            )
            color_btn.pack(side='left', padx=5)
            self.color_buttons.append(color_btn)

        # Bind mousewheel to canvas for scrolling
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas.bind("<MouseWheel>", _on_mousewheel)

        # Buttons frame (not in scrollable area)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        # Save button
        save_btn = tk.Button(
            btn_frame,
            text="💾 Speichern",
            command=self._save_changes,
            bg='#27AE60',
            fg='white',
            font=('Helvetica', 10, 'bold'),
            padx=20,
            pady=5
        )
        save_btn.pack(side='left', padx=5)

        # Cancel button
        cancel_btn = tk.Button(
            btn_frame,
            text="❌ Abbrechen",
            command=self.destroy,
            bg='#E74C3C',
            fg='white',
            font=('Helvetica', 10, 'bold'),
            padx=20,
            pady=5
        )
        cancel_btn.pack(side='left', padx=5)

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if hasattr(self, 'canvas'):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _pick_color(self, speaker_index: int):
        """Open color picker for speaker"""
        current_color = self.speakers[speaker_index].get('color', '#4A90E2')

        color = colorchooser.askcolor(
            initialcolor=current_color,
            title="Farbe wählen"
        )

        if color[1]:  # User selected a color
            new_color = color[1]
            self.speakers[speaker_index]['color'] = new_color
            self.color_buttons[speaker_index].config(bg=new_color)

    def _save_changes(self):
        """Save changes to database"""
        try:
            for i, speaker in enumerate(self.speakers):
                new_name = self.name_vars[i].get().strip()
                new_color = speaker['color']

                if new_name:
                    # Update in database if available
                    if hasattr(self.db, 'update_speaker_name'):
                        self.db.update_speaker_name(speaker['speaker_id'], new_name)
                    if hasattr(self.db, 'update_speaker_color'):
                        self.db.update_speaker_color(speaker['speaker_id'], new_color)

                    # Update in-memory
                    speaker['name'] = new_name
                    speaker['color'] = new_color

            messagebox.showinfo(
                "Erfolg",
                "Änderungen wurden gespeichert!"
            )

            # Call callback if provided
            if self.callback:
                self.callback(self.speakers)

            self.destroy()

        except Exception as e:
            messagebox.showerror(
                "Fehler",
                f"Fehler beim Speichern: {e}"
            )

# Integration example
def open_speaker_editor(speakers: List[Dict], db=None):
    """Open speaker editor dialog"""
    root = tk.Tk()
    root.withdraw()  # Hide main window

    def on_save(updated_speakers):
        print("✅ Speakers updated:")
        for s in updated_speakers:
            print(f"  - {s['name']} ({s['color']})")

    dialog = SpeakerEditorDialog(root, speakers, db, callback=on_save)
    root.wait_window(dialog)
    root.destroy()

# Test with more speakers to demonstrate scrolling
if __name__ == "__main__":
    test_speakers = [
        {'speaker_id': 'SPEAKER_00', 'name': 'Dr. Schmidt', 'color': '#4A90E2'},
        {'speaker_id': 'SPEAKER_01', 'name': 'Patient A', 'color': '#7B68EE'},
        {'speaker_id': 'SPEAKER_02', 'name': 'Patient B', 'color': '#32CD32'},
        {'speaker_id': 'SPEAKER_03', 'name': 'Patient C', 'color': '#FF69B4'},
        {'speaker_id': 'SPEAKER_04', 'name': 'Patient D', 'color': '#FF4500'},
        {'speaker_id': 'SPEAKER_05', 'name': 'Patient E', 'color': '#9370DB'},
        {'speaker_id': 'SPEAKER_06', 'name': 'Patient F', 'color': '#20B2AA'},
        {'speaker_id': 'SPEAKER_07', 'name': 'Patient G', 'color': '#FFD700'},
        {'speaker_id': 'SPEAKER_08', 'name': 'Patient H', 'color': '#FF6347'},
        {'speaker_id': 'SPEAKER_09', 'name': 'Patient I', 'color': '#7CFC00'},
        {'speaker_id': 'SPEAKER_10', 'name': 'Patient J', 'color': '#4169E1'},
        {'speaker_id': 'SPEAKER_11', 'name': 'Patient K', 'color': '#DDA0DD'},
    ]

    open_speaker_editor(test_speakers)