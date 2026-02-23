/**
 * SVT Dashboard Application
 * Hauptanwendung für das Therapeuten-Dashboard
 */

// Initialize global state
const AppState = {
    currentView: 'upload',
    currentFile: null,
    transcript: null,
    analysis: null,
    turnpoints: null,
    isProcessing: false
};

// Initialize API
const api = new SVTAPI();

// DOM Elements
const elements = {};

/**
 * Initialize the application
 */
function initApp() {
    cacheElements();
    bindEvents();
    loadDemoData();
    showToast('Dashboard geladen', 'success');
}

/**
 * Cache DOM elements for performance
 */
function cacheElements() {
    elements.navItems = document.querySelectorAll('.nav-item');
    elements.views = document.querySelectorAll('.view');
    elements.dropZone = document.getElementById('dropZone');
    elements.fileInput = document.getElementById('fileInput');
    elements.selectFileBtn = document.getElementById('selectFileBtn');
    elements.uploadProgress = document.getElementById('uploadProgress');
    elements.progressFill = document.getElementById('progressFill');
    elements.progressPercent = document.getElementById('progressPercent');
    elements.progressFileName = document.getElementById('progressFileName');
    elements.progressStatus = document.getElementById('progressStatus');
    elements.transcriptContent = document.getElementById('transcriptContent');
    elements.searchInput = document.getElementById('searchInput');
    elements.showTherapist = document.getElementById('showTherapist');
    elements.showPatient = document.getElementById('showPatient');
    elements.runAnalysis = document.getElementById('runAnalysis');
    elements.markerList = document.getElementById('markerList');
    elements.markerCount = document.getElementById('markerCount');
    elements.themeList = document.getElementById('themeList');
    elements.suggestionsList = document.getElementById('suggestionsList');
    elements.turnpointsTimeline = document.getElementById('turnpointsTimeline');
    elements.toastContainer = document.getElementById('toastContainer');
    elements.modalOverlay = document.getElementById('modalOverlay');
    elements.modal = document.getElementById('modal');
    elements.modalTitle = document.getElementById('modalTitle');
    elements.modalContent = document.getElementById('modalContent');
    elements.modalClose = document.getElementById('modalClose');
    elements.loadingOverlay = document.getElementById('loadingOverlay');
    elements.loadingText = document.getElementById('loadingText');
}

/**
 * Bind event listeners
 */
function bindEvents() {
    // Navigation
    elements.navItems.forEach(item => {
        item.addEventListener('click', () => switchView(item.dataset.view));
    });

    // File upload
    elements.dropZone.addEventListener('click', () => elements.fileInput.click());
    elements.selectFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        elements.fileInput.click();
    });

    elements.fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    elements.dropZone.addEventListener('dragover', handleDragOver);
    elements.dropZone.addEventListener('dragleave', handleDragLeave);
    elements.dropZone.addEventListener('drop', handleDrop);

    // Search
    elements.searchInput.addEventListener('input', handleSearch);

    // Speaker filter
    elements.showTherapist.addEventListener('change', renderTranscript);
    elements.showPatient.addEventListener('change', renderTranscript);

    // Analysis
    elements.runAnalysis.addEventListener('click', runAnalysis);

    // Export buttons
    document.querySelectorAll('.export-card button').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const format = e.target.closest('.export-card').dataset.format;
            handleExport(format);
        });
    });

    // Modal
    elements.modalClose.addEventListener('click', closeModal);
    elements.modalOverlay.addEventListener('click', (e) => {
        if (e.target === elements.modalOverlay) closeModal();
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboard);
}

/**
 * Switch between views
 */
function switchView(viewName) {
    if (AppState.isProcessing && viewName !== 'upload') {
        showToast('Bitte warten Sie, bis die Verarbeitung abgeschlossen ist', 'warning');
        return;
    }

    // Update nav
    elements.navItems.forEach(item => {
        item.classList.toggle('active', item.dataset.view === viewName);
    });

    // Update views
    elements.views.forEach(view => {
        view.classList.toggle('active', view.id === `view-${viewName}`);
    });

    AppState.currentView = viewName;
}

/**
 * Handle file selection
 */
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) processFile(file);
}

/**
 * Handle drag over
 */
function handleDragOver(e) {
    e.preventDefault();
    elements.dropZone.classList.add('dragover');
}

/**
 * Handle drag leave
 */
function handleDragLeave(e) {
    e.preventDefault();
    elements.dropZone.classList.remove('dragover');
}

