#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Builder aus Transkriptionen
Analysiert vorhandene Transkriptionen und baut/aktualisiert Sprecher-Memory-Profile
"""

import os
import sys
import yaml
import re
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, Any
import json

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MemoryBuilder:
    def __init__(self, base_path=None):
        if base_path is None:
            # Use current directory as default (cross-platform)
            self.base_path = Path(__file__).parent
        else:
            self.base_path = Path(base_path)
        
        # Fallback für lokale Entwicklung
        if not self.base_path.exists():
            logger.warning(f"Google Drive Pfad nicht verfügbar: {self.base_path}")
            self.base_path = Path("./whisper_speaker_matcher")
            
        self.eingang_path = self.base_path / "Eingang"
        self.memory_path = self.base_path / "Memory"
        self.memory_path.mkdir(parents=True, exist_ok=True)
        
    def extract_speaker_from_filename(self, filename):
        """Extrahiere Sprecher aus Dateiname"""
        # Pattern: YYYY-MM-DD_speaker_originalname.txt
        pattern = r'^\d{4}-\d{2}-\d{2}_([^_]+)_'
        match = re.match(pattern, filename)
        if match:
            return match.group(1)
            
        # Alternative Pattern: speaker im Dateinamen
        known_speakers = ['ben', 'schroeti', 'freddy', 'marike', 'elke', 'christoph']
        filename_lower = filename.lower()
        
        for speaker in known_speakers:
            if speaker in filename_lower:
                return speaker
                
        return None
    
    def analyze_text_patterns(self, text):
        """Analysiere Text-Muster für Sprecher-Charakteristika"""
        text_lower = text.lower()
        
        # Wortfrequenz
        words = re.findall(r'\b\w+\b', text_lower)
        word_freq = Counter(words)
        
        # Füllwörter und charakteristische Phrasen
        filler_words = ['also', 'äh', 'ehm', 'genau', 'halt', 'eigentlich', 'irgendwie', 'sozusagen']
        filler_count = {word: text_lower.count(word) for word in filler_words}
        
        # Satzlänge (approximativ durch Punkte)
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        # Emotionale Indikatoren
        positive_words = ['toll', 'super', 'klasse', 'genial', 'wow', 'krass', 'mega', 'cool']
        negative_words = ['schlecht', 'scheiße', 'mist', 'problematisch', 'schwierig']
        
        positive_count = sum(text_lower.count(word) for word in positive_words)
        negative_count = sum(text_lower.count(word) for word in negative_words)
        
        return {
            'word_frequency': dict(word_freq.most_common(20)),
            'filler_words': filler_count,
            'avg_sentence_length': avg_sentence_length,
            'positive_sentiment': positive_count,
            'negative_sentiment': negative_count,
            'text_length': len(text),
            'word_count': len(words)
        }
    
    def extract_topics(self, text):
        """Extrahiere Themen aus Text"""
        text_lower = text.lower()
        
        topic_keywords = {
            'technology': ['technologie', 'software', 'programming', 'computer', 'ai', 'künstlich', 'intelligenz', 'digital', 'app', 'internet'],
            'business': ['business', 'geschäft', 'unternehmen', 'strategie', 'marketing', 'verkauf', 'kunden', 'projekt', 'meeting'],
            'personal': ['familie', 'freunde', 'beziehung', 'gefühle', 'liebe', 'persönlich', 'privat', 'leben'],
            'creative': ['kunst', 'musik', 'kreativ', 'design', 'malen', 'schreiben', 'inspiration', 'idee'],
            'health': ['gesundheit', 'sport', 'fitness', 'essen', 'ernährung', 'medizin', 'arzt', 'therapie'],
            'travel': ['reise', 'urlaub', 'fliegen', 'hotel', 'stadt', 'land', 'kultur', 'restaurant']
        }
        
        topic_scores = {}
        for topic, keywords in topic_keywords.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            if score > 0:
                topic_scores[topic] = score
                
        return topic_scores
    
    def build_speaker_profile(self, speaker, transcriptions):
        """Erstelle/aktualisiere Sprecher-Profil aus Transkriptionen"""
        logger.info(f"Baue Profil für {speaker} aus {len(transcriptions)} Transkriptionen")
        
        # Sammle alle Analysen
        all_patterns = []
        all_topics = defaultdict(int)
        all_interactions = []
        
        for trans_data in transcriptions:
            patterns = self.analyze_text_patterns(trans_data['text'])
            topics = self.extract_topics(trans_data['text'])
            
            all_patterns.append(patterns)
            for topic, score in topics.items():
                all_topics[topic] += score
                
            # Speichere Interaktion
            interaction = {
                'timestamp': trans_data.get('timestamp', datetime.now().isoformat()),
                'transcription': trans_data['text'],
                'source_file': trans_data.get('filename', 'unknown'),
                'length_chars': len(trans_data['text']),
                'topics': topics,
                'patterns': patterns
            }
            all_interactions.append(interaction)
        
        # Aggregiere Statistiken
        if all_patterns:
            # Durchschnittliche Satzlänge
            avg_sentence_length = sum(p['avg_sentence_length'] for p in all_patterns) / len(all_patterns)
            
            # Häufigste Wörter
            word_freq = defaultdict(int)
            for p in all_patterns:
                for word, count in p['word_frequency'].items():
                    word_freq[word] += count
            
            # Füllwörter
            filler_stats = defaultdict(int)
            for p in all_patterns:
                for word, count in p['filler_words'].items():
                    filler_stats[word] += count
            
            # Sentiment
            total_positive = sum(p['positive_sentiment'] for p in all_patterns)
            total_negative = sum(p['negative_sentiment'] for p in all_patterns)
            
        else:
            avg_sentence_length = 0
            word_freq = {}
            filler_stats = {}
            total_positive = 0
            total_negative = 0
        
        # Erstelle Profil
        profile = {
            'name': speaker.title(),
            'last_updated': datetime.now().isoformat(),
            'total_interactions': len(transcriptions),
            'statistics': {
                'avg_sentence_length': avg_sentence_length,
                'most_common_words': dict(Counter(word_freq).most_common(10)),
                'filler_words': dict(filler_stats),
                'sentiment': {
                    'positive': total_positive,
                    'negative': total_negative,
                    'ratio': total_positive / (total_positive + total_negative) if (total_positive + total_negative) > 0 else 0
                }
            },
            'topics': dict(sorted(all_topics.items(), key=lambda x: x[1], reverse=True)),
            'characteristics': self.infer_characteristics(word_freq, filler_stats, all_topics),
            'interactions': all_interactions[-50:]  # Nur letzte 50 Interaktionen speichern
        }
        
        return profile
    
    def infer_characteristics(self, word_freq, filler_stats, topics):
        """Leite Charakteristika aus Sprachmustern ab"""
        characteristics = []
        
        # Technische Orientierung
        if any(topic in ['technology', 'business'] for topic in topics.keys()):
            characteristics.append('technisch_orientiert')
        
        # Expressivität (viele Füllwörter)
        total_fillers = sum(filler_stats.values())
        if total_fillers > 20:
            characteristics.append('expressiv')
        elif total_fillers < 5:
            characteristics.append('präzise')
        
        # Häufige Wörter als Charakteristikum
        common_words = list(word_freq.keys())[:5]
        if 'also' in common_words:
            characteristics.append('bedächtig')
        if 'genau' in common_words:
            characteristics.append('bestätigend')
        if any(word in common_words for word in ['cool', 'krass', 'mega']):
            characteristics.append('jugendlich')
        
        return characteristics
    
    def process_transcription_files(self):
        """Verarbeite alle Transkriptions-Dateien"""
        if not self.eingang_path.exists():
            logger.error(f"Eingang-Ordner nicht gefunden: {self.eingang_path}")
            return
        
        # Sammle alle .txt Dateien
        txt_files = list(self.eingang_path.rglob("*.txt"))
        logger.info(f"Gefunden: {len(txt_files)} Transkriptions-Dateien")
        
        # Gruppiere nach Sprecher
        speaker_transcriptions = defaultdict(list)
        
        for txt_file in txt_files:
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Versuche Sprecher aus Dateiinhalt zu extrahieren
                speaker = None
                if content.startswith('Sprecher:'):
                    lines = content.split('\n')
                    speaker_line = lines[0]
                    speaker = speaker_line.split(':', 1)[1].strip()
                    # Extrahiere nur Transkription (nach "Transkription:")
                    if 'Transkription:' in content:
                        text = content.split('Transkription:', 1)[1].strip()
                    else:
                        text = content
                else:
                    # Versuche aus Dateiname
                    speaker = self.extract_speaker_from_filename(txt_file.name)
                    text = content
                
                if not speaker:
                    speaker = "Unbekannt"
                
                # Extrahiere Timestamp falls vorhanden
                timestamp = None
                if txt_file.stat().st_mtime:
                    timestamp = datetime.fromtimestamp(txt_file.stat().st_mtime).isoformat()
                
                speaker_transcriptions[speaker].append({
                    'text': text,
                    'filename': txt_file.name,
                    'timestamp': timestamp
                })
                
            except Exception as e:
                logger.error(f"Fehler beim Lesen von {txt_file}: {e}")
        
        # Erstelle Profile für jeden Sprecher
        for speaker, transcriptions in speaker_transcriptions.items():
            if speaker == "Unbekannt":
                continue
                
            profile = self.build_speaker_profile(speaker, transcriptions)
            
            # Speichere Profil
            profile_path = self.memory_path / f"{speaker.lower()}.yaml"
            with open(profile_path, 'w', encoding='utf-8') as f:
                yaml.dump(profile, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"✅ Profil für {speaker} gespeichert: {profile_path}")
            logger.info(f"   - {len(transcriptions)} Interaktionen")
            logger.info(f"   - Top Themen: {list(profile['topics'].keys())[:3]}")
        
        # Erstelle Zusammenfassung
        self.create_summary_report(speaker_transcriptions)
    
    def create_summary_report(self, speaker_data):
        """Erstelle Zusammenfassungsbericht"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_speakers': len(speaker_data),
            'speakers': {}
        }
        
        for speaker, transcriptions in speaker_data.items():
            total_words = sum(len(t['text'].split()) for t in transcriptions)
            report['speakers'][speaker] = {
                'transcription_count': len(transcriptions),
                'total_words': total_words,
                'avg_words_per_message': total_words / len(transcriptions) if transcriptions else 0
            }
        
        report_path = self.memory_path / "memory_build_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 Zusammenfassungsbericht erstellt: {report_path}")

