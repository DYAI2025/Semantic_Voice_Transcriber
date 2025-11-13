"""
Whisper Large-v3 Transcriber
Optimized for German therapeutic conversations with maximum quality
"""

import whisper
import torch
import numpy as np
import logging
import time
import psutil
from typing import Dict, List, Optional
from pathlib import Path
import math

logger = logging.getLogger(__name__)


class WhisperTranscriberV3:
    """
    Whisper large-v3 integration with optimization for quality and performance
    """

    # Model size mappings
    MODEL_SIZES = {
        'tiny': 'tiny',
        'base': 'base',
        'small': 'small',
        'medium': 'medium',
        'large': 'large-v2',
        'large-v3': 'large-v3',  # NEW: Latest and best model
    }

    def __init__(
        self,
        model_size: str = "large-v3",
        device: str = "auto",
        compute_type: str = "auto"
    ):
        """
        Initialize Whisper transcriber

        Args:
            model_size: Model size ('tiny', 'base', 'small', 'medium', 'large', 'large-v3')
            device: 'cpu', 'cuda', or 'auto'
            compute_type: 'int8', 'float16', 'float32', or 'auto'
        """
        self.model_size = self._resolve_model_size(model_size)
        self.device = self._resolve_device(device)
        self.compute_type = self._resolve_compute_type(compute_type, self.device)

        logger.info(f"🎤 Initializing Whisper {self.model_size}")
        logger.info(f"   Device: {self.device}")
        logger.info(f"   Compute: {self.compute_type}")

        # Load model
        start_time = time.time()
        self.model = whisper.load_model(
            self.model_size,
            device=self.device
        )
        load_time = time.time() - start_time

        logger.info(f"✅ Model loaded in {load_time:.1f}s")

        # Get model info
        self._log_model_info()

    def _resolve_model_size(self, size: str) -> str:
        """Resolve model size alias to actual model name"""
        return self.MODEL_SIZES.get(size.lower(), size)

    def _resolve_device(self, device: str) -> str:
        """Auto-detect best device if 'auto'"""
        if device == "auto":
            if torch.cuda.is_available():
                device = "cuda"
                logger.info(f"🚀 CUDA available: {torch.cuda.get_device_name(0)}")
            else:
                device = "cpu"
                logger.info("💻 Using CPU")
        return device

    def _resolve_compute_type(self, compute_type: str, device: str) -> str:
        """Auto-select compute type based on device"""
        if compute_type == "auto":
            if device == "cuda":
                # FP16 on GPU: 2x faster, half memory
                compute_type = "float16"
            else:
                # INT8 on CPU: faster, less memory
                # Note: Whisper doesn't natively support INT8, so we use float32
                compute_type = "float32"

        return compute_type

    def _log_model_info(self):
        """Log model size and memory usage"""
        if self.device == "cuda":
            memory_allocated = torch.cuda.memory_allocated() / 1024**3
            memory_reserved = torch.cuda.memory_reserved() / 1024**3
            logger.info(f"📊 GPU Memory: {memory_allocated:.2f}GB allocated, {memory_reserved:.2f}GB reserved")
        else:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            logger.info(f"📊 CPU Memory: {memory_mb:.0f}MB")

    def transcribe(
        self,
        audio_path: str,
        language: str = "de",
        task: str = "transcribe",
        **kwargs
    ) -> Dict:
        """
        Transcribe audio file with Whisper large-v3

        Args:
            audio_path: Path to audio file
            language: Language code (de, en, etc.)
            task: 'transcribe' or 'translate'
            **kwargs: Additional whisper.transcribe() parameters

        Returns:
            Dict with:
                - text: Full transcription
                - segments: List of segment dicts with timestamps
                - language: Detected/specified language
                - metadata: Processing info
        """
        logger.info(f"🎯 Transcribing: {Path(audio_path).name}")
        logger.info(f"   Language: {language}")

        start_time = time.time()
        start_memory = self._get_memory_usage()

        # Optimal settings for quality
        transcribe_options = {
            'language': language,
            'task': task,
            'verbose': False,

            # Quality settings
            'beam_size': 5,  # Beam search for better quality
            'best_of': 5,    # Consider top 5 candidates

            # Temperature fallback for low confidence segments
            'temperature': (0.0, 0.2, 0.4, 0.6, 0.8, 1.0),

            # Context from previous text improves accuracy
            'condition_on_previous_text': True,

            # VAD (Voice Activity Detection)
            'no_speech_threshold': 0.6,
            'logprob_threshold': -1.0,

            # Compression ratio threshold (detect repetitions)
            'compression_ratio_threshold': 2.4,

            # FP16 for GPU
            'fp16': (self.device == "cuda"),
        }

        # Merge with user-provided options
        transcribe_options.update(kwargs)

        # Transcribe
        result = self.model.transcribe(audio_path, **transcribe_options)

        # Processing time and memory
        processing_time = time.time() - start_time
        end_memory = self._get_memory_usage()
        memory_used = end_memory - start_memory

        # Calculate metrics
        audio_duration = self._get_audio_duration(result)
        real_time_factor = audio_duration / processing_time if processing_time > 0 else 0

        logger.info(f"✅ Transcription complete")
        logger.info(f"   Duration: {audio_duration:.1f}s")
        logger.info(f"   Processing: {processing_time:.1f}s ({real_time_factor:.1f}x real-time)")
        logger.info(f"   Memory: +{memory_used:.0f}MB")

        # Enhance segments with confidence scores
        result['segments'] = self._enhance_segments(result.get('segments', []))

        # Add metadata
        result['metadata'] = {
            'model': self.model_size,
            'device': self.device,
            'compute_type': self.compute_type,
            'processing_time': processing_time,
            'real_time_factor': real_time_factor,
            'memory_used_mb': memory_used,
            'audio_duration': audio_duration,
        }

        return result

    def _enhance_segments(self, segments: List[Dict]) -> List[Dict]:
        """
        Add confidence scores and quality metrics to segments

        Whisper provides:
        - avg_logprob: Average log probability (negative)
        - no_speech_prob: Probability of silence

        We convert to confidence score (0-1)
        """
        enhanced = []

        for seg in segments:
            # Calculate confidence from logprob
            avg_logprob = seg.get('avg_logprob', -1.0)
            no_speech_prob = seg.get('no_speech_prob', 0.5)

            # Convert logprob to probability (0-1)
            # logprob is negative, so exp(logprob) gives probability
            prob = math.exp(avg_logprob)

            # Adjust by speech detection confidence
            # If no_speech_prob is high, confidence should be low
            confidence = prob * (1 - no_speech_prob)

            # Clamp to [0, 1]
            confidence = min(max(confidence, 0.0), 1.0)

            # Classify confidence level
            if confidence >= 0.9:
                confidence_level = "very_high"
            elif confidence >= 0.7:
                confidence_level = "high"
            elif confidence >= 0.5:
                confidence_level = "medium"
            elif confidence >= 0.3:
                confidence_level = "low"
            else:
                confidence_level = "very_low"

            enhanced.append({
                'id': seg.get('id', len(enhanced)),
                'start': seg['start'],
                'end': seg['end'],
                'text': seg['text'].strip(),
                'confidence': round(confidence, 3),
                'confidence_level': confidence_level,
                'avg_logprob': avg_logprob,
                'no_speech_prob': no_speech_prob,
                'compression_ratio': seg.get('compression_ratio', 1.0),
            })

        return enhanced

    def _get_audio_duration(self, result: Dict) -> float:
        """Calculate total audio duration from segments"""
        segments = result.get('segments', [])
        if segments:
            return segments[-1]['end']
        return 0.0

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        if self.device == "cuda":
            return torch.cuda.memory_allocated() / 1024 / 1024
        else:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024

    def transcribe_batch(
        self,
        audio_paths: List[str],
        **kwargs
    ) -> List[Dict]:
        """
        Transcribe multiple audio files

        Args:
            audio_paths: List of audio file paths
            **kwargs: Arguments passed to transcribe()

        Returns:
            List of transcription results
        """
        results = []

        for i, audio_path in enumerate(audio_paths, 1):
            logger.info(f"📝 Batch progress: {i}/{len(audio_paths)}")

            try:
                result = self.transcribe(audio_path, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"❌ Failed to transcribe {audio_path}: {e}")
                results.append({
                    'error': str(e),
                    'audio_path': audio_path
                })

        logger.info(f"✅ Batch complete: {len(results)} files processed")
        return results

    def get_model_info(self) -> Dict:
        """Get information about loaded model"""
        return {
            'model_size': self.model_size,
            'device': self.device,
            'compute_type': self.compute_type,
            'cuda_available': torch.cuda.is_available(),
            'cuda_device': torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        }

    @staticmethod
    def list_available_models() -> List[str]:
        """List all available Whisper models"""
        return list(WhisperTranscriberV3.MODEL_SIZES.values())

    @staticmethod
    def estimate_memory_requirement(model_size: str, device: str = "cuda") -> Dict:
        """
        Estimate memory requirements for a model

        Returns:
            Dict with estimated memory in GB
        """
        # Approximate model sizes (parameters)
        model_params = {
            'tiny': 39,      # 39M parameters
            'base': 74,      # 74M
            'small': 244,    # 244M
            'medium': 769,   # 769M
            'large-v2': 1550,  # 1.55B
            'large-v3': 1550,  # 1.55B
        }

        params = model_params.get(model_size, 1550) * 1_000_000

        if device == "cuda":
            # FP16: 2 bytes per parameter
            # Add 50% overhead for activations
            memory_gb = (params * 2 * 1.5) / 1024**3
        else:
            # FP32: 4 bytes per parameter
            memory_gb = (params * 4 * 1.5) / 1024**3

        return {
            'model_size': model_size,
            'parameters': f"{params/1_000_000:.0f}M",
            'estimated_memory_gb': round(memory_gb, 1),
            'device': device,
            'recommendation': (
                "Recommended" if memory_gb < 8
                else "Possible but may be slow" if memory_gb < 16
                else "Requires high-end GPU"
            )
        }