/**
 * Handle drop
 */
function handleDrop(e) {
    e.preventDefault();
    elements.dropZone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file) processFile(file);
}

/**
 * Process uploaded file
 */
async function processFile(file) {
    // Validate file
    const validTypes = ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/mp4', 'audio/ogg', 'audio/flac', 'audio/x-m4a'];
    const maxSize = 500 * 1024 * 1024; // 500MB

    if (!validTypes.includes(file.type) && !file.name.match(/\.(mp3|wav|m4a|ogg|flac)$/i)) {
        showToast('Ungültiges Dateiformat. Bitte MP3, WAV, M4A, OGG oder FLAC verwenden.', 'error');
        return;
    }

    if (file.size > maxSize) {
        showToast('Datei zu groß. Maximal 500 MB erlaubt.', 'error');
        return;
    }

    AppState.currentFile = file;
    
    // Show progress
    elements.uploadProgress.style.display = 'block';
    elements.progressFileName.textContent = file.name;
    updateProgress(10, 'Bereit zum Hochladen...');

    try {
        // Simulate upload progress
        simulateUpload();

    } catch (error) {
        showToast(`Fehler: ${error.message}`, 'error');
        updateProgress(0, 'Fehler aufgetreten');
    }
}

/**
 * Simulate file upload (placeholder for real implementation)
 */
async function simulateUpload() {
    for (let i = 10; i <= 100; i += 10) {
        await sleep(200);
        updateProgress(i, i < 100 ? 'Transkription läuft...' : 'Transkription abgeschlossen');
    }

    // Generate demo transcript
    AppState.transcript = generateDemoTranscript();
    
    showToast('Transkription erfolgreich', 'success');
    updateProgress(100, 'Fertig! Klicken Sie auf "Transkription" um das Ergebnis zu sehen.');
    
    // Auto switch to transcript view
    setTimeout(() => {
        switchView('transcript');
        renderTranscript();
    }, 1000);
}

/**
 * Update progress bar
 */
function updateProgress(percent, status) {
    elements.progressFill.style.width = `${percent}%`;
    elements.progressPercent.textContent = `${percent}%`;
    elements.progressStatus.textContent = status;
}

/**
 * Render transcript
 */
function renderTranscript() {
    if (!AppState.transcript) {
        elements.transcriptContent.innerHTML = `
            <div class="empty-state">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                </svg>
                <p>Keine Transkription geladen</p>
                <span>Laden Sie zuerst eine Audio-Datei hoch</span>
            </div>
        `;
        return;
    }

    const showTherapist = elements.showTherapist.checked;
    const showPatient = elements.showPatient.checked;
    const searchTerm = elements.searchInput.value.toLowerCase();

    const filteredEntries = AppState.transcript.filter(entry => {
        const speaker = entry.speaker?.toLowerCase() || '';
        const isTherapist = speaker.includes('therapist') || speaker.includes('arzt') || speaker === 't';
        const isPatient = speaker.includes('patient') || speaker.includes('klient') || speaker === 'p';
        
        if (isTherapist && !showTherapist) return false;
        if (isPatient && !showPatient) return false;
        
        if (searchTerm && !entry.text.toLowerCase().includes(searchTerm)) return false;
        
        return true;
    });

    elements.transcriptContent.innerHTML = filteredEntries.map((entry, index) => {
        const speaker = entry.speaker || 'Unknown';
        const isTherapist = speaker.toLowerCase().includes('therapist') || speaker.toLowerCase() === 't' || speaker.toLowerCase().includes('arzt');
        const speakerClass = isTherapist ? 'therapist' : (speaker.toLowerCase().includes('patient') || speaker.toLowerCase() === 'p') ? 'patient' : 'unknown';
        const speakerLabel = isTherapist ? 'Therapeut' : (speaker.toLowerCase().includes('patient') || speaker.toLowerCase() === 'p') ? 'Patient' : speaker;

        const startTime = formatTime(entry.start || 0);
        const markers = (entry.markers || []).map(m => 
            `<span class="marker-tag ${m.category || 'theme'}">${m.type}</span>`
        ).join('');

        return `
            <div class="transcript-entry ${speakerClass}${entry.markers?.length ? ' has-markers' : ''}" data-index="${index}">
                <div class="entry-meta">
                    <span class="entry-speaker ${speakerClass}">
                        <span class="speaker-dot ${speakerClass}"></span>
                        ${speakerLabel}
                    </span>
                    <span class="entry-time">${startTime}</span>
                </div>
                <div class="entry-text">${highlightSearch(highlightATOMarkers(entry.text, entry.markers), searchTerm)}</div>
            </div>
        `;
    }).join('');

    // Scroll to bottom
    elements.transcriptContent.scrollTop = elements.transcriptContent.scrollHeight;
}

