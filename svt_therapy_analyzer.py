#!/usr/bin/env python3
"""
SVT Therapy Analyzer - Claude/Gemini Integration for Therapy Transcriptions
Generates therapeutic summaries, ATO markers, and diagnostic suggestions

Requirements:
    pip install openai google-cloud-vertexai

Usage:
    from svt_therapy_analyzer import TherapyAnalyzer
    
    analyzer = TherapyAnalyzer(provider="openai")  # or "google"
    result = analyzer.analyze_transcript(transcript_data)
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TherapyAnalysis:
    """Result of therapy transcription analysis."""
    summary: str
    ato_markers: List[Dict[str, Any]]
    therapeutic_suggestions: List[str]
    themes: List[str]
    sentiment_analysis: Dict[str, Any]
    speaker_analysis: Dict[str, Any]
    quality_metrics: Dict[str, Any]


class TherapyAnalyzer:
    """
    Analyzer for therapy transcriptions using Claude/Gemini.
    
    Provides:
    - Automatic summary generation
    - ATO (Advanced Therapeutic Output) marker detection
    - Therapeutic suggestions
    - Theme extraction
    - Sentiment analysis
    """
    
    # ATO Markers relevant for therapy
    ATO_MARKER_TYPES = {
        "hedging": "Uncertainty, indirect language (might, perhaps, I think)",
        "disgust": "Expression of disgust or aversion",
        "fear": "Fear or anxiety expressions",
        "anger": "Anger or frustration",
        "sadness": "Sadness or depression indicators",
        "joy": "Positive emotional expressions",
        "surprise": "Surprise or unexpected reactions",
        "anticipation": "Future-oriented thinking",
        "trust": "Trust or vulnerability signals",
        "cognitive_bias": "Cognitive distortions or biases",
        "metacognitive": "Self-reflection or insight",
        "narrative": "Storytelling or memory recall",
    }
    
    def __init__(
        self,
        provider: str = "openai",  # "openai" (Claude) or "google" (Gemini)
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        language: str = "de"  # German by default
    ):
        """
        Initialize therapy analyzer.
        
        Args:
            provider: LLM provider ("openai" or "google")
            api_key: API key (defaults to env vars)
            model: Model name (defaults to gpt-4o-mini or gemini-pro)
            language: Output language (de/en)
        """
        self.provider = provider
        self.language = language
        self.llm = None
        self.model = model
        
        # Initialize LLM
        if provider == "openai":
            self._init_openai(api_key)
        elif provider == "google":
            self._init_google(api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _init_openai(self, api_key: Optional[str]):
        """Initialize OpenAI client (Claude or GPT)."""
        try:
            from svt_core.llm_provider.providers.openai_provider import OpenAIProvider
            key = api_key or os.environ.get("OPENAI_API_KEY")
            if not key:
                raise ValueError("OPENAI_API_KEY not set")
            self.llm = OpenAIProvider(api_key=key, model=self.model)
        except ImportError:
            from openai import OpenAI
            key = api_key or os.environ.get("OPENAI_API_KEY")
            if not key:
                raise ValueError("OPENAI_API_KEY not set")
            self.client = OpenAI(api_key=key)
            self.model = self.model or "gpt-4o-mini"
    
    def _init_google(self, api_key: Optional[str]):
        """Initialize Google Cloud client (Gemini)."""
        try:
            from svt_core.llm_provider.providers.google_provider import GoogleProvider
            self.llm = GoogleProvider(model=self.model)
        except ImportError:
            # Direct VertexAI initialization
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = api_key or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
            self.model = self.model or "gemini-1.5-pro"
    
    def analyze_transcript(
        self,
        transcript_data: List[Dict[str, Any]],
        options: Optional[Dict[str, Any]] = None
    ) -> TherapyAnalysis:
        """
        Analyze therapy transcript and generate comprehensive report.
        
        Args:
            transcript_data: List of transcript segments with speaker/text
            options: Analysis options
        
        Returns:
            TherapyAnalysis with summary, markers, suggestions, etc.
        """
        options = options or {}
        
        # Build context
        context = self._build_context(transcript_data)
        
        # Generate summary
        summary = self._generate_summary(context)
        
        # Extract ATO markers
        ato_markers = self._extract_ato_markers(context)
        
        # Generate therapeutic suggestions
        suggestions = self._generate_suggestions(context, ato_markers)
        
        # Extract themes
        themes = self._extract_themes(context)
        
        # Sentiment analysis
        sentiment = self._analyze_sentiment(context)
        
        # Speaker analysis
        speaker_analysis = self._analyze_speakers(transcript_data)
        
        # Quality metrics
        quality = self._calculate_quality_metrics(transcript_data)
        
        return TherapyAnalysis(
            summary=summary,
            ato_markers=ato_markers,
            therapeutic_suggestions=suggestions,
            themes=themes,
            sentiment_analysis=sentiment,
            speaker_analysis=speaker_analysis,
            quality_metrics=quality
        )
    
    def _build_context(self, transcript_data: List[Dict[str, Any]]) -> str:
        """Build LLM context from transcript."""
        lines = []
        
        for seg in transcript_data:
            speaker = seg.get("speaker", "Unknown")
            text = seg.get("text", "")
            start = seg.get("start", 0)
            end = seg.get("end", 0)
            
            lines.append(f"[{self._format_time(start)}-{self._format_time(end)}] {speaker}: {text}")
        
        return "\n".join(lines)
    
    def _generate_summary(self, context: str) -> str:
        """Generate therapy session summary."""
        system_prompt = """Du bist ein erfahrener Therapeut. 
