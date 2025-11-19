# Installer Matrix

## Windows (Lite)
- NSIS script: `installer/windows/svt_lite.nsi`
- Copies repo to `$INSTDIR`, runs `scripts\setup_local_stack.py`, creates desktop shortcut.
- Build: `makensis installer/windows/svt_lite.nsi`

## macOS
- Script: `installer/macos/build_app.sh`
- Produces `.app` bundle wrapping SVT resources and a launcher that executes provisioning on first launch.
- Resulting bundle can be codesigned/notarized before distributing a `.dmg`.

## Linux
- AppImage helper: `installer/linux/build_appimage.sh` (produces `SVT.AppDir`; run `appimagetool` to pack).
- deb helper: `installer/linux/build_deb.sh` (creates package skeleton; run `dpkg-deb --build`).
- Both run `scripts/setup_local_stack.py` during launch or post-install to ensure directories, `.env`, and Ollama setup.

## Provisioning Script
- All installers invoke `python3 scripts/setup_local_stack.py --env <path> --overwrite-env` to configure defaults and verify health.
- Health-check output is surfaced to the user before the GUI launches (see `svt.py` health gate).
