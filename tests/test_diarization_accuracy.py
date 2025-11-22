#!/usr/bin/env python3
"""
Diarization Accuracy Evaluation Framework

Evaluates speaker diarization performance using ground truth annotations.
Calculates DER (Diarization Error Rate), Precision, Recall, F1 scores.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from svt_core.audio.diarization import SpeakerDiarizer
    DIARIZER_AVAILABLE = True
except ImportError:
    DIARIZER_AVAILABLE = False
    print("⚠️ SpeakerDiarizer not available - install dependencies")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DiarizationEvaluator:
    """Evaluate diarization performance against ground truth"""

    def __init__(self, collar: float = 0.25):
        """
        Initialize evaluator

        Args:
            collar: Tolerance window for segment boundaries (seconds)
        """
        self.collar = collar

    def calculate_der(
        self,
        ground_truth: List[Dict],
        predicted: List[Dict],
        total_duration: float
    ) -> Dict[str, float]:
        """
        Calculate Diarization Error Rate (DER)

        DER = (FA + MISS + CONF) / Total Speech Time

        Where:
        - FA (False Alarm): Non-speech detected as speech
        - MISS (Missed Detection): Speech not detected
        - CONF (Confusion): Wrong speaker assigned

        Args:
            ground_truth: Ground truth segments
            predicted: Predicted diarization segments
            total_duration: Total audio duration

        Returns:
            Dict with DER components and total DER
        """
        # Create timeline with 100ms resolution
        resolution = 0.1  # 100ms
        timeline_length = int(total_duration / resolution) + 1

        # Initialize timelines
        gt_timeline = np.zeros(timeline_length, dtype=object)
        pred_timeline = np.zeros(timeline_length, dtype=object)

        # Fill ground truth timeline
        for seg in ground_truth:
            start_idx = int(seg['start'] / resolution)
            end_idx = int(seg['end'] / resolution)
            gt_timeline[start_idx:end_idx] = seg['speaker']

        # Fill predicted timeline
        for seg in predicted:
            start_idx = int(seg['start'] / resolution)
            end_idx = int(seg['end'] / resolution)
            pred_timeline[start_idx:end_idx] = seg['speaker']

        # Calculate errors
        false_alarm = 0  # Predicted speech where no speech
        missed_detection = 0  # Missed speech
        speaker_confusion = 0  # Wrong speaker
        correct = 0  # Correct detection

        total_speech_time = 0

        for i in range(timeline_length):
            gt_speaker = gt_timeline[i]
            pred_speaker = pred_timeline[i]

            if gt_speaker != 0:  # Ground truth has speech
                total_speech_time += 1

                if pred_speaker == 0:  # Missed detection
                    missed_detection += 1
                elif not self._speakers_match(gt_speaker, pred_speaker):
                    # Speaker confusion (wrong speaker)
                    speaker_confusion += 1
                else:
                    # Correct detection
                    correct += 1

            elif pred_speaker != 0:  # False alarm
                false_alarm += 1

        # Calculate DER
        total_errors = false_alarm + missed_detection + speaker_confusion

        if total_speech_time > 0:
            der = (total_errors / total_speech_time) * 100
            fa_rate = (false_alarm / total_speech_time) * 100
            miss_rate = (missed_detection / total_speech_time) * 100
            conf_rate = (speaker_confusion / total_speech_time) * 100
        else:
            der = fa_rate = miss_rate = conf_rate = 0

        return {
            'DER': der,
            'false_alarm': fa_rate,
            'missed_detection': miss_rate,
            'speaker_confusion': conf_rate,
            'correct': (correct / total_speech_time * 100) if total_speech_time > 0 else 0,
            'total_speech_time_s': total_speech_time * resolution,
            'total_errors': total_errors,
            'correct_frames': correct
        }

    def _speakers_match(self, gt_speaker: str, pred_speaker: str) -> bool:
        """
        Check if speakers match (handles mapping between ground truth and predicted labels)

        This is a simple heuristic - in production, you'd want speaker mapping/alignment
        """
        # For now, exact match (since we use "Speaker A", "Speaker B" in both)
        return gt_speaker == pred_speaker

    def calculate_precision_recall_f1(
        self,
        ground_truth: List[Dict],
        predicted: List[Dict],
        per_speaker: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate Precision, Recall, F1 scores

        Args:
            ground_truth: Ground truth segments
            predicted: Predicted segments
            per_speaker: If True, calculate per-speaker metrics

        Returns:
            Dict with overall and per-speaker metrics
        """
        results = {
            'overall': {},
            'per_speaker': {}
        }

        # Get all speakers
        gt_speakers = set(seg['speaker'] for seg in ground_truth)
        pred_speakers = set(seg['speaker'] for seg in predicted)
        all_speakers = gt_speakers.union(pred_speakers)

        # Calculate per-speaker metrics
        speaker_metrics = {}

        for speaker in all_speakers:
            gt_segs = [s for s in ground_truth if s['speaker'] == speaker]
            pred_segs = [s for s in predicted if s['speaker'] == speaker]

            # Calculate overlap-based precision/recall
            tp = 0  # True positives (correctly identified segments)
            fp = 0  # False positives (incorrectly identified as this speaker)
            fn = 0  # False negatives (missed segments of this speaker)

            # Check predicted segments
            for pred_seg in pred_segs:
                matched = False
                for gt_seg in gt_segs:
                    overlap = self._calculate_overlap(pred_seg, gt_seg)
                    if overlap > 0.5:  # At least 50% overlap
                        tp += 1
                        matched = True
                        break

                if not matched:
                    fp += 1

            # Check for missed ground truth segments
            for gt_seg in gt_segs:
                matched = False
                for pred_seg in pred_segs:
                    overlap = self._calculate_overlap(gt_seg, pred_seg)
                    if overlap > 0.5:
                        matched = True
                        break

                if not matched:
                    fn += 1

            # Calculate metrics
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

            speaker_metrics[speaker] = {
                'precision': precision * 100,
                'recall': recall * 100,
                'f1': f1 * 100,
                'true_positives': tp,
                'false_positives': fp,
                'false_negatives': fn
            }

        # Calculate overall metrics (macro-average)
        if speaker_metrics:
            overall_precision = np.mean([m['precision'] for m in speaker_metrics.values()])
            overall_recall = np.mean([m['recall'] for m in speaker_metrics.values()])
            overall_f1 = np.mean([m['f1'] for m in speaker_metrics.values()])
        else:
            overall_precision = overall_recall = overall_f1 = 0

        results['overall'] = {
            'precision': overall_precision,
            'recall': overall_recall,
            'f1': overall_f1
        }

        results['per_speaker'] = speaker_metrics

        return results

    def _calculate_overlap(self, seg1: Dict, seg2: Dict) -> float:
        """Calculate overlap ratio between two segments"""
        overlap_start = max(seg1['start'], seg2['start'])
        overlap_end = min(seg1['end'], seg2['end'])
        overlap_duration = max(0, overlap_end - overlap_start)

        seg1_duration = seg1['end'] - seg1['start']

        return overlap_duration / seg1_duration if seg1_duration > 0 else 0

    def generate_confusion_matrix(
        self,
        ground_truth: List[Dict],
        predicted: List[Dict]
    ) -> Dict[str, Any]:
        """Generate confusion matrix for speaker assignments"""
        # Get all speakers
        gt_speakers = sorted(set(seg['speaker'] for seg in ground_truth))
        pred_speakers = sorted(set(seg['speaker'] for seg in predicted))

        # Initialize confusion matrix
        matrix = {gt: {pred: 0 for pred in pred_speakers} for gt in gt_speakers}

        # Fill matrix
        for gt_seg in ground_truth:
            # Find best matching predicted segment
            best_pred_seg = None
            best_overlap = 0

            for pred_seg in predicted:
                overlap = self._calculate_overlap(gt_seg, pred_seg)
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_pred_seg = pred_seg

            if best_pred_seg and best_overlap > 0.5:
                matrix[gt_seg['speaker']][best_pred_seg['speaker']] += 1

        return {
            'matrix': matrix,
            'ground_truth_speakers': gt_speakers,
            'predicted_speakers': pred_speakers
        }

    def evaluate(
        self,
        ground_truth_file: Path,
        predicted_segments: List[Dict]
    ) -> Dict[str, Any]:
        """
        Full evaluation against ground truth

        Args:
            ground_truth_file: Path to ground truth JSON
            predicted_segments: Predicted diarization segments

        Returns:
            Complete evaluation results
        """
        # Load ground truth
        with open(ground_truth_file) as f:
            ground_truth_data = json.load(f)

        gt_segments = ground_truth_data['segments']
        total_duration = ground_truth_data['duration']

        # Calculate DER
        der_results = self.calculate_der(gt_segments, predicted_segments, total_duration)

        # Calculate Precision/Recall/F1
        pr_results = self.calculate_precision_recall_f1(gt_segments, predicted_segments)

        # Generate confusion matrix
        confusion = self.generate_confusion_matrix(gt_segments, predicted_segments)

        # Compile results
        results = {
            'audio_file': ground_truth_data['audio_file'],
            'duration': total_duration,
            'num_speakers_gt': ground_truth_data['num_speakers'],
            'num_speakers_pred': len(set(seg['speaker'] for seg in predicted_segments)),
            'der': der_results,
            'precision_recall': pr_results,
            'confusion_matrix': confusion
        }

        return results


