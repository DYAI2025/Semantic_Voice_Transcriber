#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhisperSprecherMatcher V4 - Mit emotionaler Sprachanalyse
- Extrahiert Datum/Zeit aus Audio-Dateinamen  
- Erkennt emotionale Sprachfärbung während der Transkription
- Zeigt Original-Aufnahmezeit und Emotionen im Transkript
- Nutzt vorhandene Marker-Systeme für emotionale Klassifikation
"""

import os
import sys
import subprocess
import json
import yaml
import re
import logging
import numpy as np
from pathlib import Path
from datetime import datetime
import shutil
from typing import List, Dict, Tuple, Optional, Any

# Lokales TextBlob einbinden (falls vorhanden)
textblob_local_path = Path(__file__).parent / "TextBlob" / "src"
if textblob_local_path.exists() and str(textblob_local_path) not in sys.path:
    sys.path.insert(0, str(textblob_local_path))
    print(f"✅ Lokales TextBlob eingebunden: {textblob_local_path}")

# Versuche zusätzliche Audio-Bibliotheken zu importieren
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("⚠️ Librosa nicht installiert. Audio-Feature-Extraktion limitiert.")

try:
    from svt_core.audio import ProsodyExtractor, ProsodyFeatures, ProsodyBaseline
    PROSODY_AVAILABLE = True
except ImportError:
    PROSODY_AVAILABLE = False
    print("⚠️ Prosody Extractor nicht gefunden. Prosodieanalyse deaktiviert.")

try:
    from svt_core.audio import SpeakerDiarizer
    DIARIZATION_AVAILABLE = True
except ImportError:
    DIARIZATION_AVAILABLE = False
    print("⚠️ Speaker Diarizer nicht gefunden. Pyannote-Sprechererkennung deaktiviert.")

from svt_core.audio.diarization_cpu import CPUDiarizer

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("⚠️ TextBlob nicht installiert. Sentiment-Analyse limitiert.")

# Import ATO correlation components
try:
    from ato_correlation_engine import CorrelationEngine
    from ato_correlation_types import ProsodyFeatureVector
    from ato_correlation_config import CorrelationConfig
    CORRELATION_AVAILABLE = True
except ImportError:
    CORRELATION_AVAILABLE = False
    print("⚠️ ATO Correlation Engine nicht gefunden. Korrelationsanalyse deaktiviert.")

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('transcription_v4_emotion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EmotionalAnalyzer:
    """Analysiert emotionale Sprachfärbung aus Audio und Text"""
    
    def __init__(self, confidence_threshold: float = 0.5):
        self.emotional_markers = self._load_emotional_markers()
        self.confidence_threshold = confidence_threshold
        # ADD THIS LINE:
        from prosody_analyzer import ProsodyAnalyzer
        self.prosody_analyzer = ProsodyAnalyzer()
        
    def _load_emotional_markers(self):
        """Lade emotionale Marker aus deinem bestehenden System"""
        try:
            # Lade deine emotionalen Marker aus dem bestehenden System
            marker_paths = [
                Path("../ALL_SEMANTIC_MARKER_TXT/Former_NEW_MARKER_FOLDERS/emotions"),
                Path("../Assist_TXT_marker_py: 2/resonance"),
                Path("../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01")
            ]
            
            markers = {}
            
            for marker_path in marker_paths:
                if marker_path.exists():
                    for marker_file in marker_path.glob("*.txt"):
                        emotion_name = marker_file.stem.lower()
                        try:
                            with open(marker_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                # Extrahiere Keywords aus den Marker-Dateien
                                keywords = re.findall(r'\b\w+\b', content.lower())
                                if keywords:  # Nur wenn Keywords gefunden wurden
                                    markers[emotion_name] = keywords[:20]  # Top 20 Keywords
                        except Exception as e:
                            logger.debug(f"Fehler beim Lesen von {marker_file}: {e}")
                            
            if markers:
                logger.info(f"Emotionale Marker geladen: {list(markers.keys())[:5]}...")
                return markers
            else:
                return self._create_default_emotional_markers()
                
        except Exception as e:
            logger.warning(f"Fehler beim Laden der Marker: {e}")
            return self._create_default_emotional_markers()
    
    def _create_default_emotional_markers(self):
        """Erstelle Standard-Emotionsmarker basierend auf deinen resonance-Dateien"""
        return {
            'hoffnungsvoll_antreibend': [
                'aufbruch', 'chancen', 'möglichkeiten', 'weiter', 'loslegen', 
                'positiv', 'motivierend', 'antreibend', 'energie', 'kraft'
            ],
            'neugierig_forschend': [
                'was wäre wenn', 'mal angenommen', 'zeig mir', 'experimentiere',
                'neugierig', 'interessant', 'spannend', 'frage', 'erkunden'
            ],
            'sehnsuchtsvoll_still': [
                'vermisse', 'fehlt mir', 'leere', 'sehnsucht', 'heimweh',
                'melancholisch', 'ruhig', 'zart', 'sanft', 'still'
            ],
            'traurig_reflektierend': [
                'verloren', 'schade', 'einsamkeit', 'traurig', 'leer',
                'reflektierend', 'nachdenklich', 'schwermütig', 'betrübt'
            ],
            'wuetend_rebellisch': [
                'ungerecht', 'nicht mit mir', 'kämpfen', 'widerstand', 'bullshit',
                'wütend', 'rebellisch', 'dagegen', 'aufgeladen', 'konfrontation'
            ],
            'mystisch_symbolisch': [
                'geheimnis', 'symbol', 'tor', 'schwelle', 'schlüssel',
                'verborgen', 'unsichtbar', 'schatten', 'vision', 'mystisch'
            ],
            'begeistert_enthusiastisch': [
                'fantastisch', 'wunderbar', 'begeistert', 'großartig', 'toll',
                'super', 'genial', 'wow', 'krass', 'mega', 'cool'
            ]
        }
    
    def analyze_audio_features(self, audio_path: Path) -> Dict[str, float]:
        """Analysiere Audio-Features für emotionale Erkennung"""
        if not LIBROSA_AVAILABLE:
            logger.warning("Librosa nicht verfügbar - Audio-Feature-Extraktion übersprungen")
            return {}
            
        try:
            # Lade Audio-Datei
            y, sr = librosa.load(str(audio_path), sr=22050)
            
            # Extrahiere emotionale Audio-Features
            features = {}
            
            # 1. Tempo
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            features['tempo'] = float(tempo)
            
            # 2. Spektrale Features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            features['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
            features['spectral_centroid_std'] = float(np.std(spectral_centroids))
            
            # 3. MFCC Features (wichtig für Emotion)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            for i in range(3):  # Nur die ersten 3 MFCCs für Emotion
                features[f'mfcc_{i}_mean'] = float(np.mean(mfccs[i]))
                features[f'mfcc_{i}_std'] = float(np.std(mfccs[i]))
            
            # 4. Energy und Intensität
            rms = librosa.feature.rms(y=y)[0]
            features['energy_mean'] = float(np.mean(rms))
            features['energy_std'] = float(np.std(rms))
            
            # 5. Zero Crossing Rate (Sprachfluss)
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            features['zcr_mean'] = float(np.mean(zcr))
            
            return features
            
        except Exception as e:
            logger.error(f"Fehler bei Audio-Analyse: {e}")
            return {}
    
    def analyze_text_emotion(self, text: str) -> Dict[str, any]:
        """Analysiere emotionale Färbung des Textes"""
        if not text:
            return {'dominant_emotion': 'neutral', 'emotion_scores': {}, 'valence': 0.0}
        
        text_lower = text.lower()
        emotion_scores = {}
        
        # Analysiere mit emotionalen Markern
        for emotion, keywords in self.emotional_markers.items():
            score = 0
            for keyword in keywords:
                # Exakte und partielle Matches
                if keyword in text_lower:
                    score += text_lower.count(keyword)
                # Fuzzy matching für ähnliche Wörter
                for word in text_lower.split():
                    if len(word) > 3 and keyword in word:
                        score += 0.5
            
            emotion_scores[emotion] = score
        
        # Normalisiere Scores
        total_score = sum(emotion_scores.values())
        if total_score > 0:
            emotion_scores = {k: v/total_score for k, v in emotion_scores.items()}
        
        # Finde dominante Emotion
        dominant_emotion = max(emotion_scores, key=emotion_scores.get) if emotion_scores else 'neutral'
        
        # Sentiment-Analyse mit TextBlob
        valence = 0.0
        arousal = 0.0
        subjectivity = 0.0
        
        if TEXTBLOB_AVAILABLE:
            try:
                blob = TextBlob(text)
                valence = blob.sentiment.polarity  # -1 (negativ) bis +1 (positiv)
                arousal = abs(blob.sentiment.polarity)  # Intensität
                subjectivity = blob.sentiment.subjectivity
            except:
                valence = 0.0
                arousal = 0.0
                subjectivity = 0.0
        
        return {
            'dominant_emotion': dominant_emotion,
            'emotion_scores': emotion_scores,
            'valence': valence,
            'arousal': arousal,
            'subjectivity': subjectivity
        }
    
    def classify_emotion_from_audio(self, audio_features: Dict[str, float]) -> str:
        """Klassifiziere Emotion basierend auf Audio-Features (vereinfacht)"""
        if not audio_features:
            return 'neutral'
        
        # Vereinfachte Heuristik basierend auf Audio-Features
        energy_mean = audio_features.get('energy_mean', 0)
        tempo = audio_features.get('tempo', 120)
        spectral_centroid = audio_features.get('spectral_centroid_mean', 0)
        
        # Hohe Energie + hohes Tempo = Begeistert/Wütend
        if energy_mean > 0.1 and tempo > 130:
            if spectral_centroid > 2000:  # Höhere Frequenzen
                return 'wuetend_rebellisch'
            else:
                return 'begeistert_enthusiastisch'
        
        # Niedrige Energie = Traurig/Sehnsuchtsvoll
        elif energy_mean < 0.05:
            if tempo < 100:
                return 'traurig_reflektierend'
            else:
                return 'sehnsuchtsvoll_still'
        
        # Mittlere Werte = Neugierig/Hoffnungsvoll
        elif tempo > 100:
            return 'neugierig_forschend'
        else:
            return 'hoffnungsvoll_antreibend'

    def analyze_emotion(self, text: str, audio_path: Optional[str] = None,
                       audio_data: Optional[np.ndarray] = None,
                       sr: int = 22050) -> Dict[str, Any]:
        """
        Analysiert emotionale Färbung aus Text und optionalem Audio

        Args:
            text: Transkribierter Text
            audio_path: Pfad zur Audio-Datei (optional)
            audio_data: Audio als numpy array (optional)
            sr: Sample rate

        Returns:
            Dict mit emotion, valence, confidence, text_sentiment, audio_features, prosody
        """
        result = {
            'emotion': 'neutral',
            'valence': 0.0,
            'confidence': 0.0,
            'text_sentiment': {},
            'audio_features': {},
            'prosody': {}  # ADD THIS
        }

        # Text-Sentiment-Analyse
        text_sentiment = self.analyze_text_emotion(text)
        result['text_sentiment'] = text_sentiment

        # Audio-Feature-Extraktion
        audio_features = {}
        if LIBROSA_AVAILABLE and (audio_path or audio_data is not None):
            if audio_path:
                audio_features = self.analyze_audio_features(Path(audio_path))
            elif audio_data is not None:
                audio_features = self._extract_audio_features_from_array(audio_data, sr)
            result['audio_features'] = audio_features

            # PROSODY EXTRACTION - ADD THIS BLOCK:
            try:
                if audio_data is not None:
                    prosody_features = self.prosody_analyzer.extract_prosody(audio_data, sr)
                elif audio_path:
                    prosody_features = self.prosody_analyzer.extract_from_file(audio_path)
                else:
                    prosody_features = {}
                result['prosody'] = prosody_features
            except Exception as e:
                logger.warning(f"Prosody extraction failed: {e}")
                result['prosody'] = {}

        # Kombiniere Text + Audio für Gesamtemotion
        combined_emotion = self._combine_text_audio_emotion(text_sentiment, audio_features)
        result.update(combined_emotion)

        return result

    def _extract_audio_features_from_array(self, audio_data: np.ndarray, sr: int) -> Dict[str, float]:
        """Extrahiert Audio-Features aus numpy array"""
        try:
            features = {}

            # Pitch
            pitches, magnitudes = librosa.piptrack(y=audio_data, sr=sr)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)

            if pitch_values:
                features['pitch_mean'] = float(np.mean(pitch_values))
                features['pitch_std'] = float(np.std(pitch_values))

            # Energy
            rms = librosa.feature.rms(y=audio_data)[0]
            features['energy_mean'] = float(np.mean(rms))
            features['energy_std'] = float(np.std(rms))

            # Tempo
            onset_env = librosa.onset.onset_strength(y=audio_data, sr=sr)
            tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
            features['tempo'] = float(tempo[0]) if len(tempo) > 0 else 0.0

            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sr)[0]
            features['spectral_centroid_mean'] = float(np.mean(spectral_centroids))

            return features

        except Exception as e:
            logger.error(f"Fehler bei Audio-Feature-Extraktion: {e}")
            return {}

    def _combine_text_audio_emotion(self, text_sentiment: Dict[str, Any], audio_features: Dict[str, float]) -> Dict[str, Any]:
        """Kombiniert Text- und Audio-Emotionen zu Gesamtbewertung"""
        # Get text emotion
        text_emotion = text_sentiment.get('dominant_emotion', 'neutral')
        text_valence = text_sentiment.get('valence', 0.0)

        # Get audio emotion if available
        audio_emotion = 'neutral'
        if audio_features:
            audio_emotion = self.classify_emotion_from_audio(audio_features)

        # Combine (simple weighted average for now)
        if audio_features:
            # Both text and audio available - give equal weight
            combined_emotion = text_emotion if text_valence != 0 else audio_emotion
            confidence = 0.8
        else:
            # Text only
            combined_emotion = text_emotion
            confidence = 0.6

        return {
            'emotion': combined_emotion,
            'valence': text_valence,
            'confidence': confidence
        }

# ATO Correlation functions
def apply_ato_correlations(segment: dict, engine: CorrelationEngine) -> dict:
    """Apply ATO correlations to a transcript segment."""
    if "prosody_features" not in segment:
        return segment

    prosody = segment["prosody_features"]
    features = ProsodyFeatureVector(
        pitch_deviation=prosody.get("pitch_deviation", 0),
        tempo_deviation=prosody.get("tempo_deviation", 0),
        energy_deviation=prosody.get("energy_deviation", 0),
        pause_frequency=prosody.get("pause_frequency", 0),
        pitch_variability=prosody.get("pitch_variability", 0)
    )

    predictions = engine.predict_markers(features, threshold=0.5)

    segment["ato_markers"] = [p.marker_name for p in predictions]
    segment["correlation_confidence"] = {
        p.marker_name: p.confidence for p in predictions
    }

    return segment

def generate_correlation_explanation(prediction) -> str:
    """Generate human-readable explanation for marker prediction."""
    explanation = f"{prediction.marker_name} (confidence: {prediction.confidence:.0%})"

    if prediction.contributing_features:
        top_features = sorted(
            prediction.contributing_features.items(),
            key=lambda x: x[1],
            reverse=True
        )[:2]

        feature_str = ", ".join([
            f"{feat}: {score:.2f}" for feat, score in top_features
        ])
        explanation += f" - Primary indicators: {feature_str}"

    return explanation

class WhisperSpeakerMatcherV4:
    def __init__(self, base_path=None, use_faster_whisper=True):
        if base_path is None:
            # Use current directory as default (cross-platform)
            self.base_path = Path(__file__).parent
        else:
            self.base_path = Path(base_path)

        self.eingang_path = self.base_path / "Eingang"
        self.memory_path = self.base_path / "Memory"
        self.output_path = self.base_path / "Transkripte_LLM"
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Fallback für lokale Entwicklung
        if not self.base_path.exists():
            logger.warning(f"Google Drive Pfad nicht verfügbar: {self.base_path}")
            self.base_path = Path("./whisper_speaker_matcher")
            self.eingang_path = self.base_path / "Eingang"
            self.memory_path = self.base_path / "Memory"
            self.output_path = self.base_path / "Transkripte_LLM"
            self._create_local_structure()

        self.use_faster_whisper = use_faster_whisper
        self.speakers = self._load_speaker_profiles()
        self.emotion_analyzer = EmotionalAnalyzer()

        # Add new layer flags
        self.enable_turning_points = False
        self.enable_dual_markers = False
        self.enable_enhanced_speakers = False

        # Initialize layer components
        self.turning_points_layer = None
        self.dual_marker_system = None
        self.speaker_visualizer = None
        
    def _create_local_structure(self):
        """Erstelle lokale Verzeichnisstruktur wenn Google Drive nicht verfügbar"""
        for path in [self.eingang_path, self.memory_path, self.output_path]:
            path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Lokale Struktur erstellt: {self.base_path}")
    
    def _load_speaker_profiles(self):
        """Lade bekannte Sprecher-Profile aus Memory-Ordner"""
        speakers = {}
        
        if not self.memory_path.exists():
            logger.warning(f"Memory-Pfad existiert nicht: {self.memory_path}")
            return self._create_default_speakers()
            
        for yaml_file in self.memory_path.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    profile = yaml.safe_load(f)
                    speaker_name = yaml_file.stem
                    speakers[speaker_name] = profile
                    logger.info(f"Sprecher-Profil geladen: {speaker_name}")
            except Exception as e:
                logger.error(f"Fehler beim Laden von {yaml_file}: {e}")
                
        return speakers if speakers else self._create_default_speakers()
    
    def _create_default_speakers(self):
        """Erstelle Standard-Sprecher wenn keine Profile gefunden werden"""
        return {
            'ben': {
                'name': 'Benjamin Poersch',
                'keywords': ['also', 'genau', 'interessant', 'technisch', 'system']
            },
            'ich': {
                'name': 'Ich',
                'keywords': []
            }
        }
    
    def extract_whatsapp_datetime(self, filename: str) -> Tuple[Optional[datetime], str]:
        """
        Extrahiere Datum und Zeit aus Audio-Dateinamen
        Beispiele:
        - WhatsApp Audio 2025-06-29 at 13.20.58.opus
        - 00000249-AUDIO-2025-02-28-07-05-24.opus
        """
        # Pattern für WhatsApp Dateien (Standard-Format)
        whatsapp_pattern = r'WhatsApp (?:Audio|Video) (\d{4})-(\d{2})-(\d{2}) at (\d{1,2})\.(\d{2})\.(\d{2})'
        
        match = re.search(whatsapp_pattern, filename)
        if match:
            year, month, day, hour, minute, second = match.groups()
            try:
                dt = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
                formatted_date = dt.strftime('%Y-%m-%d_%H-%M-%S')
                return dt, formatted_date
            except ValueError as e:
                logger.warning(f"Ungültiges Datum in {filename}: {e}")
        
        # Pattern für nummerierte AUDIO-Dateien (Format: XXXXXXXX-AUDIO-YYYY-MM-DD-HH-MM-SS.opus)
        audio_pattern = r'\d+-AUDIO-(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})'
        
        match = re.search(audio_pattern, filename)
        if match:
            year, month, day, hour, minute, second = match.groups()
            try:
                dt = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
                formatted_date = dt.strftime('%Y-%m-%d_%H-%M-%S')
                logger.info(f"Erkanntes Aufnahmedatum: {dt.strftime('%d.%m.%Y um %H:%M:%S')} aus Datei {filename}")
                return dt, formatted_date
            except ValueError as e:
                logger.warning(f"Ungültiges Datum in {filename}: {e}")
        
        # Fallback: Verwende Datei-Erstellungszeit
        logger.warning(f"Kein Datum im Dateinamen erkannt: {filename}")
        return None, "unbekannt"

    def get_chatpartner_from_path(self, file_path: Path) -> str:
        """Extrahiere Chatpartner aus Ordnerstruktur"""
        relative_path = file_path.relative_to(self.eingang_path)
        parts = relative_path.parts
        
        if len(parts) > 1:
            chatpartner = parts[0]
            return chatpartner.replace('_', ' ')
        
        filename = file_path.name.lower()
        for known_person in ['schroeti', 'freddy', 'marike', 'vincent', 'elke']:
            if known_person in filename:
                return known_person.title()

        return "Unbekannt"

    def transcribe_audio_standard(self, audio_path: Path) -> Optional[str]:
        """Standard Whisper Transkription"""
        try:
            whisper_cmd = self._find_whisper_command()
            
            if not whisper_cmd:
                raise Exception("Whisper nicht gefunden. Bitte installieren: pip install openai-whisper")
            
            cmd = [whisper_cmd, str(audio_path), "--language", "de", "--model", "base", "--output_format", "txt"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Whisper Fehler: {result.stderr}")
                return None
                
            # Whisper erstellt TXT im aktuellen Verzeichnis
            txt_filename = audio_path.name.replace('.opus', '.txt')
            txt_path = Path(txt_filename)
            if txt_path.exists():
                with open(txt_path, 'r', encoding='utf-8') as f:
                    transcription = f.read().strip()
                txt_path.unlink()  # Lösche temporäre Datei
                return transcription
            
            return None
                
        except Exception as e:
            logger.error(f"Transkriptions-Fehler für {audio_path}: {e}")
            return None

    def _find_whisper_command(self):
        """Finde verfügbare Whisper-Installation"""
        possible_commands = ['whisper', 'python -m whisper', 'python3 -m whisper']
        
        for cmd in possible_commands:
            try:
                result = subprocess.run(cmd.split() + ['--help'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return cmd.split()[0] if len(cmd.split()) == 1 else cmd
            except:
                continue
        return None

    def identify_speaker_in_conversation(self, transcription: str, chatpartner: str) -> List[Tuple[str, str]]:
        """Identifiziere Sprecher in der Konversation"""
        transcription_lower = transcription.lower()
        
        my_indicators = ['ich schicke', 'ich sende', 'hier ist', 'ich wollte', 'von mir', 'meine']
        is_my_message = any(indicator in transcription_lower for indicator in my_indicators)
        
        if is_my_message:
            speaker = "Ich"
        else:
            speaker = chatpartner
        
        return [(speaker, transcription)]

    def format_for_llm_with_emotion(self, chatpartner: str, conversation_parts: List[Tuple[str, str]], 
                                  audio_file: Path, recording_datetime: Optional[datetime], 
                                  processing_time: datetime, emotion_analysis: Dict) -> str:
        """Formatiere Transkription für optimale LLM-Verarbeitung mit emotionaler Analyse"""
        
        if recording_datetime:
            recording_str = recording_datetime.strftime('%d.%m.%Y um %H:%M:%S')
            recording_date = recording_datetime.strftime('%Y-%m-%d')
            recording_time = recording_datetime.strftime('%H:%M:%S')
        else:
            recording_str = "Unbekannt"
            recording_date = "Unbekannt"
            recording_time = "Unbekannt"
        
        # Emotionale Zusammenfassung
        emotion_summary = self._format_emotion_summary(emotion_analysis)
        
        output = f"""# WhatsApp Audio Transkription mit emotionaler Analyse

