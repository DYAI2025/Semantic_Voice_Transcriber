#!/bin/bash
# Bereinigungsskript für Semantic Voice Transcriber
# Erstellt: 2025-11-17
# Basierend auf: BESTANDSAUFNAHME_2025-11-17.md

set -e  # Exit on error

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funktion für farbigen Output
print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Banner
echo "=============================================="
echo "  Semantic Voice Transcriber"
echo "  Bereinigungsskript"
echo "  Datum: 2025-11-17"
echo "=============================================="
echo ""

# Bestätigung einholen
read -p "$(printf '%b' "${YELLOW}Möchten Sie die Bereinigung starten? [y/N]: ${NC}")" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    print_warning "Bereinigung abgebrochen."
    exit 0
fi

echo ""

# Phase-Auswahl
echo "Verfügbare Phasen:"
echo "  1 - Phase 1: Sofort-Bereinigung (leere Dateien, V3-Archiv, Logs)"
echo "  2 - Phase 2: Test-Organisation"
echo "  3 - Phase 3: Speaker Visualizer konsolidieren"
echo "  4 - Phase 4: Dokumentation konsolidieren (manuell)"
echo "  5 - Phase 5: Marker zentralisieren"
echo "  A - Alle Phasen (1+2+3+5)"
echo ""
read -p "$(echo -e ${YELLOW}Welche Phase möchten Sie ausführen? [1/2/3/5/A]: ${NC})" PHASE
echo ""

# ==============================================
# PHASE 1: SOFORT-BEREINIGUNG
# ==============================================

if [[ $PHASE == "1" ]] || [[ $PHASE == "A" ]] || [[ $PHASE == "a" ]]; then
    print_step "Phase 1: Sofort-Bereinigung"
    echo ""

    # 1. Backup erstellen
    print_step "1.1 Erstelle Git Backup..."
    git add -A 2>/dev/null || true
    git status --short
    read -p "$(echo -e ${YELLOW}Backup committen? [y/N]: ${NC})" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git commit -m "Pre-cleanup backup - Phase 1" 2>/dev/null || print_warning "Nichts zu committen"
        print_success "Backup erstellt"
    fi
    echo ""

    # 2. Leere Dateien löschen
    print_step "1.2 Lösche leere Dateien..."
    if [ -f "whisper_auto_runner.py" ]; then
        rm whisper_auto_runner.py
        print_success "Gelöscht: whisper_auto_runner.py"
    else
        print_warning "Nicht gefunden: whisper_auto_runner.py"
    fi

    if [ -f "whisper_transcriber.py" ]; then
        rm whisper_transcriber.py
        print_success "Gelöscht: whisper_transcriber.py"
    else
        print_warning "Nicht gefunden: whisper_transcriber.py"
    fi
    echo ""

    # 3. Leere Logs löschen
    print_step "1.3 Lösche leere Log-Dateien..."
    for log in transcription.log transcription_v2.log transcription_v3.log; do
        if [ -f "$log" ]; then
            rm "$log"
            print_success "Gelöscht: $log"
        else
            print_warning "Nicht gefunden: $log"
        fi
    done
    echo ""

    # 4. Archiv-Ordner erstellen
    print_step "1.4 Erstelle Archiv-Verzeichnis..."
    if [ ! -d "archive" ]; then
        mkdir archive
        print_success "Erstellt: archive/"
    else
        print_warning "Verzeichnis existiert bereits: archive/"
    fi
    echo ""

    # 5. V3-Versionen archivieren
    print_step "1.5 Archiviere veraltete V3-Versionen..."
    if [ -f "auto_transcriber_v3.py" ]; then
        mv auto_transcriber_v3.py archive/
        print_success "Archiviert: auto_transcriber_v3.py"
    else
        print_warning "Nicht gefunden: auto_transcriber_v3.py"
    fi

    if [ -f "whisper_transcriber_v3.py" ]; then
        mv whisper_transcriber_v3.py archive/
        print_success "Archiviert: whisper_transcriber_v3.py"
    else
        print_warning "Nicht gefunden: whisper_transcriber_v3.py"
    fi
    echo ""

    # 6. Leere Marker bereinigen
    print_step "1.6 Bereinige leere Marker-Dateien..."
    if [ -f "ATO_C_SOFT_COMMITMENT_MARKER.yaml" ]; then
        rm ATO_C_SOFT_COMMITMENT_MARKER.yaml
        print_success "Gelöscht: ATO_C_SOFT_COMMITMENT_MARKER.yaml"
    else
        print_warning "Nicht gefunden: ATO_C_SOFT_COMMITMENT_MARKER.yaml"
    fi

    if [ -f "ATO_DEFENSIVENESS_SHIFT_MARKER.yaml" ]; then
        rm ATO_DEFENSIVENESS_SHIFT_MARKER.yaml
        print_success "Gelöscht: ATO_DEFENSIVENESS_SHIFT_MARKER.yaml"
    else
        print_warning "Nicht gefunden: ATO_DEFENSIVENESS_SHIFT_MARKER.yaml"
    fi
    echo ""

    # 7. Commit Phase 1
    print_step "1.7 Committe Änderungen..."
    git add -A 2>/dev/null || true
    git status --short
    read -p "$(echo -e ${YELLOW}Phase 1 committen? [y/N]: ${NC})" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git commit -m "Phase 1: Remove empty files, archive V3, cleanup logs and markers" 2>/dev/null || print_warning "Nichts zu committen"
        print_success "Phase 1 committed"
    fi
    echo ""

    print_success "Phase 1 abgeschlossen!"
    echo ""
