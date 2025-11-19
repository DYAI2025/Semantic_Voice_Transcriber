#!/usr/bin/env python3
"""Provisioning helper to bootstrap SVT's local stack."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from svt_core.tools.generate_env import ensure_directories, write_env_file
from svt_core.config.defaults import DefaultPaths, DEFAULT_ENV
from svt_core import health_check


def ensure_ollama(cli_path: Optional[str]) -> bool:
    binary = cli_path or shutil.which("ollama")
    if not binary:
        print("⚠️ Ollama CLI nicht gefunden. Installiere von https://ollama.com/download")
        return False
    try:
        subprocess.run([binary, "--version"], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as exc:
        print(f"⚠️ Ollama CLI nicht lauffähig: {exc}")
        return False


def ensure_model(model: str, binary: Optional[str]) -> bool:
    binary = binary or shutil.which("ollama")
    if not binary:
        return False
    try:
        list_proc = subprocess.run([binary, "list"], capture_output=True, text=True, check=True)
        if model in list_proc.stdout:
            return True
        print(f"🌐 Lade Modell {model}...")
        subprocess.run([binary, "pull", model], check=True)
        return True
    except subprocess.CalledProcessError as exc:
        print(f"⚠️ Modell konnte nicht geladen werden: {exc}")
        return False


def run_health_check():
    results = health_check.run_all()
    status, summary = health_check.summarize(results)
    print(summary)
    if status == "error":
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description="Setup local SVT stack")
    parser.add_argument("--env", default=".env", help="Ziel-.env Pfad")
    parser.add_argument("--overwrite-env", action="store_true")
    parser.add_argument("--model", default=DEFAULT_ENV.get("OLLAMA_MODEL", "qwen2.5-coder:7b"))
    parser.add_argument("--ollama", default=None, help="Pfad zur ollama CLI")
    args = parser.parse_args()

    ensure_directories(DefaultPaths())
    write_env_file(Path(args.env), overwrite=args.overwrite_env)
    ok_cli = ensure_ollama(args.ollama)
    if ok_cli:
        ensure_model(args.model, args.ollama)
    run_health_check()
    print("✅ Lokaler Stack bereit.")


if __name__ == "__main__":
    main()
