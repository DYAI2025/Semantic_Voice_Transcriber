# quality_validator.py
"""
Quality Validation Layer for SVT
Monitors output quality and detects missing/incorrect data
Implements POST-processing validation as designed in ARCHITECTURE.md
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime


class QualityIssue:
    """Represents a quality issue found during validation"""

    SEVERITY_ERROR = "ERROR"      # Critical issue, output may be unusable
    SEVERITY_WARNING = "WARNING"  # Non-critical issue, output usable but degraded
    SEVERITY_INFO = "INFO"        # Informational notice

    def __init__(self, severity: str, component: str, message: str, recommendation: str, details: Dict = None):
        self.severity = severity
        self.component = component
        self.message = message
        self.recommendation = recommendation
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "severity": self.severity,
            "component": self.component,
            "message": self.message,
            "recommendation": self.recommendation,
            "details": self.details,
            "timestamp": self.timestamp
        }

    def __str__(self) -> str:
        icon = "❌" if self.severity == "ERROR" else "⚠️" if self.severity == "WARNING" else "ℹ️"
        return f"{icon} [{self.severity}] {self.component}: {self.message}\n   → {self.recommendation}"


class QualityValidator:
    """Validates transcript quality and generates quality reports"""

    def __init__(self, config: Dict = None):
        """Initialize validator with configurable thresholds"""
        self.config = config or {}

        # Default thresholds (can be overridden in config)
        self.confidence_error_threshold = self.config.get("confidence_error_threshold", 0.50)
        self.confidence_warning_threshold = self.config.get("confidence_warning_threshold", 0.70)
        self.min_markers_per_segment = self.config.get("min_markers_per_segment", 0.05)  # 5% of segments should have markers
        self.min_speaker_coverage = self.config.get("min_speaker_coverage", 0.95)  # 95% of segments should have speaker labels

    def validate_transcript(self, transcript_json: Dict, prosody_json: Dict = None) -> List[QualityIssue]:
        """
        Validate complete transcript quality

        Args:
            transcript_json: Main transcript JSON with segments
            prosody_json: Optional prosody JSON with features

        Returns:
            List of QualityIssue objects
        """
        issues = []

        # Run all validation checks
        issues.extend(self._validate_speaker_labels(transcript_json))
        issues.extend(self._validate_ato_markers(transcript_json))
        issues.extend(self._validate_confidence(transcript_json))
        issues.extend(self._validate_prosody(prosody_json))
        issues.extend(self._validate_completeness(transcript_json))

        return issues

    def _validate_speaker_labels(self, transcript_json: Dict) -> List[QualityIssue]:
        """Validate speaker label quality"""
        issues = []
        segments = transcript_json.get("segments", [])

        if not segments:
            return [QualityIssue(
                severity=QualityIssue.SEVERITY_ERROR,
                component="Transcript Structure",
                message="No segments found in transcript",
                recommendation="Check transcription pipeline - transcript appears empty"
            )]

        # Count segments with/without speaker labels
        total_segments = len(segments)
        segments_with_speakers = sum(1 for s in segments if s.get("speaker") is not None)
        segments_with_unknown = sum(1 for s in segments if s.get("speaker") == "Unknown")

        speaker_coverage = segments_with_speakers / total_segments if total_segments > 0 else 0

        # Check if ALL segments have no speaker labels
        if segments_with_speakers == 0:
            issues.append(QualityIssue(
                severity=QualityIssue.SEVERITY_ERROR,
                component="Speaker Diarization",
                message="No speaker labels detected in any segment",
                recommendation="Enable speaker diarization in SVT GUI or check HF_TOKEN in .env file",
                details={
                    "total_segments": total_segments,
                    "segments_with_speakers": 0,
                    "speaker_coverage": "0%"
                }
            ))

        # Check if MOST segments are "Unknown"
        elif segments_with_unknown > total_segments * 0.8:
            issues.append(QualityIssue(
                severity=QualityIssue.SEVERITY_WARNING,
                component="Speaker Diarization",
                message=f"{segments_with_unknown}/{total_segments} segments labeled as 'Unknown'",
                recommendation="Speaker names may not be configured. Check Memory/*.yaml files or speaker mapping.",
                details={
                    "total_segments": total_segments,
                    "unknown_segments": segments_with_unknown,
                    "unknown_percentage": f"{(segments_with_unknown/total_segments)*100:.1f}%"
                }
            ))

        # Check if speaker coverage is low
        elif speaker_coverage < self.min_speaker_coverage:
            issues.append(QualityIssue(
                severity=QualityIssue.SEVERITY_WARNING,
                component="Speaker Diarization",
                message=f"Only {speaker_coverage*100:.1f}% of segments have speaker labels",
                recommendation="Some segments missing speaker labels - may indicate diarization issues",
                details={
                    "total_segments": total_segments,
                    "segments_with_speakers": segments_with_speakers,
                    "speaker_coverage": f"{speaker_coverage*100:.1f}%"
                }
            ))

        return issues

    def _validate_ato_markers(self, transcript_json: Dict) -> List[QualityIssue]:
        """Validate ATO marker quality"""
        issues = []
        segments = transcript_json.get("segments", [])

        if not segments:
            return []

        # Count segments with markers
        total_segments = len(segments)
        segments_with_markers = sum(1 for s in segments if len(s.get("ato_markers", [])) > 0)

        # Count total markers and unique markers
        all_markers = []
        for s in segments:
            all_markers.extend(s.get("ato_markers", []))

        total_markers = len(all_markers)
        unique_markers = len(set(all_markers))

        # Check if NO markers detected
        if total_markers == 0:
            issues.append(QualityIssue(
                severity=QualityIssue.SEVERITY_WARNING,
                component="ATO Marker Detection",
                message="No ATO markers detected in transcript",
                recommendation="Check if ATO detection is enabled or if markers exist in curated_markers.json",
                details={
                    "total_segments": total_segments,
                    "segments_with_markers": 0,
                    "marker_coverage": "0%"
                }
            ))

        # Check if ONLY ONE unique marker (suspicious)
        elif unique_markers == 1:
            issues.append(QualityIssue(
                severity=QualityIssue.SEVERITY_ERROR,
                component="ATO Marker Detection",
                message=f"Only one unique marker detected: {all_markers[0]}",
                recommendation="This is likely a bug - check for stale Python cache. Run: find . -name '__pycache__' -type d -exec rm -rf {{}} + 2>/dev/null",
                details={
                    "marker": all_markers[0],
                    "occurrences": total_markers,
                    "unique_markers": 1
                }
            ))

        # Check if marker diversity is low
        elif unique_markers < 3 and total_markers > 5:
            issues.append(QualityIssue(
                severity=QualityIssue.SEVERITY_WARNING,
                component="ATO Marker Detection",
                message=f"Low marker diversity: {unique_markers} unique markers across {total_markers} occurrences",
                recommendation="Marker detection may be too narrow - check marker configuration",
                details={
                    "unique_markers": unique_markers,
                    "total_markers": total_markers,
                    "markers": list(set(all_markers))
                }
            ))

        # Check marker coverage
        marker_coverage = segments_with_markers / total_segments if total_segments > 0 else 0
        if total_markers > 0 and marker_coverage < self.min_markers_per_segment:
            issues.append(QualityIssue(
                severity=QualityIssue.SEVERITY_INFO,
                component="ATO Marker Detection",
                message=f"Low marker coverage: only {marker_coverage*100:.1f}% of segments have markers",
                recommendation="This may be normal for non-therapeutic content or low marker confidence",
                details={
                    "segments_with_markers": segments_with_markers,
                    "total_segments": total_segments,
                    "marker_coverage": f"{marker_coverage*100:.1f}%"
                }
            ))

        return issues

    def _validate_confidence(self, transcript_json: Dict) -> List[QualityIssue]:
        """Validate transcription confidence scores"""
        issues = []
        segments = transcript_json.get("segments", [])

        if not segments:
            return []

        # Calculate average confidence
        confidences = [s.get("confidence", 0.0) for s in segments]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Count low confidence segments
        low_confidence_segments = sum(1 for c in confidences if c < self.confidence_warning_threshold)
        very_low_confidence_segments = sum(1 for c in confidences if c < self.confidence_error_threshold)

        # Check for very low average confidence (ERROR)
        if avg_confidence < self.confidence_error_threshold:
            issues.append(QualityIssue(
                severity=QualityIssue.SEVERITY_ERROR,
                component="Transcription Quality",
                message=f"Very low average confidence: {avg_confidence*100:.1f}%",
                recommendation="Audio quality is poor. Try: 1) Use larger Whisper model (medium/large), 2) Enable audio preprocessing, 3) Check original audio quality",
                details={
                    "average_confidence": f"{avg_confidence*100:.1f}%",
                    "segments_below_50%": very_low_confidence_segments,
                    "segments_below_70%": low_confidence_segments,
                    "total_segments": len(segments)
                }
            ))

        # Check for low average confidence (WARNING)
        elif avg_confidence < self.confidence_warning_threshold:
            issues.append(QualityIssue(
                severity=QualityIssue.SEVERITY_WARNING,
                component="Transcription Quality",
                message=f"Low average confidence: {avg_confidence*100:.1f}%",
                recommendation="Consider using a larger Whisper model or enabling audio preprocessing",
                details={
                    "average_confidence": f"{avg_confidence*100:.1f}%",
                    "segments_below_70%": low_confidence_segments,
                    "total_segments": len(segments)
                }
            ))

        # Check for many individual low-confidence segments
        if low_confidence_segments > len(segments) * 0.3:  # More than 30% low confidence
            issues.append(QualityIssue(
                severity=QualityIssue.SEVERITY_WARNING,
                component="Transcription Quality",
                message=f"{low_confidence_segments}/{len(segments)} segments have confidence < {self.confidence_warning_threshold*100:.0f}%",
                recommendation="Many segments have low confidence - review transcript carefully",
                details={
                    "low_confidence_segments": low_confidence_segments,
                    "total_segments": len(segments),
                    "percentage": f"{(low_confidence_segments/len(segments))*100:.1f}%"
                }
            ))

        return issues

    def _validate_prosody(self, prosody_json: Dict) -> List[QualityIssue]:
        """Validate prosody feature completeness"""
        issues = []

        if not prosody_json:
            issues.append(QualityIssue(
                severity=QualityIssue.SEVERITY_INFO,
                component="Prosody Analysis",
                message="No prosody data available",
                recommendation="Enable prosody analysis in SVT GUI for deeper insights",
                details={"prosody_enabled": False}
            ))
            return issues

        segments = prosody_json.get("segments", [])

        if not segments:
            issues.append(QualityIssue(
                severity=QualityIssue.SEVERITY_WARNING,
                component="Prosody Analysis",
                message="Prosody analysis enabled but no segment data",
                recommendation="Check prosody extractor - may have failed silently",
                details={"prosody_segments": 0}
            ))
            return issues

        # Check for missing prosody features
        required_features = ["tempo_bpm", "pitch_mean", "energy_mean", "pause_before_ms"]
        missing_features = {feature: 0 for feature in required_features}

        for segment in segments:
            for feature in required_features:
                if segment.get(feature) is None:
                    missing_features[feature] += 1

        total_segments = len(segments)

        for feature, missing_count in missing_features.items():
            if missing_count > 0:
                issues.append(QualityIssue(
                    severity=QualityIssue.SEVERITY_WARNING,
                    component="Prosody Analysis",
                    message=f"Missing '{feature}' in {missing_count}/{total_segments} segments",
                    recommendation="Prosody extraction may be incomplete - check audio quality or segment duration",
                    details={
                        "feature": feature,
                        "missing_count": missing_count,
                        "total_segments": total_segments,
                        "percentage": f"{(missing_count/total_segments)*100:.1f}%"
                    }
                ))

        return issues

    def _validate_completeness(self, transcript_json: Dict) -> List[QualityIssue]:
        """Validate overall transcript completeness"""
        issues = []

        # Check for required metadata
        required_meta = ["file", "duration_seconds", "model"]
        meta = transcript_json.get("meta", {})

        for field in required_meta:
            if field not in meta or meta[field] is None:
                issues.append(QualityIssue(
                    severity=QualityIssue.SEVERITY_WARNING,
                    component="Transcript Metadata",
                    message=f"Missing metadata field: '{field}'",
                    recommendation="Transcript metadata incomplete - may affect reproducibility",
                    details={"missing_field": field}
                ))

        # Check for empty transcript
        segments = transcript_json.get("segments", [])
        total_text = " ".join(s.get("text", "") for s in segments).strip()

        if not total_text:
            issues.append(QualityIssue(
                severity=QualityIssue.SEVERITY_ERROR,
                component="Transcript Content",
                message="Transcript contains no text",
                recommendation="Transcription completely failed - check audio file and Whisper model",
                details={"total_segments": len(segments)}
            ))

        return issues

    def generate_quality_report(self, issues: List[QualityIssue], output_path: Optional[Path] = None) -> Dict:
        """
        Generate quality report from issues

        Args:
            issues: List of QualityIssue objects
            output_path: Optional path to save JSON report

        Returns:
            Quality report as dictionary
        """
        # Categorize issues by severity
        errors = [i for i in issues if i.severity == QualityIssue.SEVERITY_ERROR]
        warnings = [i for i in issues if i.severity == QualityIssue.SEVERITY_WARNING]
        info = [i for i in issues if i.severity == QualityIssue.SEVERITY_INFO]

        # Build report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_issues": len(issues),
                "errors": len(errors),
                "warnings": len(warnings),
                "info": len(info),
                "quality_status": self._determine_quality_status(errors, warnings)
            },
            "issues": [issue.to_dict() for issue in issues]
        }

        # Save to file if requested
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

        return report

    def _determine_quality_status(self, errors: List, warnings: List) -> str:
        """Determine overall quality status"""
        if len(errors) > 0:
            return "POOR"
        elif len(warnings) > 2:
            return "FAIR"
        elif len(warnings) > 0:
            return "GOOD"
        else:
            return "EXCELLENT"

    def print_quality_report(self, issues: List[QualityIssue]) -> None:
        """Print human-readable quality report to console"""
        if not issues:
            print("✅ Quality validation passed - no issues found!")
            return

        errors = [i for i in issues if i.severity == QualityIssue.SEVERITY_ERROR]
        warnings = [i for i in issues if i.severity == QualityIssue.SEVERITY_WARNING]
        info = [i for i in issues if i.severity == QualityIssue.SEVERITY_INFO]

        print("\n" + "="*80)
        print("📊 QUALITY VALIDATION REPORT")
        print("="*80)

        # Summary
        status = self._determine_quality_status(errors, warnings)
        status_icon = "❌" if status == "POOR" else "⚠️" if status == "FAIR" else "✅"
        print(f"\n{status_icon} Overall Status: {status}")
        print(f"   Total Issues: {len(issues)} ({len(errors)} errors, {len(warnings)} warnings, {len(info)} info)")

        # Print errors
        if errors:
            print(f"\n❌ ERRORS ({len(errors)}):")
            for issue in errors:
                print(f"\n{issue}")

        # Print warnings
        if warnings:
            print(f"\n⚠️  WARNINGS ({len(warnings)}):")
            for issue in warnings:
                print(f"\n{issue}")

        # Print info
        if info:
            print(f"\nℹ️  INFORMATION ({len(info)}):")
            for issue in info:
                print(f"\n{issue}")

        print("\n" + "="*80 + "\n")


# Standalone test
if __name__ == "__main__":
    print("Testing Quality Validator...\n")

    # Test case 1: Perfect transcript
    perfect_transcript = {
        "meta": {
            "file": "test.m4a",
            "duration_seconds": 120,
            "model": "base"
        },
        "segments": [
            {
                "id": 0,
                "speaker": "Patient",
                "text": "Hello, how are you?",
                "confidence": 0.95,
                "ato_markers": ["ATO_GREETING", "ATO_QUESTION"]
            },
            {
                "id": 1,
                "speaker": "Therapeut",
                "text": "I'm fine, thank you.",
                "confidence": 0.92,
                "ato_markers": ["ATO_RESPONSE", "ATO_GRATITUDE"]
            }
        ]
    }

    perfect_prosody = {
        "segments": [
            {"tempo_bpm": 120, "pitch_mean": 150, "energy_mean": 0.05, "pause_before_ms": 500},
            {"tempo_bpm": 115, "pitch_mean": 180, "energy_mean": 0.04, "pause_before_ms": 300}
        ]
    }

    validator = QualityValidator()

    print("Test 1: Perfect Transcript")
    issues = validator.validate_transcript(perfect_transcript, perfect_prosody)
    validator.print_quality_report(issues)

    # Test case 2: Problematic transcript
    problematic_transcript = {
        "meta": {"file": "test.m4a"},  # Missing duration and model
        "segments": [
            {
                "id": 0,
                "speaker": None,  # Missing speaker
                "text": "Hello",
                "confidence": 0.35,  # Low confidence
                "ato_markers": ["ATO_OFFENDED_SILENCE"]  # Only one marker
            },
            {
                "id": 1,
                "speaker": None,
                "text": "World",
                "confidence": 0.42,
                "ato_markers": ["ATO_OFFENDED_SILENCE"]  # Same marker
            },
            {
                "id": 2,
                "speaker": None,
                "text": "Test",
                "confidence": 0.38,
                "ato_markers": ["ATO_OFFENDED_SILENCE"]  # Same marker
            }
        ]
    }

    print("\nTest 2: Problematic Transcript")
    issues = validator.validate_transcript(problematic_transcript)
    validator.print_quality_report(issues)

    # Generate JSON report
    report = validator.generate_quality_report(issues)
    print(f"\nJSON Report Keys: {list(report.keys())}")
    print(f"Quality Status: {report['summary']['quality_status']}")
