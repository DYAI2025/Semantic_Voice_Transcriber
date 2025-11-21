"""
Transcription Debug Logger

Provides comprehensive logging and performance monitoring for
the transcription pipeline to diagnose crashes and lags.

Features:
- Timestamped progress tracking
- Performance profiling with timers
- Detailed exception logging
- Memory usage monitoring
- Step-by-step pipeline instrumentation
"""

import logging
import time
import traceback
import psutil
import os
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from functools import wraps

# Create dedicated logger
logger = logging.getLogger("svt.transcription.debug")
logger.setLevel(logging.DEBUG)

# Create file handler for detailed logs
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"transcription_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# Create console handler for important messages
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatters
detailed_formatter = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(funcName)-30s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_formatter = logging.Formatter(
    '%(levelname)s: %(message)s'
)

file_handler.setFormatter(detailed_formatter)
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


class TranscriptionDebugger:
    """Debug helper for transcription pipeline"""

    def __init__(self, progress_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize debugger.

        Args:
            progress_callback: Optional callback for progress updates (for GUI)
        """
        self.progress_callback = progress_callback
        self.start_time = None
        self.step_times = {}
        self.current_step = None
        self.process = psutil.Process(os.getpid())

    def log(self, message: str, level: str = "info"):
        """
        Log message with level.

        Args:
            message: Message to log
            level: Log level (debug, info, warning, error, critical)
        """
        log_func = getattr(logger, level.lower())
        log_func(message)

        # Send to GUI if callback provided
        if self.progress_callback:
            self.progress_callback(message)

    def start(self, pipeline_name: str = "Transcription"):
        """Start pipeline timing"""
        self.start_time = time.time()
        self.step_times = {}
        self.log(f"{'='*60}", "info")
        self.log(f"🚀 STARTING {pipeline_name.upper()} PIPELINE", "info")
        self.log(f"{'='*60}", "info")
        self.log(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "info")
        self._log_system_info()

    def step(self, step_name: str, details: str = ""):
        """Start a new step and log previous step duration"""
        current_time = time.time()

        # Log previous step duration if exists
        if self.current_step:
            duration = current_time - self.step_times[self.current_step]
            self.log(f"✅ {self.current_step}: {duration:.2f}s", "info")

        # Start new step
        self.current_step = step_name
        self.step_times[step_name] = current_time

        mem_mb = self.process.memory_info().rss / 1024 / 1024
        self.log(f"", "info")  # Empty line
        self.log(f"📍 STEP: {step_name}", "info")
        if details:
            self.log(f"   {details}", "info")
        self.log(f"   Memory: {mem_mb:.1f} MB", "debug")

    def complete(self):
        """Complete pipeline and log total duration"""
        if self.start_time:
            total_duration = time.time() - self.start_time

            # Log final step
            if self.current_step:
                step_duration = time.time() - self.step_times[self.current_step]
                self.log(f"✅ {self.current_step}: {step_duration:.2f}s", "info")

            self.log(f"", "info")
            self.log(f"{'='*60}", "info")
            self.log(f"✅ PIPELINE COMPLETE", "info")
            self.log(f"{'='*60}", "info")
            self.log(f"⏱️  Total Duration: {total_duration:.2f}s ({total_duration/60:.1f} min)", "info")
            self._log_step_summary()

    def error(self, error: Exception, step: str = ""):
        """Log error with full traceback"""
        step_info = f" in {step}" if step else ""
        self.log(f"", "error")
        self.log(f"{'='*60}", "error")
        self.log(f"❌ ERROR{step_info}", "error")
        self.log(f"{'='*60}", "error")
        self.log(f"Exception Type: {type(error).__name__}", "error")
        self.log(f"Exception Message: {str(error)}", "error")
        self.log(f"", "error")
        self.log(f"Full Traceback:", "error")
        self.log(f"{traceback.format_exc()}", "error")

        # Log system state at time of error
        self._log_system_info()

    def warning(self, message: str, details: str = ""):
        """Log warning"""
        self.log(f"⚠️  WARNING: {message}", "warning")
        if details:
            self.log(f"   {details}", "warning")

    def _log_system_info(self):
        """Log system information"""
        mem = self.process.memory_info()
        mem_mb = mem.rss / 1024 / 1024

        cpu_percent = self.process.cpu_percent(interval=0.1)

        self.log(f"📊 System Info:", "debug")
        self.log(f"   Memory: {mem_mb:.1f} MB", "debug")
        self.log(f"   CPU: {cpu_percent:.1f}%", "debug")
        self.log(f"   PID: {self.process.pid}", "debug")

    def _log_step_summary(self):
        """Log summary of all steps with durations"""
        if self.step_times:
            self.log(f"", "info")
            self.log(f"📊 Step Summary:", "info")
            for step, start_time in self.step_times.items():
                # Find next step or use current time
                step_list = list(self.step_times.keys())
                current_idx = step_list.index(step)
                if current_idx < len(step_list) - 1:
                    next_step = step_list[current_idx + 1]
                    duration = self.step_times[next_step] - start_time
                else:
                    duration = time.time() - start_time

                percentage = (duration / (time.time() - self.start_time)) * 100
                self.log(f"   {step}: {duration:.2f}s ({percentage:.1f}%)", "info")


def profile_function(debugger: Optional[TranscriptionDebugger] = None):
    """
    Decorator to profile function execution time.

    Usage:
        @profile_function(debugger)
        def my_function():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__

            if debugger:
                debugger.log(f"▶️  Entering {func_name}", "debug")

            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                if debugger:
                    debugger.log(f"✅ {func_name} completed in {duration:.2f}s", "debug")
                else:
                    logger.debug(f"{func_name} completed in {duration:.2f}s")

                return result

            except Exception as e:
                duration = time.time() - start_time

                if debugger:
                    debugger.log(f"❌ {func_name} failed after {duration:.2f}s", "error")
                    debugger.error(e, func_name)
                else:
                    logger.error(f"{func_name} failed after {duration:.2f}s: {e}", exc_info=True)

                raise

        return wrapper
    return decorator


# Convenience functions for quick logging
def log_debug(message: str):
    """Quick debug log"""
    logger.debug(message)

def log_info(message: str):
    """Quick info log"""
    logger.info(message)

def log_warning(message: str):
    """Quick warning log"""
    logger.warning(message)

def log_error(message: str, exc_info: bool = False):
    """Quick error log"""
    logger.error(message, exc_info=exc_info)


if __name__ == "__main__":
    # Demo usage
    print("Transcription Debugger - Demo\n")

    debugger = TranscriptionDebugger()
    debugger.start("Demo Pipeline")

    debugger.step("Loading Model", "Model: whisper-small")
    time.sleep(1)  # Simulate model loading

    debugger.step("Transcribing Audio", "File: test.m4a")
    time.sleep(2)  # Simulate transcription

    debugger.step("Processing Results", "Applying markers")
    time.sleep(0.5)

    debugger.complete()

    print(f"\nLog file created: {log_file}")