**Chat mit:** {chatpartner}
**Aufnahme am:** {recording_str}
**Verarbeitet am:** {processing_time.strftime('%d.%m.%Y um %H:%M:%S')}
**Original-Datei:** {audio_file.name}

## Zeitstempel:
- **Aufnahme-Datum:** {recording_date}
- **Aufnahme-Uhrzeit:** {recording_time}
- **Verarbeitungszeit:** {processing_time.strftime('%Y-%m-%d %H:%M:%S')}

## 🎭 Emotionale Analyse:
{emotion_summary}

## Transkription:

"""
        
        for speaker, text in conversation_parts:
            # Füge emotionale Marker zur Transkription hinzu
            emotion_marker = self._get_emotion_marker_for_text(text, emotion_analysis)
            
            if speaker == "Ich":
                output += f"**[Ich - {recording_time}]{emotion_marker}:** {text}\n\n"
            else:
                output += f"**[{speaker} - {recording_time}]{emotion_marker}:** {text}\n\n"
        
        output += f"""## Kontext für LLM:
Diese Nachricht wurde am {recording_str} in einem WhatsApp-Chat zwischen mir und {chatpartner} aufgenommen.

### Emotionale Einordnung:
Die Sprachanalyse zeigt {emotion_analysis.get('dominant_emotion', 'neutrale')} emotionale Färbung mit einer Valenz von {emotion_analysis.get('valence', 0):.2f} (Positivität/Negativität) und einer Intensität von {emotion_analysis.get('arousal', 0):.2f}.