/**
 * Highlight ATO markers inline in transcript text
 */
function highlightATOMarkers(text, markers = []) {
    if (!markers || markers.length === 0) return autoDetectMarkers(text);
    
    let result = text;
    markers.forEach(marker => {
        if (marker.position && marker.text) {
            const regex = new RegExp(`(${escapeRegex(marker.text)})`, 'gi');
            const tooltip = getMarkerTooltip(marker);
            result = result.replace(regex, 
                `<span class="marker-inline ${marker.category || 'theme'}" data-tooltip="${tooltip}">$1</span>`
            );
        }
    });
    
    return autoDetectMarkers(result);
}

/**
 * Auto-detect markers in text based on keywords
 */
function autoDetectMarkers(text) {
    const markerPatterns = {
        'defense_denial': { pattern: /\b(nicht wahr|stimmt nicht|leugnen|das stimmt nicht|ich nicht)\b/gi, tooltip: 'Verleugnung: Ablehnung unangenehmer Realitäten' },
        'defense_projection': { pattern: /\b(der andere|schuld ist|anderen geben|er/sie macht|die schuld)\b/gi, tooltip: 'Projektion: Zuschreiben eigener unerwünschter Eigenschaften' },
        'defense_rationalization': { pattern: /\b(eigentlich|logisch|vernünftig|betrachtet|ja aber)\b/gi, tooltip: 'Rationalisierung: Intellektuelle Rechtfertigung' },
        'defense_displacement': { pattern: /\b(egal|hauptsache|nebensächlich|anderen geht es)\b/gi, tooltip: 'Verschiebung: Emotion auf ungefährliches Ziel' },
        'resistance_topic_change': { pattern: /\b(übrigens|nebenbei|was noch|eigentlich)\b/gi, tooltip: 'Themenwechsel: Vermeidung' },
        'resistance_humor': { pattern: /\b(lachen muss|witzig|lustig|ha ha|ähaha)\b/gi, tooltip: 'Humor: Ablenkung von Ernst' },
        'transference_positive': { pattern: /\b(vertrauen ihnen|glaube ihnen|hilfreich|danke|besser)\b/gi, tooltip: 'Positive Übertragung' },
        'transference_negative': { pattern: /\b(schwierig|unangenehm|nicht hilfreich|traue nicht)\b/gi, tooltip: 'Negative Übertragung' },
        'transference_dependency': { pattern: /\b(immer|nur|ohne sie|brauche|allein nicht)\b/gi, tooltip: 'Abhängigkeit in der Beziehung' },
        'theme_separation_anxiety': { pattern: /\b(allein|verlassen|verloren|trennung|alleine sein)\b/gi, tooltip: 'Trennungsangst' },
        'theme_control': { pattern: /\b(kontrolle|muss|muessen|bestimmen|alles unter)\b/gi, tooltip: 'Kontrollbedürfnis' },
        'theme_abandonment': { pattern: /\b(verlassen|allein|niemand|nie|verlassen werden)\b/gi, tooltip: 'Verlassenheitsangst' },
        'theme_shame_guilt': { pattern: /\b(schuld|scham|peinlich|falsch|schäme|schäm mich)\b/gi, tooltip: 'Scham/Schuld' },
    };
    
    let result = text;
    Object.entries(markerPatterns).forEach(([markerType, {pattern, tooltip}]) => {
        const category = markerType.split('_')[0];
        result = result.replace(pattern, (match) => 
            `<span class="marker-inline ${category}" data-tooltip="${tooltip}">${match}</span>`
        );
    });
    
    return result;
}

/**
 * Get marker tooltip text
 */