fi

# ==============================================
# PHASE 2: TEST-ORGANISATION
# ==============================================

if [[ $PHASE == "2" ]] || [[ $PHASE == "A" ]] || [[ $PHASE == "a" ]]; then
    print_step "Phase 2: Test-Organisation"
    echo ""

    # Liste der Test-Dateien
    TEST_FILES=(
        "test_prosody_analyzer.py"
        "test_prosody_pipeline.py"
        "test_audio_quality_analyzer.py"
        "test_audio_preprocessor.py"
        "test_confidence_scoring.py"
        "test_intelligent_pipeline_integration.py"
        "test_integration_therapeutic.py"
        "test_memory_prosody.py"
        "test_output_formatter_osd.py"
        "test_overlapped_speech_detection.py"
        "test_transcriber_osd_integration.py"
        "test_transcriber_v4_prosody.py"
        "test_transcription.py"
        "test_initialize_person.py"
        "test_yaml_structure.py"
        "test_task3_integration.py"
        "task3_requirements_check.py"
        "run_test_prosody.py"
    )

    # Tests verschieben
    print_step "2.1 Verschiebe Test-Dateien nach tests/..."
    MOVED=0
    for test_file in "${TEST_FILES[@]}"; do
        if [ -f "$test_file" ]; then
            mv "$test_file" tests/
            print_success "Verschoben: $test_file → tests/"
            MOVED=$((MOVED + 1))
        else
            print_warning "Nicht gefunden: $test_file"
        fi
    done
    echo ""
    print_success "Verschoben: $MOVED Dateien"
    echo ""

    # Commit Phase 2
    print_step "2.2 Committe Änderungen..."
    git add -A 2>/dev/null || true
    git status --short
    read -p "$(echo -e ${YELLOW}Phase 2 committen? [y/N]: ${NC})" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git commit -m "Phase 2: Move all tests to tests/ directory" 2>/dev/null || print_warning "Nichts zu committen"
        print_success "Phase 2 committed"
    fi
    echo ""

    print_success "Phase 2 abgeschlossen!"
    echo ""
fi

# ==============================================
# PHASE 3: SPEAKER VISUALIZER KONSOLIDIEREN
# ==============================================

if [[ $PHASE == "3" ]] || [[ $PHASE == "A" ]] || [[ $PHASE == "a" ]]; then
    print_step "Phase 3: Speaker Visualizer konsolidieren"
    echo ""

    # Archiv-Ordner sicherstellen
    if [ ! -d "archive" ]; then
        mkdir archive
        print_success "Erstellt: archive/"
    fi

    # Speaker Visualizer v2 archivieren
    print_step "3.1 Archiviere speaker_visualizer_v2.py..."
    if [ -f "speaker_visualizer_v2.py" ]; then
        mv speaker_visualizer_v2.py archive/
        print_success "Archiviert: speaker_visualizer_v2.py"
    else
        print_warning "Nicht gefunden: speaker_visualizer_v2.py"
    fi
    echo ""

    # Enhanced Version ins Root verschieben
    print_step "3.2 Verschiebe enhanced speaker_visualizer ins Root..."
    if [ -f "enhanced_components/speaker_visualizer.py" ]; then
        mv enhanced_components/speaker_visualizer.py ./
        print_success "Verschoben: enhanced_components/speaker_visualizer.py → ./"
    else
        print_warning "Nicht gefunden: enhanced_components/speaker_visualizer.py"
    fi
    echo ""

    # enhanced_components aufräumen
    print_step "3.3 Räume enhanced_components/ auf..."
    if [ -d "enhanced_components" ]; then
        # Prüfe ob Verzeichnis leer ist (außer __init__.py und __pycache__)
        REMAINING=$(find enhanced_components -type f ! -name "__init__.py" ! -path "*/__pycache__/*" | wc -l)
        if [ "$REMAINING" -eq 0 ]; then
            rm -rf enhanced_components/
            print_success "Gelöscht: enhanced_components/ (leer)"
        else
            print_warning "enhanced_components/ enthält noch $REMAINING Dateien - nicht gelöscht"
        fi
    fi
    echo ""

    # Commit Phase 3
    print_step "3.4 Committe Änderungen..."
    git add -A 2>/dev/null || true
    git status --short
    read -p "$(echo -e ${YELLOW}Phase 3 committen? [y/N]: ${NC})" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git commit -m "Phase 3: Consolidate speaker visualizer, remove duplicate" 2>/dev/null || print_warning "Nichts zu committen"
        print_success "Phase 3 committed"
    fi
    echo ""

    print_success "Phase 3 abgeschlossen!"
    echo ""