def update_speaker_memory(speaker: str, transcript_data: Dict[str, Any], memory_dir: Path):
    """
    Aktualisiert das Memory-Profil für einen Sprecher

    Args:
        speaker: Sprecher-Name
        transcript_data: Transkript mit Metadaten (text, emotion, etc.)
        memory_dir: Memory-Verzeichnis
    """
    memory_file = memory_dir / f"{speaker}.yaml"

    # Lade existierendes Profil oder erstelle neues
    if memory_file.exists():
        with open(memory_file, 'r', encoding='utf-8') as f:
            memory = yaml.safe_load(f) or {}
    else:
        memory = {
            'name': speaker,
            'last_updated': None,
            'total_interactions': 0,
            'statistics': {
                'avg_sentence_length': 0,
                'most_common_words': {},
                'sentiment': {'positive': 0, 'negative': 0, 'ratio': 0}
            },
            'topics': {},
            'characteristics': [],
            'prosody_patterns': {
                'pitch_profile': {
                    'mean_pitch': 0,
                    'pitch_variability': 0,
                    'sample_count': 0
                },
                'tempo_profile': {
                    'mean_bpm': 0,
                    'mean_speech_rate': 0,
                    'sample_count': 0
                },
                'energy_profile': {
                    'mean_energy': 0,
                    'energy_variability': 0,
                    'mean_dynamic_range': 0,
                    'sample_count': 0
                }
            }
        }

    # Update statistics from transcript
    text = transcript_data.get('text', '')
    if text:
        sentences = text.split('.')
        memory['statistics']['avg_sentence_length'] = len(text.split()) / max(len(sentences), 1)

    # UPDATE PROSODY PATTERNS
    if 'emotion' in transcript_data and 'prosody' in transcript_data['emotion']:
        prosody = transcript_data['emotion']['prosody']

        # Update pitch profile
        if 'pitch' in prosody:
            pitch_data = prosody['pitch']
            pitch_profile = memory['prosody_patterns']['pitch_profile']
            n = pitch_profile['sample_count']

            # Running average
            if n > 0:
                pitch_profile['mean_pitch'] = (
                    (pitch_profile['mean_pitch'] * n + pitch_data.get('mean', 0)) / (n + 1)
                )
                pitch_profile['pitch_variability'] = (
                    (pitch_profile['pitch_variability'] * n + pitch_data.get('std', 0)) / (n + 1)
                )
            else:
                pitch_profile['mean_pitch'] = pitch_data.get('mean', 0)
                pitch_profile['pitch_variability'] = pitch_data.get('std', 0)

            pitch_profile['sample_count'] = n + 1

        # Update tempo profile
        if 'tempo' in prosody:
            tempo_data = prosody['tempo']
            tempo_profile = memory['prosody_patterns']['tempo_profile']
            n = tempo_profile['sample_count']

            if n > 0:
                tempo_profile['mean_bpm'] = (
                    (tempo_profile['mean_bpm'] * n + tempo_data.get('bpm', 0)) / (n + 1)
                )
                tempo_profile['mean_speech_rate'] = (
                    (tempo_profile['mean_speech_rate'] * n + tempo_data.get('speech_rate', 0)) / (n + 1)
                )
            else:
                tempo_profile['mean_bpm'] = tempo_data.get('bpm', 0)
                tempo_profile['mean_speech_rate'] = tempo_data.get('speech_rate', 0)

            tempo_profile['sample_count'] = n + 1

        # Update energy profile
        if 'energy' in prosody:
            energy_data = prosody['energy']
            energy_profile = memory['prosody_patterns']['energy_profile']
            n = energy_profile['sample_count']

            if n > 0:
                energy_profile['mean_energy'] = (
                    (energy_profile['mean_energy'] * n + energy_data.get('mean', 0)) / (n + 1)
                )
                energy_profile['energy_variability'] = (
                    (energy_profile['energy_variability'] * n + energy_data.get('std', 0)) / (n + 1)
                )
                energy_profile['mean_dynamic_range'] = (
                    (energy_profile['mean_dynamic_range'] * n + energy_data.get('dynamic_range', 0)) / (n + 1)
                )
            else:
                energy_profile['mean_energy'] = energy_data.get('mean', 0)
                energy_profile['energy_variability'] = energy_data.get('std', 0)
                energy_profile['mean_dynamic_range'] = energy_data.get('dynamic_range', 0)

            energy_profile['sample_count'] = n + 1

    # Update metadata
    memory['last_updated'] = datetime.now().isoformat()
    memory['total_interactions'] += 1

    # Save
    with open(memory_file, 'w', encoding='utf-8') as f:
        yaml.dump(memory, f, allow_unicode=True, default_flow_style=False)

def main():
    """Hauptfunktion"""
    print("🧠 Memory Builder gestartet...")
    print("Analysiere Transkriptionen und baue Sprecher-Profile...")
    
    try:
        builder = MemoryBuilder()
        builder.process_transcription_files()
        print("✅ Memory-Profile erfolgreich erstellt/aktualisiert!")
        
    except Exception as e:
        logger.error(f"Kritischer Fehler: {e}")
        print(f"❌ Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 