"""
Enhanced Speaker Visualization
Format transcripts with colors, icons, dividers, indentation
"""

from typing import List, Dict

class SpeakerVisualizerV2:
    """Professional speaker visualization"""

    SPEAKER_ICONS = {
        0: "👤", 1: "👨", 2: "👩", 3: "🧑",
        4: "👴", 5: "👵", 6: "🧔", 7: "👱"
    }

    def format_markdown(self, segments: List[Dict]) -> str:
        """
        Format transcript as Markdown with speaker visualization

        Args:
            segments: List of segments with speaker info

        Returns:
            Formatted markdown string
        """
        output = []
        previous_speaker = None

        for seg in segments:
            speaker_id = seg['speaker_id']
            speaker_name = seg.get('speaker_name', f'Speaker {speaker_id}')
            text = seg['text']
            start = seg['start']
            end = seg['end']
            confidence = seg.get('confidence', 1.0)

            # Add divider line if speaker changed
            if speaker_id != previous_speaker and previous_speaker is not None:
                output.append('\n---\n')

            # Get icon
            icon = self.SPEAKER_ICONS.get(hash(speaker_id) % 8, "👤")

            # Speaker header
            header = f"\n{icon} **{speaker_name}** `[{start:.1f}s - {end:.1f}s]`\n"
            output.append(header)

            # Content with confidence indicator if low
            if confidence < 0.7:
                content = f"> {text} *[⚠️ Low confidence: {confidence:.0%}]*\n"
            else:
                content = f"> {text}\n"
            output.append(content)

            previous_speaker = speaker_id

        return ''.join(output)

    def format_html(self, segments: List[Dict]) -> str:
        """
        Format transcript as HTML with speaker visualization

        Args:
            segments: List of segments with speaker info

        Returns:
            Formatted HTML string
        """
        output = ['<div class="transcript">']
        previous_speaker = None

        for seg in segments:
            speaker_id = seg['speaker_id']
            speaker_name = seg.get('speaker_name', f'Speaker {speaker_id}')
            speaker_color = seg.get('color', '#4A90E2')
            text = seg['text']
            start = seg['start']
            end = seg['end']
            confidence = seg.get('confidence', 1.0)

            # Add divider if speaker changed
            if speaker_id != previous_speaker and previous_speaker is not None:
                output.append('<hr class="speaker-divider"/>')

            # Get icon
            icon = self.SPEAKER_ICONS.get(hash(speaker_id) % 8, "👤")

            # Determine background based on confidence
            bg_color = "#f8f9fa"  # Default
            if confidence < 0.7:
                bg_color = "#fff5f5"  # Light red for low confidence

            # Speaker block
            block = f'''
            <div class="speaker-block" style="border-left: 4px solid {speaker_color}; padding: 10px; margin: 15px 0; background: {bg_color}; border-radius: 8px;">
                <div class="speaker-header" style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-weight: bold;">
                    <span class="speaker-icon" style="font-size: 24px;">{icon}</span>
                    <span class="speaker-name">{speaker_name}</span>
                    <span class="timestamp" style="color: #6c757d; font-size: 0.9em;">[{start:.1f}s - {end:.1f}s]</span>
                    {f'<span class="confidence" style="color: #e74c3c; font-size: 0.8em;">⚠️ Low confidence: {confidence:.0%}</span>' if confidence < 0.7 else ''}
                </div>
                <div class="speaker-content" style="padding-left: 35px; line-height: 1.6;">
                    {text}
                </div>
            </div>
            '''
            output.append(block)

            previous_speaker = speaker_id

        output.append('</div>')
        return '\n'.join(output)

# Usage example
if __name__ == "__main__":
    visualizer = SpeakerVisualizerV2()

    test_segments = [
        {
            'speaker_id': 'SPEAKER_00',
            'speaker_name': 'Dr. Schmidt',
            'color': '#4A90E2',
            'start': 0.0,
            'end': 5.2,
            'text': 'Guten Tag. Wie geht es Ihnen heute?'
        },
        {
            'speaker_id': 'SPEAKER_01',
            'speaker_name': 'Patient A',
            'color': '#7B68EE',
            'start': 5.2,
            'end': 12.5,
            'text': 'Mir geht es gut, danke. Ich möchte heute über meine Fortschritte sprechen.'
        }
    ]

    # Test Markdown
    print("=== MARKDOWN ===")
    print(visualizer.format_markdown(test_segments))

    # Test HTML
    print("\n=== HTML ===")
    print(visualizer.format_html(test_segments))