---
*Transkribiert mit WhisperSprecherMatcher V4 (Emotion) am {processing_time.strftime('%d.%m.%Y um %H:%M:%S')}*
"""
        
        return output
    
    def _format_emotion_summary(self, emotion_analysis: Dict) -> str:
        """Formatiere emotionale Analyse für das Transkript"""
        dominant = emotion_analysis.get('dominant_emotion', 'neutral')
        valence = emotion_analysis.get('valence', 0)
        arousal = emotion_analysis.get('arousal', 0)
        scores = emotion_analysis.get('emotion_scores', {})
        
        # Deutsche Übersetzungen
        emotion_translations = {
            'hoffnungsvoll_antreibend': 'Hoffnungsvoll & Antreibend',
            'neugierig_forschend': 'Neugierig & Forschend', 
            'sehnsuchtsvoll_still': 'Sehnsuchtsvoll & Still',
            'traurig_reflektierend': 'Traurig & Reflektierend',
            'wuetend_rebellisch': 'Wütend & Rebellisch',
            'mystisch_symbolisch': 'Mystisch & Symbolisch',
            'begeistert_enthusiastisch': 'Begeistert & Enthusiastisch',
            'neutral': 'Neutral'
        }
        
        summary = f"""
**Dominante Emotion:** {emotion_translations.get(dominant, dominant)}
**Emotionale Valenz:** {valence:.2f} (Positivität: -1 bis +1)
**Emotionale Intensität:** {arousal:.2f} (Aufregung/Energie)