fi

# ==============================================
# PHASE 4: DOKUMENTATION (MANUELL)
# ==============================================

if [[ $PHASE == "4" ]]; then
    print_warning "Phase 4 erfordert manuelle Konsolidierung der Dokumentation"
    echo ""
    echo "Folgende Schritte sind erforderlich:"
    echo ""
    echo "1. README konsolidieren:"
    echo "   - mv README_SUPER_SEMANTIC.md docs/SUPER_SEMANTIC.md"
    echo "   - mv FÜR_KUNDIN_README.md docs/CUSTOMER_GUIDE_DE.md"
    echo ""
    echo "2. Installations-Guides zusammenführen:"
    echo "   - Manuell docs/INSTALLATION_COMPLETE.md erstellen"
    echo "   - Inhalte aus INSTALL.md, INSTALLATION_CROSS_PLATFORM.md,"
    echo "     INSTALLATIONS_CHECKLISTE.md konsolidieren"
    echo "   - Alte Dateien löschen"
    echo ""
    echo "3. Duplikate entfernen:"
    echo "   - rm INTELLIGENT_PIPELINE.md  # docs/ Version behalten"
    echo ""
    print_warning "Bitte manuell durchführen!"
    echo ""
fi

# ==============================================
# PHASE 5: MARKER ZENTRALISIEREN
# ==============================================

if [[ $PHASE == "5" ]] || [[ $PHASE == "A" ]] || [[ $PHASE == "a" ]]; then
    print_step "Phase 5: Marker zentralisieren"
    echo ""

    # Marker-Verzeichnisse erstellen
    print_step "5.1 Erstelle Marker-Verzeichnisse..."
    mkdir -p markers/ato
    mkdir -p markers/sem
    mkdir -p markers/clu
    print_success "Erstellt: markers/{ato,sem,clu}/"
    echo ""

    # ATO Marker verschieben
    print_step "5.2 Verschiebe ATO Marker..."
    ATO_COUNT=0
    for ato_file in ATO_*.yaml; do
        if [ -f "$ato_file" ]; then
            mv "$ato_file" markers/ato/
            print_success "Verschoben: $ato_file → markers/ato/"
            ((ATO_COUNT++))
        fi
    done
    print_success "Verschoben: $ATO_COUNT ATO-Marker"
    echo ""

    # SEM Marker verschieben
    print_step "5.3 Verschiebe SEM Marker..."
    SEM_COUNT=0
    for sem_file in SEM_*.yaml; do
        if [ -f "$sem_file" ]; then
            mv "$sem_file" markers/sem/
            print_success "Verschoben: $sem_file → markers/sem/"
            SEM_COUNT=$((SEM_COUNT + 1))
        fi
    done
    print_success "Verschoben: $SEM_COUNT SEM-Marker"
    echo ""

    # Proposed markers verschieben
    print_step "5.4 Verschiebe proposed_new_markers.yaml..."
    if [ -f "proposed_new_markers.yaml" ]; then
        mv proposed_new_markers.yaml markers/
        print_success "Verschoben: proposed_new_markers.yaml → markers/"
    else
        print_warning "Nicht gefunden: proposed_new_markers.yaml"
    fi
    echo ""

    # Config bereinigen
    print_step "5.5 Verschiebe correlation_config.yaml..."
    if [ -f "correlation_config.yaml" ]; then
        mv correlation_config.yaml config/
        print_success "Verschoben: correlation_config.yaml → config/"
    else
        print_warning "Nicht gefunden: correlation_config.yaml"
    fi
    echo ""

    # Commit Phase 5
    print_step "5.6 Committe Änderungen..."
    git add -A 2>/dev/null || true
    git status --short
    read -p "$(printf '%b' "${YELLOW}Phase 5 committen? [y/N]: ${NC}")" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if git diff --cached --quiet; then
            print_warning "Nichts zu committen"
        else
            git commit -m "Phase 5: Centralize marker system"
            print_success "Phase 5 committed"
        fi
    fi
    echo ""

    print_success "Phase 5 abgeschlossen!"
    echo ""
fi

# ==============================================
# ZUSAMMENFASSUNG
# ==============================================

echo ""
print_success "=============================================="
print_success "  Bereinigung abgeschlossen!"
print_success "=============================================="
echo ""
echo "Nächste Schritte:"
echo "1. Tests ausführen: python3 -m pytest tests/"
echo "2. SVT starten: python3 svt.py"
echo "3. Funktionalität prüfen"
echo "4. Bei Erfolg: git push"
echo ""
print_warning "Bitte prüfen Sie die Änderungen mit 'git status' und 'git diff'"
echo ""
