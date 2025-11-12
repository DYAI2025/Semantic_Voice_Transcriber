from typing import Dict, List, Optional

class DualMarkerSystem:
    """System for applying both simple and advanced markers to transcript text"""

    def __init__(self, mode: str = 'dual'):
        """Initialize dual marker system

        Args:
            mode: 'simple', 'advanced', 'dual', or 'therapeutic'
        """
        self.mode = mode
        self.simple_thresholds = {
            'tempo': 20.0,  # ±20% deviation
            'pitch': 15.0,  # ±15% deviation
            'energy': 25.0,  # ±25% deviation
            'pause': 1000    # 1000ms pause
        }

    def apply_markers(self, text: str,
                     prosody: Dict = None,
                     turning_points: List[Dict] = None,
                     markers: List[Dict] = None) -> str:
        """Apply markers to text based on mode

        Args:
            text: Original text segment
            prosody: Prosody features dict
            turning_points: List of turning point events
            markers: List of semantic markers

        Returns:
            Text with appropriate markers inserted
        """
        result = text

        # Apply simple markers if mode allows
        if self.mode in ['simple', 'dual', 'therapeutic']:
            result = self._apply_simple_markers(result, prosody)

        # Apply advanced markers if mode allows
        if self.mode in ['advanced', 'dual', 'therapeutic']:
            result = self._apply_advanced_markers(result, turning_points, markers)

        # Special formatting for therapeutic mode
        if self.mode == 'therapeutic' and turning_points:
            result = self._highlight_therapeutic(result, turning_points)

        return result

    def _apply_simple_markers(self, text: str, prosody: Dict = None) -> str:
        """Apply simple prosody markers"""
        if not prosody:
            return text

        markers = []

        # Tempo markers
        if 'tempo_deviation_pct' in prosody:
            deviation = prosody['tempo_deviation_pct']
            if abs(deviation) >= self.simple_thresholds['tempo']:
                if deviation > 0:
                    markers.append('[TEMPO↑]')
                else:
                    markers.append('[TEMPO↓]')

        # Pitch markers
        if 'pitch_deviation_pct' in prosody:
            deviation = prosody['pitch_deviation_pct']
            if abs(deviation) >= self.simple_thresholds['pitch']:
                if deviation > 0:
                    markers.append('[PITCH↑]')
                else:
                    markers.append('[PITCH↓]')

        # Energy markers
        if 'energy_deviation_pct' in prosody:
            deviation = prosody['energy_deviation_pct']
            if abs(deviation) >= self.simple_thresholds['energy']:
                if deviation > 0:
                    markers.append('[ENERGY↑]')
                else:
                    markers.append('[ENERGY↓]')

        # Pause marker
        if 'pause_before_ms' in prosody:
            if prosody['pause_before_ms'] >= self.simple_thresholds['pause']:
                markers.append('[PAUSE]')

        # Add markers to end of text
        if markers:
            return f"{text} {' '.join(markers)}"
        return text

    def _apply_advanced_markers(self, text: str,
                                turning_points: List[Dict] = None,
                                markers: List[Dict] = None) -> str:
        """Apply advanced turning point markers"""
        result = text

        if turning_points:
            for tp in turning_points:
                tp_type = tp.get('type', 'UNKNOWN')
                confidence = tp.get('confidence', 0)
                valence = tp.get('valence', {}).get('classification', 'neutral')

                marker = f"[TURNING_POINT: {tp_type}, {valence}, conf: {confidence:.2f}]"
                result = f"{result} {marker}"

        if markers:
            for marker in markers:
                marker_type = marker.get('type', 'UNKNOWN')
                result = f"{result} [MARKER: {marker_type}]"

        return result

    def _highlight_therapeutic(self, text: str, turning_points: List[Dict]) -> str:
        """Add special highlighting for therapeutic mode"""
        # In therapeutic mode, make turning points more prominent
        if turning_points and any(tp.get('confidence', 0) > 0.8 for tp in turning_points):
            return f">>> {text} <<<"
        return text

    def set_mode(self, mode: str):
        """Change marker display mode"""
        if mode in ['simple', 'advanced', 'dual', 'therapeutic']:
            self.mode = mode
        else:
            raise ValueError(f"Invalid mode: {mode}")

    def get_available_modes(self) -> List[str]:
        """Get list of available display modes"""
        return ['simple', 'advanced', 'dual', 'therapeutic']