function getMarkerTooltip(marker) {
    const tooltips = {
        'defense_denial': 'Verleugnung - Ablehnung unangenehmer Realitäten',
        'defense_projection': 'Projektion - Zuschreiben eigener Eigenschaften',
        'defense_rationalization': 'Rationalisierung - Intellektuelle Rechtfertigung',
        'defense_displacement': 'Verschiebung - Emotion auf anderes Ziel',
        'resistance_silence': 'Schweigen - Widerstand oder Verarbeitung',
        'resistance_topic_change': 'Themenwechsel - Vermeidung',
        'resistance_humor': 'Humor - Ablenkung',
        'transference_positive': 'Positive Übertragung',
        'transference_negative': 'Negative Übertragung',
        'transference_dependency': 'Abhängigkeit',
        'theme_separation_anxiety': 'Trennungsangst',
        'theme_control': 'Kontrollbedürfnis',
        'theme_abandonment': 'Verlassenheitsangst',
        'theme_shame_guilt': 'Scham/Schuld',
    };
    return tooltips[marker.type] || marker.description || 'Klinisch relevant';
}

/**
 * Handle search
 */
function handleSearch() {
    renderTranscript();
}

/**
 * Highlight search term
 */
function highlightSearch(text, term) {
    if (!term) return text;
    const regex = new RegExp(`(${escapeRegex(term)})`, 'gi');
    return text.replace(regex, '<mark style="background: #fef08a; padding: 0 2px;">$1</mark>');
}

/**
 * Run analysis
 */
