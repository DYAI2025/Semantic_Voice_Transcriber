# Turning-Point Pipeline Bridge (Updated)

Bridge modules under `src/` now actively import the real detector implementation from `Turning_Points_in_Transcription/turning_points_detector/src` whenever it is present, falling back to lightweight stubs only when the detector tree is missing. The loader adds the detector’s parent directory to `sys.path`, so the original namespace package (`turning_points_detector.src`) remains intact and relative imports (e.g., `.analyzers`) resolve without collisions with the repo’s own `src/` package.

Touched files:
- `src/_turning_points_loader.py`
- `src/turning_point_pipeline.py`
- `src/analyzers/cosd_analyzer.py`
- `src/detectors/semantic_marker_detector.py`

Verification:
- `python3 -m pytest tests/test_turning_points_layer.py tests/test_full_integration.py -q`
- sanity check: `from src.turning_point_pipeline import TurningPointPipeline` now reports `turning_points_detector.src.turning_point_pipeline` as the class module.
