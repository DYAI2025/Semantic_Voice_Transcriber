"""
Speaker Editor GUI Dialog

Provides a user-friendly dialog for editing speaker profiles:
- Edit speaker names
- Change speaker colors
- View speaker statistics
- Delete speakers
"""

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from typing import Dict, List, Callable, Optional
import logging
from pathlib import Path

from speaker_database import SpeakerDatabase

logger = logging.getLogger(__name__)


class SpeakerEditorDialog(tk.Toplevel):
    """Dialog for editing speaker profiles"""

    # Color palette for quick selection
    COLOR_PALETTE = [
        '#4A90E2',  # Blue
        '#7B68EE',  # Purple
        '#50C878',  # Green
        '#FF6B6B',  # Red
        '#FFA500',  # Orange
        '#20B2AA',  # Teal
        '#FF69B4',  # Pink
        '#FFD700',  # Gold
        '#8B4513',  # Brown
        '#708090',  # Gray
    ]

    # Speaker icons
    SPEAKER_ICONS = ['👤', '👨', '👩', '🧑', '👴', '👵', '🧔', '👨‍⚕️', '👩‍⚕️', '🧑‍💼']

    def __init__(
        self,
        parent,
        speakers: List[Dict],
        db_path: str,
        callback: Optional[Callable] = None
    ):
        """
        Initialize speaker editor dialog

        Args:
            parent: Parent window
            speakers: List of speaker dicts
            db_path: Path to speaker database
            callback: Optional callback function called on save
        """
        super().__init__(parent)

        self.speakers = speakers
        self.db_path = db_path
        self.callback = callback
        self.changes_made = False

        # Speaker editor widgets
        self.name_entries = {}
        self.color_buttons = {}
        self.color_canvases = {}
        self.icon_vars = {}
        self.selected_colors = {}

        # Initialize selected colors and icons from speakers
        for speaker in speakers:
            speaker_id = speaker['speaker_id']
            self.selected_colors[speaker_id] = speaker.get('color', '#4A90E2')

        # Configure dialog
        self.title("Speaker Editor")
        self.geometry("700x600")
        self.resizable(True, True)

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        self._create_ui()

        # Center on parent
        self.center_on_parent(parent)

        logger.info(f"Speaker editor dialog opened with {len(speakers)} speakers")

    def center_on_parent(self, parent):
        """Center dialog on parent window"""
        self.update_idletasks()

        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()

        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2

        self.geometry(f"+{x}+{y}")

    def _create_ui(self):
        """Create dialog UI"""
        # Main container with padding
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Edit Speaker Profiles",
            font=('Arial', 14, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 10), sticky=tk.W)

        # Scrollable speaker list
        self._create_speaker_list(main_frame)

        # Buttons
        self._create_buttons(main_frame)

    def _create_speaker_list(self, parent):
        """Create scrollable list of speaker editors"""
        # Frame with canvas and scrollbar
        container = ttk.Frame(parent)
        container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        # Canvas
        canvas = tk.Canvas(container, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbar
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        canvas.configure(yscrollcommand=scrollbar.set)

        # Frame inside canvas
        speakers_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=speakers_frame, anchor="nw")

        # Create editor for each speaker
        for i, speaker in enumerate(self.speakers):
            self._create_speaker_editor(speakers_frame, speaker, i)

        # Update scrollregion
        speakers_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _create_speaker_editor(self, parent, speaker: Dict, index: int):
        """
        Create editor widgets for a single speaker

        Args:
            parent: Parent frame
            speaker: Speaker dict
            index: Speaker index for grid layout
        """
        speaker_id = speaker['speaker_id']
        name = speaker.get('name', f'Speaker {speaker_id}')
        color = speaker.get('color', '#4A90E2')
        icon_index = speaker.get('icon_index', 0)
        total_duration = speaker.get('total_duration_seconds', 0)
        total_segments = speaker.get('total_segments', 0)

        # Container frame
        speaker_frame = ttk.LabelFrame(
            parent,
            text=f"Speaker {speaker_id}",
            padding="10"
        )
        speaker_frame.grid(row=index, column=0, sticky=(tk.W, tk.E), pady=5, padx=5)
        speaker_frame.columnconfigure(1, weight=1)

        # Name label and entry
        ttk.Label(speaker_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        name_entry = ttk.Entry(speaker_frame, width=30)
        name_entry.insert(0, name)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        self.name_entries[speaker_id] = name_entry

        # Icon selector
        ttk.Label(speaker_frame, text="Icon:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        icon_var = tk.StringVar(value=self.SPEAKER_ICONS[icon_index])
        icon_combo = ttk.Combobox(
            speaker_frame,
            textvariable=icon_var,
            values=self.SPEAKER_ICONS,
            width=5,
            state='readonly'
        )
        icon_combo.grid(row=0, column=3, padx=5)
        self.icon_vars[speaker_id] = icon_var

        # Color selector
        ttk.Label(speaker_frame, text="Color:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))

        # Color preview canvas
        color_canvas = tk.Canvas(speaker_frame, width=30, height=30, highlightthickness=1, highlightbackground="gray")
        color_canvas.create_rectangle(0, 0, 30, 30, fill=color, outline="")
        color_canvas.grid(row=1, column=1, sticky=tk.W, padx=5, pady=(5, 0))
        self.color_canvases[speaker_id] = color_canvas

        # Color picker button
        color_button = ttk.Button(
            speaker_frame,
            text="Pick Color",
            command=lambda sid=speaker_id: self._pick_color(sid)
        )
        color_button.grid(row=1, column=2, columnspan=2, sticky=tk.W, padx=(10, 5), pady=(5, 0))
        self.color_buttons[speaker_id] = color_button

        # Quick color palette
        palette_frame = ttk.Frame(speaker_frame)
        palette_frame.grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        ttk.Label(palette_frame, text="Quick:").pack(side=tk.LEFT, padx=(0, 5))

        for palette_color in self.COLOR_PALETTE[:8]:  # Show first 8 colors
            color_btn = tk.Button(
                palette_frame,
                bg=palette_color,
                width=2,
                height=1,
                command=lambda c=palette_color, sid=speaker_id: self._set_color(sid, c)
            )
            color_btn.pack(side=tk.LEFT, padx=2)

        # Statistics
        duration_min = int(total_duration // 60)
        duration_sec = int(total_duration % 60)
        stats_text = f"Segments: {total_segments} | Duration: {duration_min}m {duration_sec}s"
        stats_label = ttk.Label(speaker_frame, text=stats_text, foreground="gray")
        stats_label.grid(row=3, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))

        # Delete button (only if speaker has no segments)
        if total_segments == 0:
            delete_btn = ttk.Button(
                speaker_frame,
                text="Delete",
                command=lambda sid=speaker_id: self._delete_speaker(sid)
            )
            delete_btn.grid(row=3, column=3, sticky=tk.E, pady=(5, 0))

    def _pick_color(self, speaker_id: str):
        """Open color picker for speaker"""
        current_color = self.selected_colors.get(speaker_id, '#4A90E2')
        color = colorchooser.askcolor(
            title=f"Choose color for speaker {speaker_id}",
            initialcolor=current_color
        )

        if color[1]:  # color[1] is the hex string
            self._set_color(speaker_id, color[1])

    def _set_color(self, speaker_id: str, color: str):
        """Set speaker color and update preview"""
        self.selected_colors[speaker_id] = color

        # Update canvas
        canvas = self.color_canvases.get(speaker_id)
        if canvas:
            canvas.delete("all")
            canvas.create_rectangle(0, 0, 30, 30, fill=color, outline="")

        self.changes_made = True
        logger.debug(f"Speaker {speaker_id} color changed to {color}")

    def _delete_speaker(self, speaker_id: str):
        """Delete a speaker"""
        response = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete speaker {speaker_id}?\nThis action cannot be undone."
        )

        if response:
            try:
                with SpeakerDatabase(self.db_path) as db:
                    db.delete_speaker(speaker_id)

                messagebox.showinfo("Success", f"Speaker {speaker_id} deleted")
                self.changes_made = True

                # Remove from list
                self.speakers = [s for s in self.speakers if s['speaker_id'] != speaker_id]

                # Close and reopen to refresh
                self.destroy()

                logger.info(f"Speaker {speaker_id} deleted")

            except Exception as e:
                logger.error(f"Failed to delete speaker: {e}")
                messagebox.showerror("Error", f"Failed to delete speaker: {e}")

    def _create_buttons(self, parent):
        """Create dialog buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, pady=(10, 0), sticky=tk.E)

        # Save button
        save_btn = ttk.Button(
            button_frame,
            text="Save Changes",
            command=self._save_changes
        )
        save_btn.pack(side=tk.LEFT, padx=5)

        # Cancel button
        cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            command=self.destroy
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def _save_changes(self):
        """Save all changes to database"""
        try:
            with SpeakerDatabase(self.db_path) as db:
                for speaker in self.speakers:
                    speaker_id = speaker['speaker_id']

                    # Get new values
                    new_name = self.name_entries[speaker_id].get().strip()
                    new_color = self.selected_colors.get(speaker_id, speaker['color'])
                    new_icon = self.icon_vars[speaker_id].get()
                    new_icon_index = self.SPEAKER_ICONS.index(new_icon) if new_icon in self.SPEAKER_ICONS else 0

                    # Update if changed
                    if new_name != speaker.get('name', ''):
                        db.update_speaker_name(speaker_id, new_name)
                        logger.info(f"Updated speaker {speaker_id} name to: {new_name}")

                    if new_color != speaker.get('color', ''):
                        db.update_speaker_color(speaker_id, new_color)
                        logger.info(f"Updated speaker {speaker_id} color to: {new_color}")

                    if new_icon_index != speaker.get('icon_index', 0):
                        # Update icon index in database
                        db.cursor.execute(
                            "UPDATE speakers SET icon_index = ? WHERE speaker_id = ?",
                            (new_icon_index, speaker_id)
                        )
                        db.conn.commit()
                        logger.info(f"Updated speaker {speaker_id} icon to: {new_icon}")

            messagebox.showinfo("Success", "Speaker profiles updated successfully")
            self.changes_made = True

            # Call callback if provided
            if self.callback:
                self.callback()

            self.destroy()

        except Exception as e:
            logger.error(f"Failed to save changes: {e}")
            messagebox.showerror("Error", f"Failed to save changes:\n{e}")


# Standalone test
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    # Create test database with sample speakers
    db_path = "Memory/speaker_profiles.db"
    Path("Memory").mkdir(exist_ok=True)

    with SpeakerDatabase(db_path) as db:
        # Add test speakers if not exists
        db.add_speaker("SPEAKER_00", "Dr. Schmidt", "#4A90E2", 7)
        db.add_speaker("SPEAKER_01", "Patient A", "#7B68EE", 3)

        # Update some stats
        db.update_speaker_stats("SPEAKER_00", 923.2, 45)
        db.update_speaker_stats("SPEAKER_01", 924.3, 42)

        # Get all speakers
        speakers = db.get_all_speakers()

    # Create root window
    root = tk.Tk()
    root.title("Test Window")
    root.geometry("400x300")

    # Open editor button
    def open_editor():
        # Reload speakers
        with SpeakerDatabase(db_path) as db:
            speakers = db.get_all_speakers()

        # Open dialog
        dialog = SpeakerEditorDialog(
            root,
            speakers,
            db_path,
            callback=lambda: print("✅ Changes saved!")
        )
        root.wait_window(dialog)

    btn = ttk.Button(root, text="Open Speaker Editor", command=open_editor)
    btn.pack(pady=50)

    root.mainloop()