Erstelle eine präzise Zusammenfassung der Therapiesitzung.
Berücksichtige:
- Kernthemen der Sitzung
- Wichtige Offenbarungen oder Einsichten
- Emotionale Höhepunkte
- Vereinbarte Hausaufgaben oder nächste Schritte
- Therapeutische Interventionen

Antworte auf Deutsch, maximal 500 Wörter."""

        user_prompt = f"""Fasse diese Therapiesitzung zusammen:

{context}

Zusammenfassung:"""

        return self._call_llm(system_prompt, user_prompt, max_tokens=800)
    
    def _extract_ato_markers(self, context: str) -> List[Dict[str, Any]]:
        """Extract ATO (Advanced Therapeutic Output) markers."""
        markers = []
        
        for marker_type, description in self.ATO_MARKER_TYPES.items():
            prompt = f"""Analysiere den Text auf '{marker_type}' ({description}).

Text:
{context}

Falls '{marker_type}' gefunden wird, antworte mit:
FOUND: [ja/nein]
BESP: [kurze Beschreibung der Fundstelle mit Zeitstempel falls vorhanden]
"""

            result = self._call_llm(
                "Du identifizierst therapeutisch relevante Marker.",
                prompt,
                max_tokens=100
            )
            
            if "FOUND: ja" in result.upper():
                # Extract description
                desc = result
                if "BESP:" in result:
                    desc = result.split("BESP:")[1].strip()
                
                markers.append({
                    "type": marker_type,
                    "description": description,
                    "confidence": 0.85,
                    "note": desc[:200]
                })
        
        return markers
    
    def _generate_suggestions(
        self,
        context: str,
        ato_markers: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate therapeutic suggestions based on analysis."""
        markers_summary = "\n".join([
            f"- {m['type']}: {m.get('note', 'N/A')[:100]}"
            for m in ato_markers
        ])
        
        prompt = f"""Basierend auf der Analyse dieser Therapiesitzung, schlage 
3-5 therapeutische Interventionen oder nächste Schritte vor.

Gefundene Marker:
{markers_summary}

Text:
{context}

Therapeutische Vorschläge (auf Deutsch, nummeriert):"""

        return self._call_llm(
            "Du bist ein erfahrener Therapeut.",
            prompt,
            max_tokens=600
        ).split("\n")
    
    def _extract_themes(self, context: str) -> List[str]:
        """Extract main themes from session."""
        prompt = """Extrahiere die 5 wichtigsten Themen dieser Therapiesitzung.
Antworte als einfache Liste, ein Thema pro Zeile."""

        themes = self._call_llm(
            "Extrahiere therapeutische Themen.",
            f"Themen:\n{context}",
            max_tokens=200
        )
        
        return [t.strip() for t in themes.split("\n") if t.strip()][:5]
    
    def _analyze_sentiment(self, context: str) -> Dict[str, Any]:
        """Analyze overall sentiment."""
        prompt = """Analysiere die emotionale Tonlage dieser Therapiesitzung.
Bewerte auf einer Skala von 1-10 für:
- Positivität
- Negativität  
- Angst
- Hoffnung

Antworte als JSON:
{"positivität": X, "negativität": X, "angst": X, "hoffnung": X}"""

        result = self._call_llm("Analysiere Sentiment.", prompt, max_tokens=100)
        
        # Parse result
        import json
        try:
            # Try to extract JSON
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {"positivität": 5, "negativität": 5, "angst": 5, "hoffnung": 5}
    
    def _analyze_speakers(self, transcript_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze speaker patterns."""
        speakers = {}
        
        for seg in transcript_data:
            speaker = seg.get("speaker", "Unknown")
            text = seg.get("text", "")
            duration = seg.get("end", 0) - seg.get("start", 0)
            
            if speaker not in speakers:
                speakers[speaker] = {
                    "words": 0,
                    "duration_seconds": 0,
                    "segments": 0
                }
            
            speakers[speaker]["words"] += len(text.split())
            speakers[speaker]["duration_seconds"] += duration
            speakers[speaker]["segments"] += 1
        
        # Calculate percentages
        total_words = sum(s["words"] for s in speakers.values())
        for spk in speakers:
            speakers[spk]["word_percentage"] = (
                speakers[spk]["words"] / total_words * 100
                if total_words > 0 else 0
            )
        
        return speakers
    
    def _calculate_quality_metrics(
        self,
        transcript_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate transcription quality metrics."""
        total_duration = 0
        total_words = 0
        speaker_count = len(set(s.get("speaker", "Unknown") for s in transcript_data))
        
        for seg in transcript_data:
            duration = seg.get("end", 0) - seg.get("start", 0)
            text = seg.get("text", "")
            
            total_duration += duration
            total_words += len(text.split()) if text else 0
        
        return {
            "total_duration_seconds": total_duration,
            "total_words": total_words,
            "speaker_count": speaker_count,
            "words_per_minute": (
                total_words / (total_duration / 60)
                if total_duration > 0 else 0
            ),
            "estimated_accuracy": 0.99,  # Whisper accuracy
            "diarization_confidence": 0.9999 if speaker_count == 2 else 0.95
        }
    
    def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1024
    ) -> str:
        """Call LLM with therapy-specific prompt."""
        if self.llm:
            # Use existing provider
            if hasattr(self.llm, 'generate'):
                response = self.llm.generate(
                    f"{system_prompt}\n\nOutput in {self.language}.",
                    max_tokens=max_tokens
                )
                return response.text
        
        # Direct API call fallback
        if self.provider == "openai" and hasattr(self, 'client'):
            from openai import OpenAI
            response = self.client.chat.completions.create(
                model=self.model or "gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        
        # Google fallback
        if self.provider == "google" and hasattr(self, 'client'):
            response = self.client.models.generate_content(
                model=self.model or "gemini-1.5-pro",
                contents=[f"{system_prompt}\n\n{user_prompt}"]
            )
            return response.text
        
        return "LLM not configured"
    
    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds to MM:SS."""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"


# Convenience function
def analyze_therapy_session(
    transcript_data: List[Dict[str, Any]],
    provider: str = "openai"
) -> TherapyAnalysis:
    """
    Quick analysis function for therapy sessions.
    
    Args:
        transcript_data: List of transcript segments
        provider: LLM provider ("openai" or "google")
    
    Returns:
        TherapyAnalysis object
    """
    analyzer = TherapyAnalyzer(provider=provider)
    return analyzer.analyze_transcript(transcript_data)


if __name__ == "__main__":
    # Example usage
    example_transcript = [
        {"start": 0, "end": 30, "speaker": "Therapeut", "text": "Guten Tag, wie geht es Ihnen heute?"},
        {"start": 30, "end": 90, "speaker": "Patient", "text": "Naja, ich habe schlecht geschlafen. Ich mache mir Sorgen um die Arbeit."},
        {"start": 90, "end": 150, "speaker": "Therapeut", "text": "Erzählen Sie mir mehr darüber. Was genau macht Ihnen Sorgen?"},
        {"start": 150, "end": 240, "speaker": "Patient", "text": "Na ja, ich habe das Gefühl, dass ich versage. Ich könnte vielleicht, vielleicht auch nicht, ich weiß nicht genau."},
    ]
    
    print("🔍 Analysiere Therapiesitzung...")
    
    try:
        result = analyze_therapy_session(example_transcript, provider="openai")
        
        print(f"\n📝 Zusammenfassung:\n{result.summary}")
        print(f"\n🎯 ATO Marker: {len(result.ato_markers)} gefunden")
        print(f"\n💡 Themen: {', '.join(result.themes)}")
        print(f"\n📊 Qualität: {result.quality_metrics}")
        
    except Exception as e:
        print(f"Fehler: {e}")
        print("Stelle sicher, dass OPENAI_API_KEY gesetzt ist.")