**Top Emotionen erkannt:**"""

        # Zeige Top 3 Emotionen
        top_emotions = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
        for emotion, score in top_emotions:
            if score > 0:
                emotion_name = emotion_translations.get(emotion, emotion)
                percentage = score * 100
                summary += f"\n- {emotion_name}: {percentage:.1f}%"
        
        return summary
    
    def _get_emotion_marker_for_text(self, text: str, emotion_analysis: Dict) -> str:
        """Generiere emotionalen Marker für die Transkription"""
        dominant = emotion_analysis.get('dominant_emotion', 'neutral')
        valence = emotion_analysis.get('valence', 0)
        
        # Emoji-Mapping für emotionale Marker
        emotion_emojis = {
            'hoffnungsvoll_antreibend': ' 🚀',
            'neugierig_forschend': ' 🔍',
            'sehnsuchtsvoll_still': ' 🌙',
            'traurig_reflektierend': ' 😔',
            'wuetend_rebellisch': ' ⚡',
            'mystisch_symbolisch': ' ✨',
            'begeistert_enthusiastisch': ' 🎉',
            'neutral': ''
        }
        
        emoji = emotion_emojis.get(dominant, '')
        
        # Zusätzliche Valenz-Indikatoren
        if valence > 0.3:
            emoji += ' +'
        elif valence < -0.3:
            emoji += ' -'
            
        return emoji

    def get_sorted_audio_files(self) -> List[Path]:
        """Hole alle OPUS-Dateien sortiert nach Datum"""
        if not self.eingang_path.exists():
            logger.error(f"Eingang-Ordner nicht gefunden: {self.eingang_path}")
            return []

        all_opus_files = list(self.eingang_path.rglob("*.opus"))

        def sort_by_whatsapp_date(file_path):
            dt, _ = self.extract_whatsapp_datetime(file_path.name)
            return dt if dt else datetime.fromtimestamp(file_path.stat().st_mtime)

        all_opus_files.sort(key=sort_by_whatsapp_date, reverse=True)

        return all_opus_files

    def process_audio_files(self):
        """Verarbeite alle OPUS Audio-Dateien mit emotionaler Analyse"""

        audio_files = self.get_sorted_audio_files()
        logger.info(f"Gefunden: {len(audio_files)} OPUS-Dateien")
        
        processed_count = 0
        for audio_file in audio_files:
            try:
                recording_datetime, formatted_date = self.extract_whatsapp_datetime(audio_file.name)
                chatpartner = self.get_chatpartner_from_path(audio_file)
                
                if recording_datetime:
                    output_filename = f"{formatted_date}_{chatpartner.replace(' ', '_')}_{audio_file.stem}_emotion_transkript.md"
                else:
                    output_filename = f"{chatpartner.replace(' ', '_')}_{audio_file.stem}_emotion_transkript.md"
                
                output_path = self.output_path / output_filename
                
                if output_path.exists():
                    logger.info(f"Bereits verarbeitet: {audio_file.name}")
                    continue
                
                if recording_datetime:
                    logger.info(f"Verarbeite: {audio_file.name} (Chat mit {chatpartner}, aufgenommen am {recording_datetime.strftime('%d.%m.%Y um %H:%M')})")
                else:
                    logger.info(f"Verarbeite: {audio_file.name} (Chat mit {chatpartner})")
                
                # 1. Audio transkribieren
                transcription = self.transcribe_audio_standard(audio_file)
                
                if not transcription:
                    logger.warning(f"Keine Transkription erhalten für {audio_file.name}")
                    continue
                
                # 2. Emotionale Analyse
                logger.info(f"🎭 Analysiere emotionale Sprachfärbung...")
                
                # Audio-Features analysieren
                audio_features = self.emotion_analyzer.analyze_audio_features(audio_file)
                
                # Text-Emotion analysieren
                text_emotion = self.emotion_analyzer.analyze_text_emotion(transcription)
                
                # Audio-Emotion klassifizieren
                audio_emotion = self.emotion_analyzer.classify_emotion_from_audio(audio_features)
                
                # Kombiniere beide Analysen
                emotion_analysis = {
                    'dominant_emotion': text_emotion['dominant_emotion'],  # Priorität auf Text
                    'audio_emotion': audio_emotion,
                    'emotion_scores': text_emotion['emotion_scores'],
                    'valence': text_emotion['valence'],
                    'arousal': text_emotion['arousal'],
                    'audio_features': audio_features
                }
                
                logger.info(f"🎭 Emotionale Färbung: {emotion_analysis['dominant_emotion']} (Valenz: {emotion_analysis['valence']:.2f})")
                
                # 3. Sprecher identifizieren
                conversation_parts = self.identify_speaker_in_conversation(transcription, chatpartner)
                
                # 4. Formatiere für LLM mit emotionaler Analyse
                processing_time = datetime.now()
                llm_formatted = self.format_for_llm_with_emotion(chatpartner, conversation_parts, 
                                                               audio_file, recording_datetime, 
                                                               processing_time, emotion_analysis)
                
                # 5. Speichere Transkript
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(llm_formatted)
                
                processed_count += 1
                logger.info(f"✅ Verarbeitet: {audio_file.name} -> {output_filename}")
                
                progress = (audio_files.index(audio_file) + 1) / len(audio_files) * 100
                logger.info(f"Fortschritt: {progress:.1f}% ({audio_files.index(audio_file) + 1}/{len(audio_files)})")
                
            except Exception as e:
                logger.error(f"Fehler bei {audio_file.name}: {e}")
                continue
        
        logger.info(f"Verarbeitung abgeschlossen. {processed_count} neue Dateien verarbeitet.")

def transcribe_with_whisper(
    audio_path: str,
    model_size: str = 'base',
    language: str = 'de',
    use_intelligent_pipeline: bool = False,
    quality_score: Optional[float] = None,
    quality_analyzer: Optional[Any] = None,
    audio_preprocessor: Optional[Any] = None,
    extract_prosody: bool = False,
    enable_diarization: bool = False,
    hf_token: Optional[str] = None,
    num_speakers: Optional[int] = None,
    enable_overlap_detection: bool = False,
    osd_min_duration: float = 0.5,
    use_audio_chunking: bool = True,  # NEW PARAMETER
    chunk_duration: float = 300.0,    # NEW PARAMETER (5 minutes default)
    overlap_duration: float = 5.0     # NEW PARAMETER (5 seconds default)
) -> Dict[str, Any]:
    """
    Transkribiert Audio mit Whisper und extrahiert Confidence Scores

    Args:
        audio_path: Pfad zur Audio-Datei
        model_size: Whisper-Modell (tiny, base, small, medium, large)
        language: Sprache (de, en, etc.)
        use_intelligent_pipeline: Enable quality-based preprocessing
        quality_score: Pre-calculated quality score (0-1)
        quality_analyzer: AudioQualityAnalyzer instance
        audio_preprocessor: AudioPreprocessor instance
        extract_prosody: Extract prosodic features (tempo, pitch, energy, pauses)
        enable_diarization: Enable automatic speaker diarization (Speaker A, B, C, ...)
        hf_token: Hugging Face token for pyannote.audio (required for diarization/OSD)
        num_speakers: Fixed number of speakers (None for auto-detect)
        enable_overlap_detection: Enable overlapped speech detection
        osd_min_duration: Minimum duration (seconds) for overlap regions
        use_audio_chunking: Enable chunking for large files to reduce memory usage
        chunk_duration: Duration of each chunk in seconds (when chunking enabled)
        overlap_duration: Duration of overlap between chunks in seconds (when chunking enabled)

    Returns:
        Dict mit text, segments, confidence_scores, prosody_features/baseline,
        speaker_labels, und overlapped_speech
    """
    try:
        import whisper
        import librosa
        import soundfile as sf
        import tempfile
        from pathlib import Path

        # Check if the audio file is large and should be chunked to reduce memory usage
        audio_duration = librosa.get_duration(path=audio_path)
        
        # Only apply chunking if enabled and the audio is longer than the chunk size
        if use_audio_chunking and audio_duration > chunk_duration:
            logger.info(f"Audio file is {audio_duration:.2f}s long, using chunking (chunk size: {chunk_duration}s)")
            
            # Import the chunker
            from audio_chunker import process_large_audio_with_chunking
            
            # Prepare the transcribe function with all parameters except the audio path
            def chunk_transcribe_func(chunk_path, **kwargs):
                # Call current function but disable chunking for the chunks
                return transcribe_with_whisper(
                    chunk_path,
                    model_size=model_size,
                    language=language,
                    use_intelligent_pipeline=use_intelligent_pipeline,
                    quality_score=quality_score,
                    quality_analyzer=quality_analyzer,
                    audio_preprocessor=audio_preprocessor,
                    extract_prosody=extract_prosody,
                    enable_diarization=enable_diarization,
                    hf_token=hf_token,
                    num_speakers=num_speakers,
                    enable_overlap_detection=enable_overlap_detection,
                    osd_min_duration=osd_min_duration,
                    use_audio_chunking=False,  # Disable chunking for chunks
                    chunk_duration=chunk_duration,
                    overlap_duration=overlap_duration,
                    **kwargs
                )
            
            # Process the large audio file using chunking
            return process_large_audio_with_chunking(
                audio_path,
                chunk_transcribe_func,
                chunk_duration=chunk_duration,
                overlap_duration=overlap_duration,
                cleanup_memory=True  # Enable memory cleanup between chunks
            )

        # Apply intelligent preprocessing if enabled
        audio_file_to_transcribe = audio_path
        temp_file_created = False

        if use_intelligent_pipeline and quality_score is not None and audio_preprocessor is not None:
            logger.info(f"Applying intelligent preprocessing (quality: {quality_score:.2f})")

            # Load audio
            audio, sample_rate = librosa.load(audio_path, sr=16000, mono=True)

            # Preprocess based on quality score
            audio = audio_preprocessor.preprocess_adaptive(audio, sample_rate, quality_score)

            # Save preprocessed audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_path = tmp_file.name
                sf.write(tmp_path, audio, sample_rate)
                audio_file_to_transcribe = tmp_path
                temp_file_created = True

        logger.info(f"Lade Whisper-Modell: {model_size}")
        model = whisper.load_model(model_size)

        logger.info(f"Transkribiere: {audio_path}")
        result = model.transcribe(
            audio_file_to_transcribe,
            language=language,
            verbose=False,
            word_timestamps=True  # Enable word-level timestamps
        )

        # Clean up model from memory to reduce memory consumption
        del model
        import gc
        gc.collect()
        gc.collect()  # Run twice for thorough cleanup

        # Clear PyTorch CUDA cache if available
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                logger.debug("Cleared CUDA cache after transcription")
        except ImportError:
            # torch is not installed; skipping CUDA cache cleanup
            pass

        logger.debug("Whisper model deleted and memory cleaned")
        
        # Clean up temp file if created
        if temp_file_created:
            try:
                Path(audio_file_to_transcribe).unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"Could not delete temp file: {e}")

        # EXTRACT CONFIDENCE SCORES
        confidence_scores = _extract_confidence_scores(result)

        # EXTRACT PROSODY FEATURES (Phase 1: Big 4)
        prosody_features = []
        prosody_baseline = None

        if extract_prosody and PROSODY_AVAILABLE:
            try:
                logger.info("🎵 Extrahiere Prosodiemerkmale...")
                extractor = ProsodyExtractor(sample_rate=16000)

                # Extract from original audio file (not preprocessed temp file)
                prosody_features, prosody_baseline = extractor.extract_from_segments(
                    audio_path,  # Use original file
                    result.get('segments', []),
                    calculate_baseline=True
                )

                # Convert to dict for JSON serialization
                prosody_features = [f.to_dict() for f in prosody_features]
                if prosody_baseline:
                    prosody_baseline = prosody_baseline.to_dict()

                logger.info(f"✅ Prosodieanalyse abgeschlossen: {len(prosody_features)} Segmente")

            except Exception as e:
                logger.error(f"Fehler bei Prosodieextraktion: {e}")

        # SPEAKER DIARIZATION (Phase 2b)
        speaker_segments = []
        aligned_segments = result.get('segments', [])
        speaker_stats = {}

        if enable_diarization:
            diarization_used = False
            if DIARIZATION_AVAILABLE and hf_token:
                try:
                    logger.info("🎤 Starte Sprechererkennung (pyannote)...")
                    diarizer = SpeakerDiarizer(
                        use_auth_token=hf_token,
                        min_speakers=1,
                        max_speakers=10
                    )

                    speaker_segments = diarizer.diarize(
                        Path(audio_path),
                        num_speakers=num_speakers
                    )
                    aligned_segments = diarizer.align_with_transcription(
                        speaker_segments,
                        result.get('segments', [])
                    )
                    speaker_stats = SpeakerDiarizer.get_speaker_statistics(speaker_segments)
                    diarization_used = True
                except Exception as e:
                    logger.error(f"Fehler bei Sprechererkennung: {e}")
                    logger.warning("Fortfahren ohne pyannote, versuche CPU-Fallback...")

            if not diarization_used:
                try:
                    logger.info("🎤 Starte Sprechererkennung (CPU-Fallback)...")
                    cpu_diarizer = CPUDiarizer()
                    speaker_segments = cpu_diarizer.diarize(Path(audio_path))
                    aligned_segments = cpu_diarizer.align_with_transcription(
                        speaker_segments,
                        result.get('segments', [])
                    )
                    speaker_stats = cpu_diarizer.get_speaker_statistics(speaker_segments)
                    diarization_used = True
                except Exception as e:
                    logger.error(f"CPU-Diarisierung fehlgeschlagen: {e}")

            if diarization_used and speaker_stats:
                logger.info(f"✅ Sprechererkennung abgeschlossen: {len(speaker_stats)} Sprecher gefunden")
                for speaker, stats in speaker_stats.items():
                    logger.info(
                        f"  - {speaker}: {stats['total_duration']:.1f}s "
                        f"({stats.get('percentage', 0):.1f}%) - {stats['num_segments']} Segmente"
                    )
            elif enable_diarization:
                logger.warning("Fortfahren ohne Sprechererkennung...")

        # OVERLAPPED SPEECH DETECTION (Phase 2c)
        overlapped_speech = []

        if enable_overlap_detection and DIARIZATION_AVAILABLE:
            try:
                logger.info("🔊 Starte Overlapped Speech Detection...")
                diarizer = SpeakerDiarizer(
                    use_auth_token=hf_token,
                    min_speakers=1,
                    max_speakers=10
                )

                # Run OSD
                overlapped_speech = diarizer.detect_overlapped_speech(
                    Path(audio_path),
                    min_duration_on=osd_min_duration,
                    min_duration_off=0.3  # Fill gaps shorter than 300ms
                )

                # Mark segments that have overlaps
                aligned_segments = _mark_overlapped_segments(
                    aligned_segments,
                    overlapped_speech
                )

                logger.info(
                    f"✅ OSD abgeschlossen: {len(overlapped_speech)} "
                    f"Überlappungsbereiche gefunden"
                )

            except Exception as e:
                logger.error(f"Fehler bei Overlapped Speech Detection: {e}")
                logger.warning("Fortfahren ohne OSD...")

        return {
            'text': result['text'],
            'segments': aligned_segments,  # Use aligned segments with speaker labels
            'confidence_scores': confidence_scores,
            'prosody_features': prosody_features,
            'prosody_baseline': prosody_baseline,
            'speaker_segments': speaker_segments,  # Raw diarization output
            'overlapped_speech': overlapped_speech  # OSD regions
        }

    except Exception as e:
        logger.error(f"Fehler bei Transkription: {e}")
        return {
            'text': '',
            'segments': [],
            'confidence_scores': {
                'overall_confidence': 0.0,
                'segments': [],
                'low_confidence_segments': []
            },
            'prosody_features': [],
            'prosody_baseline': None,
            'speaker_segments': [],
            'overlapped_speech': []
        }

def _extract_confidence_scores(whisper_result: Dict[str, Any],
                               low_confidence_threshold: float = 0.5) -> Dict[str, Any]:
    """
    Extrahiert Confidence Scores aus Whisper-Ergebnis

    Args:
        whisper_result: Whisper transcribe() Ergebnis
        low_confidence_threshold: Schwellwert für niedrige Confidence

    Returns:
        Dict mit confidence-Informationen
    """
    segments = whisper_result.get('segments', [])

    segment_confidences = []
    low_confidence_segments = []
    total_confidence = 0.0

    for seg in segments:
        # Whisper gibt avg_logprob (negative log probability)
        # Konvertiere zu 0-1 Confidence Score
        avg_logprob = seg.get('avg_logprob', -1.0)
        no_speech_prob = seg.get('no_speech_prob', 0.0)

        # Heuristik: exp(avg_logprob) gibt ungefähre Wahrscheinlichkeit
        # Adjustiere mit no_speech_prob
        confidence = min(1.0, max(0.0, np.exp(avg_logprob) * (1 - no_speech_prob)))

        segment_info = {
            'text': seg.get('text', '').strip(),
            'start': seg.get('start', 0.0),
            'end': seg.get('end', 0.0),
            'confidence': float(confidence),
            'avg_logprob': float(avg_logprob),
            'no_speech_prob': float(no_speech_prob)
        }

        segment_confidences.append(segment_info)
        total_confidence += confidence

        # Mark low confidence segments
        if confidence < low_confidence_threshold:
            low_confidence_segments.append(segment_info)

    overall_confidence = total_confidence / len(segments) if segments else 0.0

    return {
        'overall_confidence': float(overall_confidence),
        'segments': segment_confidences,
        'low_confidence_segments': low_confidence_segments,
        'low_confidence_threshold': low_confidence_threshold,
        'total_segments': len(segments)
    }

def _mark_overlapped_segments(
    segments: List[Dict[str, Any]],
    overlaps: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Mark transcription segments that contain overlapped speech

    Args:
        segments: Whisper transcription segments
        overlaps: OSD overlap segments

    Returns:
        Segments with added 'has_overlap' and 'overlap_duration' fields
    """
    for seg in segments:
        seg_start = seg.get('start', 0.0)
        seg_end = seg.get('end', 0.0)

        # Check overlap with OSD regions
        total_overlap = 0.0
        has_overlap = False

        for overlap in overlaps:
            ovl_start = overlap['start']
            ovl_end = overlap['end']

            # Calculate intersection
            intersection_start = max(seg_start, ovl_start)
            intersection_end = min(seg_end, ovl_end)
            intersection = max(0, intersection_end - intersection_start)

            if intersection > 0:
                has_overlap = True
                total_overlap += intersection

        seg['has_overlap'] = has_overlap
        seg['overlap_duration'] = total_overlap

    return segments

