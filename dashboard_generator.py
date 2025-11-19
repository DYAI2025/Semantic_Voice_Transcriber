# dashboard_generator.py
import json
from pathlib import Path

class DashboardGenerator:
    """Interactive HTML dashboard generator with Chart.js and Cytoscape.js"""

    def __init__(self):
        """Initialize dashboard generator"""
        pass

    def generate_dashboard(self, analysis_result, output_path):
        """Generate interactive HTML dashboard

        Args:
            analysis_result: Dictionary with utterance_states, ued_metrics, marker_summary, turnpoints
            output_path: Path to save HTML file
        """
        output_path = Path(output_path)

        # Extract data
        utterances = analysis_result["utterance_states"]
        ued_metrics = analysis_result["ued_metrics"]
        marker_summary = analysis_result.get("marker_summary", {})
        turnpoints = analysis_result.get("turnpoints", [])
        input_meta = analysis_result.get("input_meta", {})

        # Build HTML
        html = self._build_html_structure(
            utterances, ued_metrics, marker_summary, turnpoints, input_meta
        )

        # Write to file
        output_path.write_text(html, encoding='utf-8')

    def _build_html_structure(self, utterances, ued_metrics, marker_summary, turnpoints, input_meta):
        """Build complete HTML dashboard structure"""

        # Prepare data for JavaScript
        emotion_data = self._prepare_emotion_chart_data(utterances)
        marker_freq_data = self._prepare_marker_frequency_data(marker_summary)
        network_data = self._prepare_network_data(utterances, marker_summary)
        turnpoint_data = turnpoints

        html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Psychoanalysis Dashboard - {input_meta.get('transcript_file', 'Session')}</title>

    <!-- Chart.js for emotion trajectories -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

    <!-- Cytoscape.js for marker networks -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.28.1/cytoscape.min.js"></script>

    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f5f7fa;
            color: #333;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}

        .header p {{
            opacity: 0.9;
            font-size: 0.95rem;
        }}

        .dashboard {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            padding: 1.5rem;
            max-width: 1800px;
            margin: 0 auto;
        }}

        .panel {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            padding: 1.5rem;
        }}

        .panel-title {{
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #667eea;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 0.5rem;
        }}

        /* Utterance styles */
        .utterance {{
            margin-bottom: 1.5rem;
            padding: 1rem;
            border-left: 4px solid #667eea;
            background: #f9fafb;
            border-radius: 6px;
        }}

        .utterance-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }}

        .speaker {{
            font-weight: 600;
            color: #667eea;
            font-size: 0.9rem;
        }}

        .emotions {{
            font-size: 0.75rem;
            color: #666;
        }}

        .utterance-text {{
            line-height: 1.6;
            color: #333;
            margin-bottom: 0.5rem;
        }}

        .markers {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.5rem;
        }}

        .marker-tag {{
            background: #fef3c7;
            color: #92400e;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
        }}

        .turnpoint-tag {{
            background: #fee2e2;
            color: #991b1b;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            border: 1px solid #fca5a5;
        }}

        .prosody {{
            font-size: 0.75rem;
            color: #6b7280;
            margin-top: 0.5rem;
            font-family: 'Courier New', monospace;
        }}

        /* Chart containers */
        .chart-container {{
            position: relative;
            height: 300px;
            margin-bottom: 1.5rem;
        }}

        #cytoscape-container {{
            width: 100%;
            height: 400px;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            margin-top: 1rem;
        }}

        /* UED metrics cards */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}

        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .metric-label {{
            font-size: 0.8rem;
            opacity: 0.9;
            margin-bottom: 0.25rem;
        }}

        .metric-value {{
            font-size: 1.5rem;
            font-weight: 700;
        }}

        /* Turnpoint timeline */
        .turnpoint-timeline {{
            margin-top: 1rem;
        }}

        .turnpoint-item {{
            padding: 1rem;
            margin-bottom: 1rem;
            border-left: 4px solid #ef4444;
            background: #fef2f2;
            border-radius: 6px;
        }}

        .turnpoint-type {{
            font-weight: 600;
            color: #991b1b;
            font-size: 0.85rem;
            text-transform: uppercase;
        }}

        .turnpoint-desc {{
            margin-top: 0.5rem;
            color: #333;
            font-size: 0.9rem;
        }}

        .turnpoint-significance {{
            display: inline-block;
            margin-top: 0.5rem;
            padding: 0.25rem 0.75rem;
            background: #fee2e2;
            color: #991b1b;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 600;
        }}

        @media (max-width: 1200px) {{
            .dashboard {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Psychoanalysis Dashboard</h1>
        <p>{input_meta.get('transcript_file', 'Therapeutic Session Analysis')} | {input_meta.get('language', 'de').upper()} | {input_meta.get('text_type', 'session')}</p>
    </div>

    <div class="dashboard">
        <!-- LEFT PANEL: Annotated Transcript -->
        <div class="panel" style="grid-row: span 2;">
            <h2 class="panel-title">Annotiertes Transkript</h2>
            <div id="transcript-container">
                {self._render_utterances_html(utterances, turnpoints)}
            </div>
        </div>

        <!-- RIGHT PANEL TOP: Emotion Trajectory -->
        <div class="panel">
            <h2 class="panel-title">Emotionsdynamik (UED)</h2>
            <div class="chart-container">
                <canvas id="emotionChart"></canvas>
            </div>

            <!-- UED Metrics Summary -->
            <h3 style="font-size: 1.1rem; margin-top: 1.5rem; margin-bottom: 1rem; color: #667eea;">UED Metriken</h3>
            <div class="metrics-grid">
                {self._render_ued_metrics_html(ued_metrics)}
            </div>
        </div>

        <!-- RIGHT PANEL BOTTOM: Turnpoints & Markers -->
        <div class="panel">
            <h2 class="panel-title">Wendepunkte & Marker</h2>

            <!-- Turnpoint Timeline -->
            <h3 style="font-size: 1.1rem; margin-bottom: 1rem; color: #667eea;">Turnpoints</h3>
            <div class="turnpoint-timeline">
                {self._render_turnpoints_html(turnpoints)}
            </div>

            <!-- Marker Frequency Chart -->
            <h3 style="font-size: 1.1rem; margin-top: 1.5rem; margin-bottom: 1rem; color: #667eea;">Marker-Häufigkeit</h3>
            <div class="chart-container" style="height: 200px;">
                <canvas id="markerChart"></canvas>
            </div>

            <!-- Marker Network -->
            <h3 style="font-size: 1.1rem; margin-top: 1.5rem; margin-bottom: 0.5rem; color: #667eea;">Marker-Netzwerk</h3>
            <div id="cytoscape-container"></div>
        </div>
    </div>

    <script>
        // Emotion Trajectory Chart
        const emotionCtx = document.getElementById('emotionChart').getContext('2d');
        const emotionChart = new Chart(emotionCtx, {{
            type: 'line',
            data: {json.dumps(emotion_data)},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'top',
                    }},
                    title: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        min: -1,
                        max: 1,
                        title: {{
                            display: true,
                            text: 'VAD Werte'
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: 'Utterance ID'
                        }}
                    }}
                }}
            }}
        }});

        // Marker Frequency Chart
        const markerCtx = document.getElementById('markerChart').getContext('2d');
        const markerChart = new Chart(markerCtx, {{
            type: 'bar',
            data: {json.dumps(marker_freq_data)},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            stepSize: 1
                        }},
                        title: {{
                            display: true,
                            text: 'Häufigkeit'
                        }}
                    }}
                }}
            }}
        }});

        // Marker Network (Cytoscape.js)
        const cy = cytoscape({{
            container: document.getElementById('cytoscape-container'),
            elements: {json.dumps(network_data)},
            style: [
                {{
                    selector: 'node',
                    style: {{
                        'background-color': '#667eea',
                        'label': 'data(label)',
                        'color': '#333',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'font-size': '10px',
                        'width': 40,
                        'height': 40
                    }}
                }},
                {{
                    selector: 'edge',
                    style: {{
                        'width': 2,
                        'line-color': '#cbd5e1',
                        'target-arrow-color': '#cbd5e1',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier'
                    }}
                }}
            ],
            layout: {{
                name: 'circle',
                animate: true
            }}
        }});
    </script>
