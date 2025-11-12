import pytest

def test_svt_has_layer_checkboxes():
    """Test SVT GUI has checkboxes for layers"""
    # Just verify the code has the required variables defined
    # This is a simple check without running the full GUI

    with open('svt.py', 'r') as f:
        content = f.read()

    # Check for the new variables
    assert 'self.turning_points_var = tk.BooleanVar' in content
    assert 'self.dual_markers_var = tk.BooleanVar' in content
    assert 'self.enhanced_speakers_var = tk.BooleanVar' in content

    # Check for the checkbox text
    assert 'Wendepunkte-Erkennung' in content
    assert 'Duale Marker' in content
    assert 'Erweiterte Sprecherdarstellung' in content