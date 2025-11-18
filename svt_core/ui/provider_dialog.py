from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from svt_core.llm_provider.manager import ProviderManager
from svt_core.config.settings import SettingsStore, ProviderProfile
from svt_core.llm_provider.factory import build_provider_from_profile


class ProviderDialog(tk.Toplevel):
    def __init__(self, parent, manager: ProviderManager, store: SettingsStore, on_save=None):
        super().__init__(parent)
        self.manager = manager
        self.store = store
        self.on_save = on_save
        self.title("Provider Einstellungen")
        self.resizable(False, False)

        profile = self.store.get_provider_profile()
        ttk.Label(self, text="Provider").grid(row=0, column=0, padx=5, pady=5)
        self.provider_var = tk.StringVar(value=profile.key)
        provider_opts = ["local", "openai", "anthropic", "google", "grok"]
        ttk.Combobox(self, textvariable=self.provider_var, values=provider_opts, state="readonly").grid(row=0, column=1)

        ttk.Label(self, text="API Key").grid(row=1, column=0, padx=5, pady=5)
        self.key_var = tk.StringVar(value=profile.extra.get("key", "") if profile.extra else "")
        ttk.Entry(self, textvariable=self.key_var, width=40, show="*").grid(row=1, column=1)

        ttk.Label(self, text="Modell").grid(row=2, column=0, padx=5, pady=5)
        self.model_var = tk.StringVar(value=profile.model)
        ttk.Entry(self, textvariable=self.model_var, width=40).grid(row=2, column=1)

        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Test", command=self._test_provider).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Speichern", command=self._save).grid(row=0, column=1, padx=5)

    def _test_provider(self):
        provider_key = self.provider_var.get()
        profile = self._collect_profile()
        if profile.key == "local":
            messagebox.showinfo("Provider", "Lokaler Provider immer verfügbar")
            return
        try:
            provider = build_provider_from_profile(profile)
            response = provider.generate("Testverbindung")
            messagebox.showinfo("Provider", f"Test erfolgreich für {response.metadata.get('model')}")
        except Exception as exc:
            messagebox.showerror("Provider", f"Test fehlgeschlagen: {exc}")

    def _save(self):
        profile = self._collect_profile()
        self.store.set_provider_profile(profile)
        if self.on_save:
            self.on_save(profile)
        messagebox.showinfo("Provider", "Einstellungen gespeichert")
        self.destroy()

    def _collect_profile(self) -> ProviderProfile:
        extra = {"key": self.key_var.get()}
        return ProviderProfile(
            key=self.provider_var.get(),
            model=self.model_var.get(),
            alias=self.provider_var.get(),
            extra=extra,
        )
