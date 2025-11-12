import sys
from pathlib import Path
from typing import Dict, List, Any

# Add turning points detector to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'turning_points_detector'))

from src.turning_point_pipeline import TurningPointPipeline
from src.analyzers.cosd_analyzer import CoSDAnalyzer
from src.detectors.semantic_marker_detector import SemanticMarkerDetector

class TurningPointsLayer:
    """Layer 2: Advanced analysis with turning points detection"""

    def __init__(self, config_path=None):
        """Initialize turning points layer"""
        self.config_path = config_path or Path(__file__).parent.parent / 'turning_points_detector/config/config.yaml'
        self.pipeline = None
        self.cosd_analyzer = None
        self.marker_detector = None
        self._initialize_components()

    def _initialize_components(self):
        """Initialize analysis components"""
        try:
            self.pipeline = TurningPointPipeline(self.config_path)
            self.cosd_analyzer = CoSDAnalyzer()
            self.marker_detector = SemanticMarkerDetector()
        except Exception as e:
            print(f"Warning: Could not initialize all components: {e}")
            # Fallback to minimal functionality
            pass

    def process_transcript(self, transcript: Dict, prosody_features: Dict = None) -> Dict:
        """Process transcript with turning points detection

        Args:
            transcript: Transcript dict with segments
            prosody_features: Optional prosody features by segment ID

        Returns:
            Dict with turning_points, cosd_timeline, and markers
        """
        result = {
            'turning_points': [],
            'cosd_timeline': [],
            'markers': []
        }

        if not transcript or 'segments' not in transcript:
            return result

        # Extract text for CoSD analysis
        segments = transcript['segments']

        # Detect markers
        if self.marker_detector:
            for segment in segments:
                detected = self._detect_markers(segment['text'])
                if detected:
                    result['markers'].extend(detected)

        # Compute CoSD if multiple speakers
        speakers = set(s.get('speaker', 'Unknown') for s in segments)
        if len(speakers) > 1 and self.cosd_analyzer:
            result['cosd_timeline'] = self._compute_cosd(segments)

        # Detect turning points
        if self.pipeline and prosody_features:
            tp_events = self._detect_turning_points(segments, prosody_features, result)
            result['turning_points'] = tp_events

        return result

    def _detect_markers(self, text: str) -> List[Dict]:
        """Detect semantic markers in text"""
        # Simplified marker detection
        markers = []
        marker_patterns = {
            'INSIGHT': ['aha', 'jetzt verstehe ich', 'genau'],
            'HESITATION': ['äh', 'ähm', 'also'],
            'EMOTION': ['toll', 'schön', 'schwierig']
        }

        for marker_type, patterns in marker_patterns.items():
            for pattern in patterns:
                if pattern.lower() in text.lower():
                    markers.append({
                        'type': marker_type,
                        'pattern': pattern,
                        'text': text
                    })
        return markers

    def _compute_cosd(self, segments: List[Dict]) -> List[Dict]:
        """Compute Co-Emergent Semantic Drift timeline"""
        # Simplified CoSD computation
        timeline = []
        for i, segment in enumerate(segments):
            timeline.append({
                'turn': i,
                'timestamp': segment['start'],
                'speaker': segment.get('speaker', 'Unknown'),
                'cosd': 0.5,  # Placeholder
                'heat_state': 'STABLE'
            })
        return timeline

    def _detect_turning_points(self, segments: List[Dict],
                               prosody_features: Dict,
                               analysis_result: Dict) -> List[Dict]:
        """Detect turning points from all signals"""
        turning_points = []

        # Simplified turning point detection
        for i, segment in enumerate(segments):
            if i in prosody_features:
                prosody = prosody_features[i]
                # Check for significant prosody shifts
                if prosody.get('tempo_wpm', 100) > 150:
                    turning_points.append({
                        'type': 'TEMPO_SHIFT',
                        'turn': i,
                        'timestamp': segment['start'],
                        'confidence': 0.7
                    })

        return turning_points