</body>
</html>
"""
        return html

    def _render_utterances_html(self, utterances, turnpoints):
        """Render utterances with inline annotations"""
        # Create turnpoint lookup by utterance_id
        turnpoints_by_id = {}
        for tp in turnpoints:
            utt_id = tp["utterance_id"]
            if utt_id not in turnpoints_by_id:
                turnpoints_by_id[utt_id] = []
            turnpoints_by_id[utt_id].append(tp)

        html_parts = []
        for utt in utterances:
            utt_id = utt["id"]
            speaker = utt.get("speaker", "Unknown")
            text = utt["text"]
            ued = utt.get("ued_emotions", {})
            markers = utt.get("markers", [])
            prosody = utt.get("prosody", {})

            # Emotion values
            valence = ued.get("valence", 0)
            arousal = ued.get("arousal", 0)
            dominance = ued.get("dominance", 0)

            # Build utterance HTML
            html_parts.append(f'''
                <div class="utterance">
                    <div class="utterance-header">
                        <span class="speaker">Sprecher {speaker}</span>
                        <span class="emotions">V:{valence:.2f} A:{arousal:.2f} D:{dominance:.2f}</span>
                    </div>
                    <div class="utterance-text">{text}</div>
            ''')

            # Markers
            if markers:
                html_parts.append('<div class="markers">')
                for marker in markers:
                    html_parts.append(f'<span class="marker-tag">{marker}</span>')
                html_parts.append('</div>')

            # Turnpoints
            if utt_id in turnpoints_by_id:
                html_parts.append('<div class="markers">')
                for tp in turnpoints_by_id[utt_id]:
                    html_parts.append(f'<span class="turnpoint-tag">🔄 {tp["type"]}: {tp.get("significance", "medium")}</span>')
                html_parts.append('</div>')

            # Prosody
            if prosody:
                prosody_str = f"Tempo: {prosody.get('tempo_wpm', 'N/A')} WPM | Pitch: {prosody.get('pitch_hz', 'N/A')} Hz | Pause: {prosody.get('pause_before_ms', 'N/A')} ms"
                html_parts.append(f'<div class="prosody">{prosody_str}</div>')

            html_parts.append('</div>')

        return '\n'.join(html_parts)

    def _render_ued_metrics_html(self, ued_metrics):
        """Render UED metrics as cards"""
        home_base = ued_metrics.get("home_base", {})
        variability = ued_metrics.get("variability", {})
        instability = ued_metrics.get("instability", {})

        cards = []

        # Home Base Valence
        cards.append(f'''
            <div class="metric-card">
                <div class="metric-label">Heimatbasis Valenz</div>
                <div class="metric-value">{home_base.get("valence", 0):.2f}</div>
            </div>
        ''')

        # Variability
        cards.append(f'''
            <div class="metric-card">
                <div class="metric-label">Variabilität Valenz</div>
                <div class="metric-value">{variability.get("valence", 0):.2f}</div>
            </div>
        ''')

        # Instability
        cards.append(f'''
            <div class="metric-card">
                <div class="metric-label">Instabilität Valenz</div>
                <div class="metric-value">{instability.get("valence", 0):.2f}</div>
            </div>
        ''')

        # Home Base Arousal
        cards.append(f'''
            <div class="metric-card">
                <div class="metric-label">Heimatbasis Arousal</div>
                <div class="metric-value">{home_base.get("arousal", 0):.2f}</div>
            </div>
        ''')

        return '\n'.join(cards)

    def _render_turnpoints_html(self, turnpoints):
        """Render turnpoints as timeline items"""
        if not turnpoints:
            return '<p style="color: #6b7280; font-size: 0.9rem;">Keine Wendepunkte erkannt.</p>'

        items = []
        for tp in turnpoints:
            tp_type = tp.get("type", "unknown")
            description = tp.get("description", "")
            significance = tp.get("significance", "medium")
            utt_id = tp.get("utterance_id", "?")

            items.append(f'''
                <div class="turnpoint-item">
                    <div class="turnpoint-type">{tp_type} (Utterance #{utt_id})</div>
                    <div class="turnpoint-desc">{description}</div>
                    <span class="turnpoint-significance">{significance.upper()}</span>
                </div>
            ''')

        return '\n'.join(items)

    def _prepare_emotion_chart_data(self, utterances):
        """Prepare Chart.js data for emotion trajectory"""
        labels = [utt["id"] for utt in utterances]
        valence_data = [utt.get("ued_emotions", {}).get("valence", 0) for utt in utterances]
        arousal_data = [utt.get("ued_emotions", {}).get("arousal", 0) for utt in utterances]
        dominance_data = [utt.get("ued_emotions", {}).get("dominance", 0) for utt in utterances]

        return {
            "labels": labels,
            "datasets": [
                {
                    "label": "Valenz",
                    "data": valence_data,
                    "borderColor": "rgb(239, 68, 68)",
                    "backgroundColor": "rgba(239, 68, 68, 0.1)",
                    "tension": 0.3
                },
                {
                    "label": "Arousal",
                    "data": arousal_data,
                    "borderColor": "rgb(59, 130, 246)",
                    "backgroundColor": "rgba(59, 130, 246, 0.1)",
                    "tension": 0.3
                },
                {
                    "label": "Dominanz",
                    "data": dominance_data,
                    "borderColor": "rgb(34, 197, 94)",
                    "backgroundColor": "rgba(34, 197, 94, 0.1)",
                    "tension": 0.3
                }
            ]
        }

    def _prepare_marker_frequency_data(self, marker_summary):
        """Prepare Chart.js data for marker frequency bar chart"""
        frequencies = marker_summary.get("frequencies", {})

        if not frequencies:
            return {"labels": [], "datasets": [{"label": "Häufigkeit", "data": [], "backgroundColor": "rgb(102, 126, 234)"}]}

        labels = list(frequencies.keys())
        data = list(frequencies.values())

        return {
            "labels": labels,
            "datasets": [
                {
                    "label": "Häufigkeit",
                    "data": data,
                    "backgroundColor": "rgb(102, 126, 234)"
                }
            ]
        }

    def _prepare_network_data(self, utterances, marker_summary):
        """Prepare Cytoscape.js data for marker network"""
        # Create nodes for each marker
        markers = marker_summary.get("frequencies", {}).keys()
        nodes = [{"data": {"id": marker, "label": marker.split("_")[-1]}} for marker in markers]

        # Create edges based on co-occurrence (markers appearing in same utterance)
        edges = []
        marker_list = list(markers)

        for i, marker1 in enumerate(marker_list):
            for marker2 in marker_list[i+1:]:
                # Check if they co-occur
                co_occurs = any(
                    marker1 in utt.get("markers", []) and marker2 in utt.get("markers", [])
                    for utt in utterances
                )
                if co_occurs:
                    edges.append({
                        "data": {
                            "source": marker1,
                            "target": marker2
                        }
                    })

        return nodes + edges
