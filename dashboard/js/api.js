/**
 * SVT Dashboard API
 * API-Integration für das Therapeuten-Dashboard
 */

class SVTAPI {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
    }

    // Setze die Base URL
    setBaseUrl(url) {
        this.baseUrl = url;
    }

    // Generic API call
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }

    // === Transkription ===

    /**
     * Transkription starten
     */
    async transcribe(audioFile, onProgress) {
        const formData = new FormData();
        formData.append('audio', audioFile);

        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable && onProgress) {
                    const percent = Math.round((e.loaded / e.total) * 100);
                    onProgress('upload', percent);
                }
            });

            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    try {
                        const result = JSON.parse(xhr.responseText);
                        resolve(result);
                    } catch (e) {
                        reject(new Error('Invalid JSON response'));
                    }
                } else {
                    reject(new Error(`Upload failed: ${xhr.statusText}`));
                }
            });

            xhr.addEventListener('error', () => {
                reject(new Error('Network error'));
            });

            xhr.open('POST', `${this.baseUrl}/api/transcribe`);
            xhr.send(formData);
        });
    }

    /**
     * Transkription mit Prosodie
     */
    async transcribeWithProsody(audioFile, onProgress) {
        const formData = new FormData();
        formData.append('audio', audioFile);
        formData.append('prosody', 'true');

        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable && onProgress) {
                    const percent = Math.round((e.loaded / e.total) * 100);
                    onProgress('upload', percent);
                }
            });

            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    try {
                        const result = JSON.parse(xhr.responseText);
                        resolve(result);
                    } catch (e) {
                        reject(new Error('Invalid JSON response'));
                    }
                } else {
                    reject(new Error(`Upload failed: ${xhr.statusText}`));
                }
            });

            xhr.open('POST', `${this.baseUrl}/api/transcribe`);
            xhr.send(formData);
        });
    }

    /**
     * Transkription Status abfragen
     */
    async getTranscriptionStatus(jobId) {
        return this.request(`/api/transcribe/status/${jobId}`);
    }

    // === Analyse ===

    /**
     * Therapie-Analyse starten
     */
    async analyzeTranscript(transcriptData, options = {}) {
        return this.request('/api/analyze', {
            method: 'POST',
            body: JSON.stringify({
                transcript: transcriptData,
                options: options
            })
        });
    }

    /**
     * Analyse-Status abfragen
     */
    async getAnalysisStatus(jobId) {
        return this.request(`/api/analyze/status/${jobId}`);
    }

    // === Wendepunkte ===

    /**
     * Wendepunkte analysieren
     */
    async detectTurnpoints(transcriptData) {
        return this.request('/api/turnpoints', {
            method: 'POST',
            body: JSON.stringify(transcriptData)
        });
    }

    // === Export ===

    /**
     * PDF Export
     */
    async exportPDF(transcriptData, analysisData) {
        return this.request('/api/export/pdf', {
            method: 'POST',
            body: JSON.stringify({
                transcript: transcriptData,
                analysis: analysisData
            })
        });
    }

    /**
     * DOCX Export
     */
    async exportDOCX(transcriptData, analysisData) {
        return this.request('/api/export/docx', {
            method: 'POST',
            body: JSON.stringify({
                transcript: transcriptData,
                analysis: analysisData
            })
        });
    }

    /**
     * JSON Export
     */
    async exportJSON(transcriptData, analysisData) {
        return this.request('/api/export/json', {
            method: 'POST',
            body: JSON.stringify({
                transcript: transcriptData,
                analysis: analysisData
            })
        });
    }

    // === Lokale Verarbeitung (Fallback) ===

    /**
     * Führe lokale Transkription durch (Web Speech API als Fallback)
     */
    async localTranscribe(audioBlob) {
        // Web Speech API kann nur Live-Audio, nicht Dateien
        // Dies ist ein Placeholder für zukünftige lokale Whisper-Integration
        console.warn('Local transcription requires WebAssembly Whisper');
        throw new Error('Local transcription not yet implemented');
    }

    /**
     * Analysiere Transkript lokal (regelbasiert)
     */
    analyzeLocally(transcriptData) {
        const markers = [];
        const text = transcriptData.map(e => e.text).join(' ').toLowerCase();
        
        // Comprehensive Defensive Patterns with clinical descriptions
        const defensePatterns = {
            'denial': { pattern: /\b(nicht wahr|stimmt nicht|leugnen|das stimmt|überhaupt nicht|nieee)\b/gi, desc: 'Verleugnung' },
            'projection': { pattern: /\b(der andere|die anderen|schuld ist|fremd|der chef|meine mutter|er/sie)\b/gi, desc: 'Projektion' },
            'rationalization': { pattern: /\b(eigentlich|logisch|vernünftig|betrachtet|ja aber|also|von wegen)\b/gi, desc: 'Rationalisierung' },
            'displacement': { pattern: /\b(egal|hauptsache|nebensächlich|anderen geht es|anderes)\b/gi, desc: 'Verschiebung' }
        };

        // Resistance Patterns
        const resistancePatterns = {
            'silence': { pattern: /\b(\.\.\.|schweigen|stille|pause)\b/gi, desc: 'Schweigen' },
            'topic_change': { pattern: /\b(übrigens|nebenbei|主题wechsel|was noch|anderes thema)\b/gi, desc: 'Themenwechsel' },
            'humor': { pattern: /\b(lachen muss|witzig|lustig|ha ha|ähaha|scherz)\b/gi, desc: 'Humor' },
            'hesitation': { pattern: /\b(na ja|weiß nicht|keine ahnung|vielleicht|äh)\b/gi, desc: 'Zögern' }
        };

        // Transference Patterns
        const transferencePatterns = {
            'positive': { pattern: /\b(vertrauen|glauben|hilfreich|danke|besser|sie verstehen)\b/gi, desc: 'Positive Übertragung' },
            'negative': { pattern: /\b(schwierig|unangenehm|nicht hilfreich|traue nicht|problem)\b/gi, desc: 'Negative Übertragung' },
            'dependency': { pattern: /\b(immer|nur|ohne sie|brauche|allein nicht|brauch)\b/gi, desc: 'Abhängigkeit' }
        };

        // Theme Patterns
        const themePatterns = {
            'separation_anxiety': { pattern: /\b(allein|verlassen|verloren|trennung|alleine sein|allein zu hause)\b/gi, desc: 'Trennungsangst' },
            'control': { pattern: /\b(kontrolle|muss|muessen|bestimmen|alles unter|müssen)\b/gi, desc: 'Kontrollbedürfnis' },
            'abandonment': { pattern: /\b(verlassen|allein gelassen|niemand|nie|verlassen werden|alleine)\b/gi, desc: 'Verlassenheitsangst' },
            'shame_guilt': { pattern: /\b(schuld|scham|peinlich|falsch|schäme|schäm mich|blamiert)\b/gi, desc: 'Scham/Schuld' },
            'self_worth': { pattern: /\b(nicht gut|genug|wertlos|nicht wert|versagen|versagt)\b/gi, desc: 'Selbstwert' }
        };

        // Scan for markers with unique detection
        const foundMarkers = new Set();
        
        Object.entries(defensePatterns).forEach(([type, config]) => {
            const matches = text.match(config.pattern);
            if (matches && !foundMarkers.has(`defense_${type}`)) {
                markers.push({
                    type: `defense_${type}`,
                    category: 'defense',
                    description: `${config.desc} erkannt`,
                    count: matches ? matches.length : 0
                });
                foundMarkers.add(`defense_${type}`);
            }
        });

        Object.entries(resistancePatterns).forEach(([type, config]) => {
            const matches = text.match(config.pattern);
            if (matches && !foundMarkers.has(`resistance_${type}`)) {
                markers.push({
                    type: `resistance_${type}`,
                    category: 'resistance',
                    description: `${config.desc} erkannt`,
                    count: matches ? matches.length : 0
                });
                foundMarkers.add(`resistance_${type}`);
            }
        });

        Object.entries(transferencePatterns).forEach(([type, config]) => {
            const matches = text.match(config.pattern);
            if (matches && !foundMarkers.has(`transference_${type}`)) {
                markers.push({
                    type: `transference_${type}`,
                    category: 'transference',
                    description: `${config.desc} erkannt`,
                    count: matches ? matches.length : 0
                });
                foundMarkers.add(`transference_${type}`);
            }
        });

        return {
            markers,
            themes: Object.keys(themePatterns).filter(t => themePatterns[t].pattern.test(text)),
            suggestions: this.generateSuggestions(markers),
            summary: this.generateSummary(transcriptData)
        };
    }

    /**
     * Generiere therapeutische Vorschläge basierend auf Markern
     */
    generateSuggestions(markers) {
        const suggestions = [];
        const categories = markers.map(m => m.category);
        
        if (categories.includes('defense')) {
            suggestions.push('Patient zeigt Abwehrmechanismen. Sanfte Konfrontation empfohlen.');
        }
        if (categories.includes('resistance')) {
            suggestions.push('Widerstand erkannt. Zeit lassen und nicht drängen.');
        }
        if (categories.includes('transference_positive')) {
            suggestions.push('Positive Übertragung. Dies für die therapeutische Beziehung nutzen.');
        }
        if (categories.includes('transference_negative')) {
            suggestions.push('Negative Übertragung besprechen. Beziehungsthema adressieren.');
        }
        
        return suggestions;
    }

    /**
     * Generiere einfache Zusammenfassung
     */
    generateSummary(transcriptData) {
        if (!transcriptData || transcriptData.length === 0) {
            return 'Keine Transkriptionsdaten verfügbar.';
        }

        const therapistEntries = transcriptData.filter(e => 
            e.speaker?.toLowerCase().includes('therapist') || 
            e.speaker?.toLowerCase().includes('arzt') ||
            e.speaker?.toLowerCase().includes('t')
        );

        const patientEntries = transcriptData.filter(e => 
            e.speaker?.toLowerCase().includes('patient') || 
            e.speaker?.toLowerCase().includes('klient') ||
            e.speaker?.toLowerCase().includes('p')
        );

        const totalDuration = transcriptData.reduce((acc, e) => {
            return acc + ((e.end || 0) - (e.start || 0));
        }, 0);

        return `Sitzung mit ${transcriptData.length} Beiträgen. ` +
               `Therapeut: ${therapistEntries.length} Beiträge, ` +
               `Patient: ${patientEntries.length} Beiträge. ` +
               `Gesamtdauer: ${Math.round(totalDuration / 60)} Minuten.`;
    }
}

// Export globally
window.SVTAPI = SVTAPI;