def benchmark_models(audio_path: str, models: List[str] = None) -> Dict:
    """
    Benchmark different Whisper models on the same audio

    Args:
        audio_path: Test audio file
        models: List of model sizes to test (default: all)

    Returns:
        Dict with benchmark results
    """
    if models is None:
        models = ['base', 'small', 'medium', 'large-v3']

    results = {}

    for model_size in models:
        logger.info(f"\n{'='*60}")
        logger.info(f"Benchmarking: {model_size}")
        logger.info(f"{'='*60}")

        try:
            transcriber = WhisperTranscriberV3(model_size=model_size)
            result = transcriber.transcribe(audio_path)

            results[model_size] = {
                'success': True,
                'processing_time': result['metadata']['processing_time'],
                'real_time_factor': result['metadata']['real_time_factor'],
                'memory_used_mb': result['metadata']['memory_used_mb'],
                'text_length': len(result['text']),
                'segment_count': len(result['segments']),
                'avg_confidence': np.mean([s['confidence'] for s in result['segments']])
            }

        except Exception as e:
            logger.error(f"❌ Failed: {e}")
            results[model_size] = {
                'success': False,
                'error': str(e)
            }

    return results


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    print("\n🎤 Whisper Transcriber V3 (large-v3)")
    print("=" * 60)

    # Show available models
    print("\n📋 Available models:")
    for model in WhisperTranscriberV3.list_available_models():
        info = WhisperTranscriberV3.estimate_memory_requirement(model)
        print(f"  • {model:12} - {info['parameters']:6} params - ~{info['estimated_memory_gb']}GB RAM - {info['recommendation']}")

    # Test with a sample audio file if provided
    import sys
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        print(f"\n🎯 Testing with: {audio_file}")

        # Test large-v3
        transcriber = WhisperTranscriberV3(model_size="large-v3")
        result = transcriber.transcribe(audio_file)

        print(f"\n📝 Transcription:")
        print(result['text'])

        print(f"\n📊 Segments ({len(result['segments'])}):")
        for seg in result['segments'][:3]:  # Show first 3
            print(f"  [{seg['start']:.1f}s - {seg['end']:.1f}s] (conf: {seg['confidence']:.2f})")
            print(f"  {seg['text']}")

        print(f"\n⚙️ Metadata:")
        for key, value in result['metadata'].items():
            print(f"  {key}: {value}")

    else:
        print("\n💡 Usage: python3 whisper_transcriber_v3.py <audio_file>")
        print("   Tests transcription with Whisper large-v3")
