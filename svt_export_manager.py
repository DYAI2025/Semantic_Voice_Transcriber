#!/usr/bin/env python3
"""
SVT Export Manager - Unified export interface
Handles PDF, DOCX, and JSON exports

Usage:
    from svt_export_manager import ExportManager
    
    exporter = ExportManager()
    exporter.export(transcript_data, "/output/session", format="pdf")
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class ExportManager:
    """
    Unified export manager for SVT Local.
    Supports PDF, DOCX, and JSON formats.
    """
    
    SUPPORTED_FORMATS = ["pdf", "docx", "json"]
    
    def __init__(self, output_dir: str = "./exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Import export modules
        try:
            from svt_export_pdf import generate_pdf
            from svt_export_docx import generate_docx
            self.pdf_available = True
            self.docx_available = True
        except ImportError as e:
            self.pdf_available = False
            self.docx_available = False
            print(f"⚠️ Export module not available: {e}")
    
    def export(
        self,
        transcript_data: List[Dict[str, Any]],
        base_filename: str,
        format: str = "pdf",
        include_analysis: bool = True,
        analysis_text: str = "",
        patient_name: str = "",
        therapist_name: str = "",
        session_date: str = ""
    ) -> Dict[str, str]:
        """
        Export transcript to specified format.
        
        Args:
            transcript_data: List of transcript segments
            base_filename: Output filename (without extension)
            format: Export format (pdf, docx, json)
            include_analysis: Include analysis section
            analysis_text: Analysis content
            patient_name: Patient name
            therapist_name: Therapist name
            session_date: Session date
        
        Returns:
            Dict with export status and file paths
        """
        format = format.lower()
        
        if format not in self.SUPPORTED_FORMATS:
            return {
                "status": "error",
                "message": f"Unsupported format: {format}. Supported: {self.SUPPORTED_FORMATS}"
            }
        
        output_path = self.output_dir / f"{base_filename}.{format}"
        
        try:
            if format == "pdf":
                if not self.pdf_available:
                    return {"status": "error", "message": "PDF export not available (missing reportlab)"}
                return self._export_pdf(
                    transcript_data, output_path, include_analysis,
                    analysis_text, patient_name, therapist_name, session_date
                )
            
            elif format == "docx":
                if not self.docx_available:
                    return {"status": "error", "message": "DOCX export not available (missing python-docx)"}
                return self._export_docx(
                    transcript_data, output_path, include_analysis,
                    analysis_text, patient_name, therapist_name, session_date
                )
            
            elif format == "json":
                return self._export_json(transcript_data, output_path)
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def export_all(
        self,
        transcript_data: List[Dict[str, Any]],
        base_filename: str,
        include_analysis: bool = True,
        analysis_text: str = "",
        patient_name: str = "",
        therapist_name: str = "",
        session_date: str = ""
    ) -> Dict[str, str]:
        """
        Export to all available formats.
        """
        results = {}
        
        for fmt in self.SUPPORTED_FORMATS:
            result = self.export(
                transcript_data=transcript_data,
                base_filename=base_filename,
                format=fmt,
                include_analysis=include_analysis,
                analysis_text=analysis_text,
                patient_name=patient_name,
                therapist_name=therapist_name,
                session_date=session_date
            )
            results[fmt] = result
        
        # Check if all succeeded
        all_success = all(r["status"] == "success" for r in results.values())
        
        return {
            "status": "success" if all_success else "partial",
            "formats": results,
            "output_dir": str(self.output_dir)
        }
    
    def _export_pdf(
        self,
        transcript_data: List[Dict[str, Any]],
        output_path: Path,
        include_analysis: bool,
        analysis_text: str,
        patient_name: str,
        therapist_name: str,
        session_date: str
    ) -> Dict[str, str]:
        """Export to PDF format."""
        from svt_export_pdf import generate_pdf
        
        generate_pdf(
            transcript_data=transcript_data,
            output_path=str(output_path),
            title="Therapie Transkription",
            patient_name=patient_name,
            therapist_name=therapist_name,
            session_date=session_date,
            include_analysis=include_analysis,
            analysis_text=analysis_text
        )
        
        return {
            "status": "success",
            "format": "pdf",
            "path": str(output_path),
            "size_mb": os.path.getsize(output_path) / (1024 * 1024)
        }
    
    def _export_docx(
        self,
        transcript_data: List[Dict[str, Any]],
        output_path: Path,
        include_analysis: bool,
        analysis_text: str,
        patient_name: str,
        therapist_name: str,
        session_date: str
    ) -> Dict[str, str]:
        """Export to DOCX format."""
        from svt_export_docx import generate_docx
        
        generate_docx(
            transcript_data=transcript_data,
            output_path=str(output_path),
            title="Therapie Transkription",
            patient_name=patient_name,
            therapist_name=therapist_name,
            session_date=session_date,
            include_analysis=include_analysis,
            analysis_text=analysis_text
        )
        
        return {
            "status": "success",
            "format": "docx",
            "path": str(output_path),
            "size_mb": os.path.getsize(output_path) / (1024 * 1024)
        }
    
    def _export_json(
        self,
        transcript_data: List[Dict[str, Any]],
        output_path: Path
    ) -> Dict[str, str]:
        """Export to JSON format."""
        export_data = {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "svt_version": "1.0.0",
                "format": "json"
            },
            "transcript": transcript_data
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return {
            "status": "success",
            "format": "json",
            "path": str(output_path),
            "size_mb": os.path.getsize(output_path) / (1024 * 1024)
        }
    
    def get_export_stats(self, transcript_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate export statistics."""
        total_duration = 0
        total_words = 0
        speaker_counts = {}
        
        for seg in transcript_data:
            duration = seg.get("end", 0) - seg.get("start", 0)
            total_duration += duration
            
            text = seg.get("text", "")
            total_words += len(text.split()) if text else 0
            
            speaker = seg.get("speaker", "Unknown")
            if speaker not in speaker_counts:
                speaker_counts[speaker] = {"segments": 0, "words": 0}
            speaker_counts[speaker]["segments"] += 1
            speaker_counts[speaker]["words"] += len(text.split()) if text else 0
        
        return {
            "duration_seconds": total_duration,
            "duration_formatted": format_duration(total_duration),
            "word_count": total_words,
            "segment_count": len(transcript_data),
            "speakers": len(speaker_counts),
            "speaker_details": {
                spk: {
                    "segments": data["segments"],
                    "words": data["words"]
                }
                for spk, data in speaker_counts.items()
            }
        }


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    return f"{minutes}m {secs}s"


# Convenience function for GUI
def quick_export(
    transcript_data: List[Dict[str, Any]],
    output_dir: str = "./exports",
    filename: Optional[str] = None
) -> Dict[str, str]:
    """
    Quick export to all available formats.
    
    Args:
        transcript_data: Transcript segments
        output_dir: Output directory
        filename: Custom filename (auto-generated if None)
    
    Returns:
        Export results
    """
    if filename is None:
        filename = f"therapie_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    exporter = ExportManager(output_dir=output_dir)
    
    return exporter.export_all(
        transcript_data=transcript_data,
        base_filename=filename,
        include_analysis=False
    )


if __name__ == "__main__":
    # Example
    example_data = [
        {"start": 0, "end": 30, "speaker": "Therapeut", "text": "Guten Tag, wie geht es Ihnen heute?"},
        {"start": 30, "end": 90, "speaker": "Patient", "text": "Naja, es geht so."},
    ]
    
    results = quick_export(example_data)
    print(json.dumps(results, indent=2, default=str))