async function runAnalysis() {
    if (!AppState.transcript) {
        showToast('Keine Transkription zum Analysieren', 'warning');
        return;
    }

    showLoading('Analysiere Transkription...');

    try {
        // Use local analysis as fallback
        AppState.analysis = api.analyzeLocally(AppState.transcript);
        
        // Detect turnpoints
        AppState.turnpoints = detectTurnpoints(AppState.transcript);

        renderAnalysis();
        renderTurnpoints();
        
        showToast('Analyse abgeschlossen', 'success');
    } catch (error) {
        showToast(`Analyse-Fehler: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Render analysis results
 */
function renderAnalysis() {
    if (!AppState.analysis) return;

    // Render summary
    const summaryCard = document.getElementById('summaryCard');
    summaryCard.querySelector('.card-content').innerHTML = `
        <p style="line-height: 1.8; color: var(--color-gray-700);">${AppState.analysis.summary}</p>
    `;

    // Render markers
    const markers = AppState.analysis.markers || [];
    elements.markerCount.textContent = markers.length;
    
    elements.markerList.innerHTML = markers.length ? markers.map((marker, i) => `
        <div class="marker-item" onclick="showMarkerDetails(${i})">
            <div class="marker-icon ${marker.category}">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    ${getMarkerIcon(marker.category)}
                </svg>
            </div>
            <div class="marker-content">
                <div class="marker-type">${formatMarkerType(marker.type)}</div>
                <div class="marker-description">${marker.description}</div>
            </div>
        </div>
    `).join('') : `
        <div class="empty-state small">
            <p>Keine Marker erkannt</p>
        </div>
    `;

    // Render themes
    const themes = AppState.analysis.themes || [];
    elements.themeList.innerHTML = themes.length ? themes.map(theme => 
        `<span class="theme-tag">${formatThemeName(theme)}</span>`
    ).join('') : `
        <div class="empty-state small">
            <p>Keine Themen erkannt</p>
        </div>
    `;

    // Render suggestions
    const suggestions = AppState.analysis.suggestions || [];
    elements.suggestionsList.innerHTML = suggestions.length ? suggestions.map((s, i) => `
        <div class="suggestion-item">
            <span class="suggestion-number">${i + 1}</span>
            <span class="suggestion-text">${s}</span>
        </div>
    `).join('') : `
        <div class="empty-state small">
            <p>Keine Vorschläge verfügbar</p>
        </div>
    `;

    // Update speaker stats
    updateSpeakerStats();
}

/**
 * Render turnpoints
 */
function renderTurnpoints() {
    if (!AppState.turnpoints || !AppState.turnpoints.length) {
        elements.turnpointsTimeline.innerHTML = `
            <div class="empty-state">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                </svg>
                <p>Keine Wendepunkte erkannt</p>
                <span>Führen Sie eine Analyse durch</span>
            </div>
        `;
        return;
    }

    const typeIcons = {
        emotional: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>',
        resistance: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg>',
        defense: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
        narrative: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v18h18"/><path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/></svg>'
    };

    elements.turnpointsTimeline.innerHTML = AppState.turnpoints.map(tp => `
        <div class="turnpoint-item">
            <div class="turnpoint-icon ${tp.type}">
                ${typeIcons[tp.type] || typeIcons.emotional}
            </div>
            <div class="turnpoint-content">
                <div class="turnpoint-header">
                    <span class="turnpoint-type ${tp.type}">${formatTurnpointType(tp.type)}</span>
                    <span class="turnpoint-time">${formatTime(tp.time)}</span>
                </div>
                <h4 style="margin: 8px 0; color: var(--color-gray-800);">${tp.title}</h4>
                <p style="font-size: 13px; color: var(--color-gray-600); margin-bottom: 8px;">${tp.description}</p>
                ${tp.quote ? `<div class="turnpoint-quote">"${tp.quote}"</div>` : ''}
                ${tp.context ? `<div style="font-size: 12px; color: var(--color-gray-500); margin-top: 8px;"><em>Vorangehend: "${tp.context}"</em></div>` : ''}
            </div>
        </div>
    `).join('');
}

/**
 * Detect turnpoints from transcript
 */
function detectTurnpoints(transcript) {
    const turnpoints = [];
    
    // Keyword-based detection patterns
    const patterns = {
        emotional: {
            keywords: ['fühle', 'gefühl', 'traurig', 'glücklich', 'angst', 'freude', 'schmerz', 'leid', 'hoffnung', 'verzweifelt', 'erleichtert'],
            description: 'Emotionale Regung'
        },
        resistance: {
            keywords: ['ähm', 'also', 'hm', 'na ja', 'egal', 'weiß nicht', 'keine ahnung', 'vielleicht', '主题wechsel'],
            description: 'Widerstand oder Vermeidung'
        },
        defense: {
            keywords: ['eigentlich', 'logisch', 'normal', 'da muss man', 'klar', 'natürlich', 'ja aber', 'nein eigentlich'],
            description: 'Abwehrmechanismus aktiv'
        },
        narrative: {
            keywords: ['dann', 'plötzlich', 'früher', 'immer', 'kindheit', 'eltern', 'damals', 'erinnerung', 'geschichte'],
            description: 'Narrativer Themenwechsel'
        }
    };
    
    for (let i = 0; i < transcript.length; i++) {
        const entry = transcript[i];
        const text = entry.text.toLowerCase();
        
        // Check each pattern category
        for (const [type, config] of Object.entries(patterns)) {
            for (const keyword of config.keywords) {
                if (text.includes(keyword)) {
                    // Check if this is a transition (new topic or shift)
                    const isTransition = i > 0 && (
                        text.includes('aber') || 
                        text.includes('dann') || 
                        text.includes('und dann') ||
                        text.length > 50
                    );
                    
                    // Avoid duplicate entries
                    const exists = turnpoints.some(tp => 
                        tp.time === entry.start && tp.type === type
                    );
                    
                    if (!exists && (isTransition || Math.random() < 0.3)) {
                        turnpoints.push({
                            time: entry.start || 0,
                            type: type,
                            title: `${config.description}`,
                            description: `Schlüsselwort "${keyword}" erkannt`,
                            quote: entry.text.substring(0, 120) + (entry.text.length > 120 ? '...' : ''),
                            context: i > 0 ? transcript[i-1].text.substring(0, 80) : null
                        });
                        break;
                    }
                }
            }
        }
    }

    // Sort by time and limit
    turnpoints.sort((a, b) => a.time - b.time);
    return turnpoints.slice(0, 15);
}

/**
 * Calculate simple valence score
 */
function calculateValence(text) {
    const positiveWords = ['gut', 'besser', 'schön', 'freude', 'glücklich', 'danke', 'hilfreich'];
    const negativeWords = ['schlecht', 'schwer', 'probleme', 'angst', 'traurig', 'schwer', 'unwohl'];
    
    const lower = text.toLowerCase();
    let score = 0;
    
    positiveWords.forEach(w => { if (lower.includes(w)) score += 0.2; });
    negativeWords.forEach(w => { if (lower.includes(w)) score -= 0.2; });
    
    return Math.max(-1, Math.min(1, score));
}

/**
 * Update speaker statistics
 */
function updateSpeakerStats() {
    if (!AppState.transcript) return;

    const therapistTime = AppState.transcript
        .filter(e => (e.speaker?.toLowerCase() || '').includes('therapist') || e.speaker?.toLowerCase() === 't')
        .reduce((acc, e) => acc + ((e.end || 0) - (e.start || 0)), 0);

    const patientTime = AppState.transcript
        .filter(e => (e.speaker?.toLowerCase() || '').includes('patient') || e.speaker?.toLowerCase() === 'p')
        .reduce((acc, e) => acc + ((e.end || 0) - (e.start || 0)), 0);

    document.getElementById('therapistTime').textContent = formatDuration(therapistTime);
    document.getElementById('patientTime').textContent = formatDuration(patientTime);
}

/**
 * Handle export
 */
async function handleExport(format) {
    if (!AppState.transcript) {
        showToast('Keine Daten zum Exportieren', 'warning');
        return;
    }

    const exportData = {
        transcript: AppState.transcript,
        analysis: AppState.analysis,
        exportDate: new Date().toISOString()
    };

    let content, filename, type;

    switch (format) {
        case 'json':
            content = JSON.stringify(exportData, null, 2);
            filename = `therapie_export_${Date.now()}.json`;
            type = 'application/json';
            break;
        case 'pdf':
            content = generateTextExport(exportData);
            filename = `therapie_export_${Date.now()}.txt`;
            type = 'text/plain';
            break;
        case 'docx':
            content = generateTextExport(exportData);
            filename = `therapie_export_${Date.now()}.txt`;
            type = 'text/plain';
            showToast('DOCX-Export erfordert serverseitige Konvertierung', 'info');
            break;
    }

    downloadFile(content, filename, type);
    showToast(`${format.toUpperCase()}-Export abgeschlossen`, 'success');
}

/**
 * Generate text export
 */
function generateTextExport(data) {
    let text = '=== THERAPIE TRANSKRIPTION ===\n\n';
    text += `Exportiert: ${new Date().toLocaleDateString('de-DE')}\n\n`;
    
    text += '=== TRANSKRIPT ===\n\n';
    data.transcript.forEach(entry => {
        text += `[${formatTime(entry.start || 0)}] ${entry.speaker || 'Unbekannt'}: ${entry.text}\n\n`;
    });

    if (data.analysis) {
        text += '\n=== ANALYSE ===\n\n';
        text += `Zusammenfassung: ${data.analysis.summary}\n\n`;
        
        if (data.analysis.markers?.length) {
            text += 'ATO-Marker:\n';
            data.analysis.markers.forEach(m => {
                text += `- ${m.type}: ${m.description}\n`;
            });
        }

        if (data.analysis.suggestions?.length) {
            text += '\nTherapeutische Vorschläge:\n';
            data.analysis.suggestions.forEach(s => {
                text += `- ${s}\n`;
            });
        }
    }

    return text;
}

/**
 * Download file
 */
function downloadFile(content, filename, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

/**
 * Show marker details in modal
 */
function showMarkerDetails(index) {
    const marker = AppState.analysis?.markers?.[index];
    if (!marker) return;

    elements.modalTitle.textContent = formatMarkerType(marker.type);
    elements.modalContent.innerHTML = `
        <div style="margin-bottom: 16px;">
            <span class="marker-tag ${marker.category}">${marker.category.toUpperCase()}</span>
        </div>
        <p style="margin-bottom: 16px; line-height: 1.6;">${marker.description}</p>
        <h4 style="margin-bottom: 8px;">Klinische Bedeutung</h4>
        <p style="color: var(--color-gray-600); line-height: 1.6;">${getMarkerClinicalNote(marker.type)}</p>
    `;
    openModal();
}

// === Utility Functions ===

function loadDemoData() {
    // Load demo transcript for preview
    AppState.transcript = generateDemoTranscript();
}

function generateDemoTranscript() {
    return [
        { speaker: 'Therapeut', start: 0, end: 15, text: 'Guten Tag, wie geht es Ihnen heute?' },
        { speaker: 'Patient', start: 18, end: 45, text: 'Na ja, ich weiß nicht so recht. Die letzten Tage waren wieder ziemlich schwer.' },
        { speaker: 'Therapeut', start: 48, end: 75, text: 'Erzählen Sie mir mehr darüber. Was war besonders schwer?' },
        { speaker: 'Patient', start: 78, end: 120, text: 'Ähm, also... ich fühle mich oft so, als wäre ich nicht gut genug. Mein Chef hat letztens etwas gesagt, das mich wirklich getroffen hat.' },
        { speaker: 'Therapeut', start: 123, end: 150, text: 'Das klingt belastend. Wie haben Sie darauf reagiert?' },
        { speaker: 'Patient', start: 153, end: 195, text: 'Ich habe versucht, es einfach abzuhaken, aber irgendwie... es bleibt einfach hängen, verstehen Sie? Ich grüble immer wieder darüber nach.' },
        { speaker: 'Therapeut', start: 198, end: 225, text: 'Das Grübeln kenne ich. Gibt es Situationen, in denen Sie sich sicher und ruhig fühlen?' },
        { speaker: 'Patient', start: 228, end: 270, text: 'Naja, wenn ich mit meiner Schwester spreche, das hilft mir irgendwie. Aber manchmal denke ich auch, dass ich ihr nur zur Last falle.' },
        { speaker: 'Therapeut', start: 273, end: 300, text: 'Sie sprechen von Ihrer Schwester - wie ist die Beziehung zu ihr?' },
        { speaker: 'Patient', start: 303, end: 345, text: 'Eigentlich gut, aber ich habe manchmal das Gefühl, dass sie mich nur erträgt. Ich bin nicht sicher, ob sie mich wirklich mag.' },
        { speaker: 'Therapeut', start: 348, end: 375, text: 'Diese Unsicherheit in Beziehungen scheint ein wiederkehrendes Thema zu sein.' },
        { speaker: 'Patient', start: 378, end: 420, text: 'Ja, eigentlich schon... seit meiner Kindheit fühle ich mich oft so. Meine Eltern waren sehr streng, besonders mein Vater.' },
        { speaker: 'Therapeut', start: 423, end: 450, text: 'Erzählen Sie mir mehr über Ihre Kindheit.' },
        { speaker: 'Patient', start: 453, end: 510, text: 'Es war schwer. Ich hatte immer das Gefühl, nichts richtig zu machen. Selbst jetzt, als Erwachsener, habe ich das Gefühl, ich muss immer perfekt sein, sonst bin ich wertlos.' },
        { speaker: 'Therapeut', start: 513, end: 540, text: 'Das ist ein wichtiges Thema. Dieses Gefühl von Wertlosigkeit, das Verlangen nach Perfektion - das sind Themen, die wir weiter erkunden können.' },
    ];
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function formatDuration(seconds) {
    const mins = Math.round(seconds / 60);
    return `${mins} min`;
}

function formatMarkerType(type) {
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function formatThemeName(theme) {
    return theme.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function formatTurnpointType(type) {
    const types = {
        'emotional': 'Emotional',
        'resistance': 'Widerstand',
        'defense': 'Abwehr',
        'narrative': 'Narrativ'
    };
    return types[type] || type;
}

function getMarkerIcon(category) {
    const icons = {
        'defense': '<path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/>',
        'resistance': '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
        'transference': '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
        'theme': '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>'
    };
    return icons[category] || icons['theme'];
}

function getMarkerClinicalNote(type) {
    const notes = {
        'defense_denial': 'Verleugnung ist ein primitiver Abwehrmechanismus. Der Patient weist unangenehme Realitäten zurück.',
        'defense_projection': 'Projektion schützt vor unerwünschten Impulsen, indem sie auf andere attribuiert werden.',
        'defense_rationalization': 'Rationalisierung rechtfertigt Verhaltensweisen mit logischen Erklärungen.',
        'resistance_silence': 'Schweigen kann auf Widerstand oder tiefe emotionale Verarbeitung hinweisen.',
        'resistance_topic_change': 'Themenwechsel dient der Vermeidung schwieriger Inhalte.',
        'transference_positive': 'Positive Übertragung stärkt die therapeutische Allianz.',
        'transference_negative': 'Negative Übertragung bietet Material für die Bearbeitung.',
        'theme_control': 'Kontrollbedürfnis oft aus frühem Mangel an Kontrolle.'
    };
    return notes[type] || 'Klinische Relevanz im Kontext der Therapie zu bewerten.';
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            ${type === 'success' ? '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>' : 
              type === 'error' ? '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>' :
              '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>'}
        </svg>
        <span>${message}</span>
    `;
    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function showLoading(text = 'Lädt...') {
    elements.loadingText.textContent = text;
    elements.loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    elements.loadingOverlay.style.display = 'none';
}

function openModal() {
    elements.modalOverlay.style.display = 'flex';
}

function closeModal() {
    elements.modalOverlay.style.display = 'none';
}

function handleKeyboard(e) {
    if (e.key === 'Escape') closeModal();
    if (e.key === 'Enter' && e.ctrlKey && AppState.currentView === 'transcript') {
        runAnalysis();
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', initApp);