def mark_low_confidence_segments(transcription_result: Dict[str, Any]) -> str:
    """
    Markiert Segmente mit niedriger Confidence im Text

    Args:
        transcription_result: Ergebnis von transcribe_with_whisper

    Returns:
        Text mit Markierungen für unsichere Stellen
    """
    text = transcription_result.get('text', '')
    confidence_scores = transcription_result.get('confidence_scores', {})

    # Get all segments
    segments = confidence_scores.get('segments', [])
    if not segments:
        return text

    # Erstelle markierten Text
    marked_text = text

    # Sortiere Segmente nach Position (rückwärts für korrekte String-Insertion)
    sorted_segments = sorted(
        segments,
        key=lambda s: s['start'],
        reverse=True
    )

    for seg in sorted_segments:
        if seg['confidence'] < confidence_scores.get('low_confidence_threshold', 0.5):
            # Finde Segment im Text
            seg_text = seg['text'].strip()
            if seg_text in marked_text:
                # Markiere mit Confidence Score
                marker = f" [UNSICHER:{seg['confidence']:.2f}]"
                marked_text = marked_text.replace(seg_text, seg_text + marker, 1)

    return marked_text

def main():
    """Hauptfunktion"""
    print("🎤🎭 WhisperSprecherMatcher V4 mit emotionaler Analyse gestartet...")
    print("Mit Datum/Zeit-Extraktion und emotionaler Sprachfärbung")
    
    import argparse
    parser = argparse.ArgumentParser(description="WhisperSprecherMatcher V4 (Emotion)")
    parser.add_argument("--local", action="store_true", help="Verwende lokalen Pfad")
    
    args = parser.parse_args()
    
    try:
        if args.local:
            matcher = WhisperSpeakerMatcherV4(base_path=".")
        else:
            matcher = WhisperSpeakerMatcherV4()
        
        matcher.process_audio_files()
        print("✅ Verarbeitung erfolgreich abgeschlossen!")
        print(f"📁 Transkripte mit emotionaler Analyse gespeichert in: {matcher.output_path}")
        
    except Exception as e:
        logger.error(f"Kritischer Fehler: {e}")
        print(f"❌ Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