def run_evaluation_suite(diarizer: 'SpeakerDiarizer', output_dir: Path = None):
    """
    Run full evaluation suite on ground truth test set

    Args:
        diarizer: Configured SpeakerDiarizer instance
        output_dir: Directory to save results (optional)
    """
    logger.info("=" * 80)
    logger.info("DIARIZATION ACCURACY EVALUATION SUITE")
    logger.info("=" * 80)

    fixtures_dir = Path(__file__).parent / "fixtures" / "ground_truth"

    if not fixtures_dir.exists():
        logger.error(f"Ground truth directory not found: {fixtures_dir}")
        logger.error("Run generate_ground_truth.py first!")
        return None

    # Find all ground truth JSON files
    gt_files = sorted(fixtures_dir.glob("*.json"))

    if not gt_files:
        logger.error("No ground truth files found!")
        return None

    logger.info(f"Found {len(gt_files)} ground truth test files\n")

    evaluator = DiarizationEvaluator()
    all_results = []

    for gt_file in gt_files:
        audio_file = fixtures_dir / gt_file.stem.replace('.json', '') / (gt_file.stem + '.wav')

        # Handle filename
        audio_file = gt_file.parent / (gt_file.stem + '.wav')

        if not audio_file.exists():
            logger.warning(f"Audio file not found: {audio_file}")
            continue

        logger.info(f"\nEvaluating: {audio_file.name}")
        logger.info("-" * 80)

        try:
            # Run diarization
            logger.info("Running diarization...")
            predicted_segments = diarizer.diarize(audio_file)

            logger.info(f"Predicted {len(predicted_segments)} segments")

            # Evaluate
            results = evaluator.evaluate(gt_file, predicted_segments)

            # Print results
            logger.info("\n📊 Results:")
            logger.info(f"  DER: {results['der']['DER']:.2f}%")
            logger.info(f"    - False Alarm: {results['der']['false_alarm']:.2f}%")
            logger.info(f"    - Missed Detection: {results['der']['missed_detection']:.2f}%")
            logger.info(f"    - Speaker Confusion: {results['der']['speaker_confusion']:.2f}%")
            logger.info(f"    - Correct: {results['der']['correct']:.2f}%")

            logger.info(f"\n  Precision/Recall/F1 (Overall):")
            logger.info(f"    - Precision: {results['precision_recall']['overall']['precision']:.2f}%")
            logger.info(f"    - Recall: {results['precision_recall']['overall']['recall']:.2f}%")
            logger.info(f"    - F1: {results['precision_recall']['overall']['f1']:.2f}%")

            logger.info(f"\n  Per-Speaker Metrics:")
            for speaker, metrics in results['precision_recall']['per_speaker'].items():
                logger.info(f"    {speaker}:")
                logger.info(f"      - Precision: {metrics['precision']:.2f}%")
                logger.info(f"      - Recall: {metrics['recall']:.2f}%")
                logger.info(f"      - F1: {metrics['f1']:.2f}%")

            all_results.append(results)

        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Calculate aggregate metrics
    if all_results:
        logger.info("\n" + "=" * 80)
        logger.info("AGGREGATE RESULTS")
        logger.info("=" * 80)

        avg_der = np.mean([r['der']['DER'] for r in all_results])
        avg_precision = np.mean([r['precision_recall']['overall']['precision'] for r in all_results])
        avg_recall = np.mean([r['precision_recall']['overall']['recall'] for r in all_results])
        avg_f1 = np.mean([r['precision_recall']['overall']['f1'] for r in all_results])

        logger.info(f"\nAverage DER: {avg_der:.2f}%")
        logger.info(f"Average Precision: {avg_precision:.2f}%")
        logger.info(f"Average Recall: {avg_recall:.2f}%")
        logger.info(f"Average F1: {avg_f1:.2f}%")

        # Save results
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            results_file = output_dir / "baseline_results.json"

            summary = {
                'aggregate': {
                    'avg_der': avg_der,
                    'avg_precision': avg_precision,
                    'avg_recall': avg_recall,
                    'avg_f1': avg_f1
                },
                'per_file': all_results
            }

            with open(results_file, 'w') as f:
                json.dump(summary, f, indent=2)

            logger.info(f"\n✅ Results saved to: {results_file}")

        return all_results
    else:
        logger.warning("\n⚠️ No results to aggregate")
        return None


if __name__ == "__main__":
    if not DIARIZER_AVAILABLE:
        print("❌ Cannot run evaluation - SpeakerDiarizer not available")
        print("Install dependencies: pip install pyannote.audio torch")
        sys.exit(1)

    import os
    from dotenv import load_dotenv

    load_dotenv()

    hf_token = os.getenv('HF_TOKEN')

    if not hf_token:
        print("❌ HF_TOKEN not set")
        print("Set in .env file or environment variable")
        sys.exit(1)

    # Initialize diarizer
    print("Initializing diarizer...")
    diarizer = SpeakerDiarizer(
        use_auth_token=hf_token,
        min_speakers=1,
        max_speakers=5,
        timeout_seconds=120,
        enable_graceful_degradation=True
    )

    # Run evaluation
    results = run_evaluation_suite(
        diarizer,
        output_dir=Path("tests/results")
    )

    if results:
        print("\n✅ Evaluation complete!")
    else:
        print("\n❌ Evaluation failed")
        sys.exit(1)
