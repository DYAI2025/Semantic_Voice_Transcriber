#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model Download and Caching Utility

Pre-downloads pyannote.audio models to local cache to avoid download delays
during first-time usage. This significantly improves startup time for
diarization and speaker embedding features.

Usage:
    python3 -m svt_core.audio.download_models
    python3 -m svt_core.audio.download_models --token YOUR_HF_TOKEN
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Optional, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_hf_token(token: Optional[str] = None) -> Optional[str]:
    """
    Get Hugging Face token from argument, environment, or .env file

    Args:
        token: Optional token passed as argument

    Returns:
        HF token string or None if not found
    """
    # Priority 1: Argument
    if token:
        return token

    # Priority 2: Environment variable
    if 'HF_TOKEN' in os.environ:
        return os.environ['HF_TOKEN']

    # Priority 3: .env file
    env_path = Path.cwd() / '.env'
    if env_path.exists():
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('HF_TOKEN='):
                        return line.split('=', 1)[1].strip()
        except Exception as e:
            logger.warning(f"Failed to read .env file: {e}")

    return None


def download_models(hf_token: Optional[str] = None, force: bool = False) -> bool:
    """
    Download all required pyannote.audio models to cache

    Args:
        hf_token: Hugging Face authentication token
        force: Force re-download even if models are cached

    Returns:
        True if all models downloaded successfully, False otherwise
    """
    hf_token = get_hf_token(hf_token)

    if not hf_token:
        logger.error("❌ HF_TOKEN not set.")
        logger.error("")
        logger.error("To use speaker diarization, you need a Hugging Face token:")
        logger.error("1. Create account at https://huggingface.co/join")
        logger.error("2. Accept model agreements:")
        logger.error("   - https://huggingface.co/pyannote/segmentation-3.0")
        logger.error("   - https://huggingface.co/pyannote/speaker-diarization-3.1")
        logger.error("3. Create token at https://huggingface.co/settings/tokens")
        logger.error("4. Set token:")
        logger.error("   export HF_TOKEN=hf_YourTokenHere")
        logger.error("   OR create .env file with: HF_TOKEN=hf_YourTokenHere")
        return False

    # Define models to download
    models = [
        {
            'name': 'pyannote/speaker-diarization-3.1',
            'type': 'pipeline',
            'description': 'Speaker diarization pipeline'
        },
        {
            'name': 'pyannote/segmentation-3.0',
            'type': 'model',
            'description': 'Speech segmentation model (used by diarization & OSD)'
        },
        {
            'name': 'pyannote/embedding',
            'type': 'model',
            'description': 'Speaker embedding extraction model'
        }
    ]

    logger.info("=" * 70)
    logger.info("PYANNOTE MODEL DOWNLOADER")
    logger.info("=" * 70)
    logger.info(f"Downloading {len(models)} models to local cache...")
    logger.info("")

    success_count = 0
    failed_models: List[str] = []

    for idx, model_info in enumerate(models, 1):
        model_name = model_info['name']
        model_type = model_info['type']
        description = model_info['description']

        logger.info(f"[{idx}/{len(models)}] {model_name}")
        logger.info(f"       {description}")

        try:
            if model_type == 'pipeline':
                from pyannote.audio import Pipeline
                logger.info("       Loading pipeline...")
                pipeline = Pipeline.from_pretrained(model_name, use_auth_token=hf_token)
                logger.info("       ✅ Pipeline loaded successfully")
            else:  # model_type == 'model'
                from pyannote.audio import Model
                logger.info("       Loading model...")
                model = Model.from_pretrained(model_name, use_auth_token=hf_token)
                logger.info("       ✅ Model loaded successfully")

            success_count += 1
            logger.info("")

        except Exception as e:
            logger.error(f"       ❌ Failed to download {model_name}")
            logger.error(f"       Error: {e}")
            logger.info("")
            failed_models.append(model_name)

    # Summary
    logger.info("=" * 70)
    logger.info("DOWNLOAD SUMMARY")
    logger.info("=" * 70)
    logger.info(f"✅ Successfully downloaded: {success_count}/{len(models)} models")

    if failed_models:
        logger.error(f"❌ Failed to download: {len(failed_models)} models")
        for model in failed_models:
            logger.error(f"   - {model}")
        logger.info("")
        logger.error("Please check your HF_TOKEN and internet connection.")
        return False
    else:
        logger.info("")
        logger.info("🎉 All models downloaded successfully!")
        logger.info("")
        logger.info("Models are cached at: ~/.cache/torch/pyannote/")
        logger.info("Future diarization runs will load instantly from cache.")
        return True


def check_models_cached() -> Dict[str, bool]:
    """
    Check if models are cached locally

    Returns:
        Dict mapping model names to cached status (True/False)
    """
    cache_dir = Path.home() / ".cache" / "torch" / "pyannote"

    models = [
        'pyannote/speaker-diarization-3.1',
        'pyannote/segmentation-3.0',
        'pyannote/embedding'
    ]

    status = {}

    if not cache_dir.exists():
        logger.warning(f"Cache directory does not exist: {cache_dir}")
        return {model: False for model in models}

    # Simple heuristic: check if cache directory has content
    # More sophisticated: check specific model directories
    cached_items = list(cache_dir.glob("*"))
    has_cache = len(cached_items) >= 3  # Expect at least 3 model directories

    for model in models:
        # Simplified check - assumes if cache has content, models are there
        status[model] = has_cache

    return status


def print_cache_status():
    """Print current cache status"""
    status = check_models_cached()

    logger.info("=" * 70)
    logger.info("MODEL CACHE STATUS")
    logger.info("=" * 70)

    all_cached = all(status.values())

    for model, cached in status.items():
        icon = "✅" if cached else "❌"
        state = "CACHED" if cached else "NOT CACHED"
        logger.info(f"{icon} {model}: {state}")

    logger.info("")
    if all_cached:
        logger.info("✅ All models are cached. Diarization will start instantly.")
    else:
        logger.info("⚠️  Some models are not cached. Run this script to download them:")
        logger.info("   python3 -m svt_core.audio.download_models")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Download and cache pyannote.audio models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download using HF_TOKEN from environment or .env
  python3 -m svt_core.audio.download_models

  # Download using explicit token
  python3 -m svt_core.audio.download_models --token hf_YourTokenHere

  # Check cache status without downloading
  python3 -m svt_core.audio.download_models --status

  # Force re-download
  python3 -m svt_core.audio.download_models --force
        """
    )

    parser.add_argument(
        '--token',
        type=str,
        help='Hugging Face authentication token'
    )

    parser.add_argument(
        '--status',
        action='store_true',
        help='Check cache status without downloading'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-download even if cached'
    )

    args = parser.parse_args()

    if args.status:
        print_cache_status()
        return

    # Download models
    success = download_models(hf_token=args.token, force=args.force)

    if success:
        logger.info("")
        print_cache_status()
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
