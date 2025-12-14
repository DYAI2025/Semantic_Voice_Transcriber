# SVT Plugin Architecture

**Last Updated:** 2025-12-13 | **Version:** 1.0.0 | **Status:** Production-Ready

This document defines the modular plugin architecture for Semantic Voice Transcriber (SVT), enabling developers to extend functionality without modifying core code.

---

## Table of Contents

1. [Architecture Principles](#architecture-principles)
2. [Plugin Lifecycle](#plugin-lifecycle)
3. [Plugin Slots](#plugin-slots)
4. [Plugin Development Guide](#plugin-development-guide)
5. [Built-in Plugins](#built-in-plugins)
6. [Plugin API Reference](#plugin-api-reference)
7. [Example Plugins](#example-plugins)
8. [Testing Plugins](#testing-plugins)

---

## Architecture Principles

### Design Goals

1. **Modularity**: Plugins are self-contained with explicit dependencies
2. **Hot-Reload**: Plugins can be loaded/unloaded without restarting SVT
3. **Isolation**: Plugin failures don't crash the main pipeline
4. **Composability**: Multiple plugins can operate on the same slot
5. **Configuration**: Each plugin has its own config schema
6. **Discoverability**: Automatic plugin discovery from directories

### Plugin Types

| Type | Description | Examples |
|------|-------------|----------|
| **Annotation** | Add semantic markers to transcripts | ATO markers, emotion tags |
| **Enhancement** | Enrich data with additional features | Speaker profiling, context extraction |
| **Visualization** | Generate visual outputs | Dashboards, charts, timelines |
| **Export** | Convert to external formats | ELAN, Praat TextGrid, subtitles |
| **Integration** | Connect to external services | Cloud storage, CRM systems |
| **Analysis** | Perform advanced analysis | Sentiment trends, topic modeling |

---

## Plugin Lifecycle

```
┌─────────────┐
│  Discovery  │  Scan plugin directories
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Validation  │  Check metadata, dependencies
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Registration │  Register hooks and config schema
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Initialization│ Load config, initialize resources
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Execution  │  Invoke on pipeline events
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Cleanup   │  Release resources, save state
└─────────────┘
```

### 1. Discovery

**Plugin Directories (priority order):**
1. `plugins/` - Built-in plugins (shipped with SVT)
2. `~/.svt/plugins/` - User-installed plugins
3. `$SVT_PLUGIN_PATH` - Environment variable paths (colon-separated)

**Discovery Process:**
```python
def discover_plugins() -> List[Path]:
    plugin_paths = []
    search_dirs = [
        Path("plugins"),
        Path.home() / ".svt" / "plugins",
        *get_env_plugin_paths()
    ]

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue

        for item in search_dir.iterdir():
            if item.is_dir() and (item / "metadata.json").exists():
                plugin_paths.append(item)

    return plugin_paths
```

### 2. Validation

**Required Files:**
- `metadata.json` - Plugin metadata (required)
- `plugin.py` - Main plugin class (required)
- `config.yaml` - Default configuration (optional)
- `requirements.txt` - Python dependencies (optional)
- `README.md` - Documentation (recommended)

**metadata.json Schema:**
```json
{
  "id": "unique_plugin_id",
  "name": "Human Readable Name",
  "version": "1.0.0",
  "author": "Author Name <email@example.com>",
  "description": "Brief description",
  "license": "MIT",
  "svt_version_min": "2.0.0",
  "svt_version_max": "3.0.0",
  "slots": ["annotation", "post_transcription"],
  "requires_llm": false,
  "requires_internet": false,
  "config_schema": {
    "param_name": {
      "type": "float",
      "default": 0.6,
      "min": 0.0,
      "max": 1.0,
      "description": "Parameter description"
    }
  },
  "dependencies": {
    "python": ["numpy>=1.20.0", "scikit-learn>=1.0.0"],
    "system": ["ffmpeg"],
    "svt_plugins": ["base_marker_plugin"]
  }
}
```

**Validation Checks:**
1. ✅ Metadata JSON is valid
2. ✅ Plugin ID is unique (no conflicts)
3. ✅ SVT version compatibility
4. ✅ All dependencies are met
5. ✅ Plugin class implements required methods
6. ✅ Config schema is valid

### 3. Registration

```python
class PluginRegistry:
    def __init__(self):
        self.plugins: Dict[str, PluginInfo] = {}
        self.slot_hooks: Dict[str, List[str]] = defaultdict(list)

    def register(self, plugin_path: Path) -> bool:
        """Register a plugin and its hooks."""
        metadata = self.load_metadata(plugin_path)
        plugin_id = metadata["id"]

        # Validate
        if plugin_id in self.plugins:
            raise PluginError(f"Plugin {plugin_id} already registered")

        # Load plugin class
        plugin_instance = self.load_plugin_class(plugin_path)

        # Register hooks
        for slot in metadata["slots"]:
            self.slot_hooks[slot].append(plugin_id)

        # Store plugin info
        self.plugins[plugin_id] = PluginInfo(
            id=plugin_id,
            metadata=metadata,
            instance=plugin_instance,
            path=plugin_path,
            enabled=True
        )

        logger.info(f"Registered plugin: {plugin_id}")
        return True
```

### 4. Initialization

```python
def initialize_plugin(plugin_id: str, config: Dict[str, Any]) -> None:
    """Initialize a plugin with configuration."""
    plugin = registry.plugins[plugin_id]

    # Validate config against schema
    validated_config = validate_config(config, plugin.metadata["config_schema"])

    # Initialize plugin instance
    try:
        plugin.instance.initialize(validated_config)
        plugin.initialized = True
        logger.info(f"Initialized plugin: {plugin_id}")
    except Exception as e:
        logger.error(f"Failed to initialize {plugin_id}: {e}")
        plugin.enabled = False
        raise PluginInitializationError(plugin_id, e)
```

### 5. Execution

```python
def execute_slot(slot: str, data: Dict[str, Any], job_id: str) -> Dict[str, Any]:
    """Execute all plugins registered for a slot."""
    plugin_ids = registry.slot_hooks.get(slot, [])

    for plugin_id in plugin_ids:
        plugin = registry.plugins[plugin_id]

        if not plugin.enabled or not plugin.initialized:
            continue

        try:
            # Execute plugin
            start_time = time.time()
            data = plugin.instance.execute(slot, data)
            duration = time.time() - start_time

            # Emit event
            emit_plugin_event(job_id, plugin_id, slot, {
                "duration_ms": duration * 1000,
                "status": "success"
            })

        except Exception as e:
            logger.error(f"Plugin {plugin_id} failed at slot {slot}: {e}")

            # Decide error handling strategy
            if plugin.metadata.get("critical", False):
                raise PluginExecutionError(plugin_id, slot, e)
            else:
                # Continue with other plugins
                emit_plugin_event(job_id, plugin_id, slot, {
                    "status": "failed",
                    "error": str(e)
                })

    return data
```

### 6. Cleanup

```python
def cleanup_plugin(plugin_id: str) -> None:
    """Cleanup plugin resources."""
    plugin = registry.plugins[plugin_id]

    try:
        plugin.instance.cleanup()
        logger.info(f"Cleaned up plugin: {plugin_id}")
    except Exception as e:
        logger.warning(f"Cleanup failed for {plugin_id}: {e}")

def cleanup_all() -> None:
    """Cleanup all plugins (on shutdown)."""
    for plugin_id in registry.plugins:
        cleanup_plugin(plugin_id)
```

---

## Plugin Slots

### Slot Execution Order

```
Audio File
    │
    ▼
[pre_transcription]     ← Slot 1: Modify config, preprocess audio
    │
    ▼
Whisper Transcription
    │
    ▼
[post_transcription]    ← Slot 2: Clean/enrich transcription
    │
    ▼
Prosody Extraction
    │
    ▼
[post_prosody]          ← Slot 3: Annotate prosody features
    │
    ▼
Speaker Diarization
    │
    ▼
[post_diarization]      ← Slot 4: Enrich speaker segments
    │
    ▼
[annotation]            ← Slot 5: Add semantic markers
    │
    ▼
Output Formatting
    │
    ▼
[post_processing]       ← Slot 6: Generate additional outputs
    │
    ▼
[visualization]         ← Slot 7: Create dashboards/charts
    │
    ▼
Final Results
```

### Slot Specifications

#### 1. **pre_transcription**

**Purpose**: Modify audio or config before transcription

**Input Data:**
```python
{
    "audio_path": Path,
    "config": TranscriptionConfig,
    "job_id": str
}
```

**Output Data:**
```python
{
    "audio_path": Path,  # Can be modified (e.g., preprocessed file)
    "config": TranscriptionConfig,  # Can be modified
    "job_id": str
}
```

**Use Cases:**
- Audio preprocessing (noise reduction, normalization)
- Dynamic config adjustment based on audio analysis
- Audio format conversion

---

#### 2. **post_transcription**

**Purpose**: Enrich or clean transcription results

**Input Data:**
```python
{
    "text": str,
    "segments": List[Segment],
    "language": str,
    "confidence_scores": ConfidenceScores,
    "job_id": str
}
```

**Output Data:**
```python
{
    "text": str,  # Can be modified
    "segments": List[Segment],  # Can be enriched
    "language": str,
    "confidence_scores": ConfidenceScores,
    "metadata": Dict[str, Any],  # Plugin-added metadata
    "job_id": str
}
```

**Use Cases:**
- Grammar correction
- Named entity recognition
- Speaker context loading
- Confidence boosting with language models

---

#### 3. **post_prosody**

**Purpose**: Annotate or analyze prosody features

**Input Data:**
```python
{
    "segments": List[Segment],
    "prosody_features": List[ProsodyFeature],
    "prosody_baseline": ProsodyBaseline,
    "job_id": str
}
```

**Output Data:**
```python
{
    "segments": List[Segment],
    "prosody_features": List[ProsodyFeature],  # Can add annotations
    "prosody_baseline": ProsodyBaseline,
    "prosody_markers": List[str],  # New markers added
    "job_id": str
}
```

**Use Cases:**
- Emotion detection from prosody
- Turn-taking analysis
- Stress pattern detection
- Prosody-based ATO marker correlation

---

#### 4. **post_diarization**

**Purpose**: Enrich speaker segments with additional data

**Input Data:**
```python
{
    "segments": List[Segment],
    "speakers": List[str],
    "speaker_embeddings": Dict[str, np.ndarray],
    "job_id": str
}
```

**Output Data:**
```python
{
    "segments": List[Segment],  # Can modify speaker labels
    "speakers": List[str],
    "speaker_profiles": Dict[str, SpeakerProfile],  # Plugin-added profiles
    "speaker_embeddings": Dict[str, np.ndarray],
    "job_id": str
}
```

**Use Cases:**
- Speaker identification from embeddings
- Speaker profile loading from memory
- Speaker characteristic annotation
- Overlapped speech analysis

---

#### 5. **annotation**

**Purpose**: Add semantic markers to transcript

**Input Data:**
```python
{
    "segments": List[Segment],
    "text": str,
    "prosody_features": List[ProsodyFeature],
    "job_id": str
}
```

**Output Data:**
```python
{
    "segments": List[Segment],  # Enriched with markers
    "markers": List[Marker],  # All detected markers
    "marker_summary": MarkerSummary,
    "job_id": str
}
```

**Use Cases:**
- ATO marker detection
- Turning point detection
- Therapeutic pattern recognition
- Sentiment markers

---

#### 6. **post_processing**

**Purpose**: Generate additional outputs or perform final analysis

**Input Data:**
```python
{
    "transcription_result": Dict[str, Any],  # Full result
    "output_files": Dict[str, Path],  # Already generated files
    "job_id": str
}
```

**Output Data:**
```python
{
    "transcription_result": Dict[str, Any],
    "output_files": Dict[str, Path],  # Can add new files
    "additional_data": Dict[str, Any],  # Plugin-specific data
    "job_id": str
}
```

**Use Cases:**
- Export to external formats (ELAN, Praat, SRT)
- Upload to cloud storage
- Send notifications
- Generate summaries

---

#### 7. **visualization**

**Purpose**: Create visual representations of data

**Input Data:**
```python
{
    "transcription_result": Dict[str, Any],
    "output_files": Dict[str, Path],
    "job_id": str
}
```

**Output Data:**
```python
{
    "transcription_result": Dict[str, Any],
    "output_files": Dict[str, Path],  # Add visualization files
    "visualizations": List[Visualization],
    "job_id": str
}
```

**Use Cases:**
- Psychoanalysis dashboards
- Prosody timelines
- Speaker interaction graphs
- Emotion trajectory charts

---

## Plugin Development Guide

### Step 1: Create Plugin Structure

```bash
mkdir -p ~/.svt/plugins/my_plugin
cd ~/.svt/plugins/my_plugin
touch metadata.json plugin.py config.yaml requirements.txt README.md
```

### Step 2: Define Metadata

**metadata.json:**
```json
{
  "id": "my_plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "author": "Your Name <you@example.com>",
  "description": "Does something useful",
  "license": "MIT",
  "svt_version_min": "2.0.0",
  "slots": ["annotation"],
  "requires_llm": false,
  "config_schema": {
    "threshold": {
      "type": "float",
      "default": 0.5,
      "min": 0.0,
      "max": 1.0,
      "description": "Detection threshold"
    },
    "enable_advanced": {
      "type": "bool",
      "default": false,
      "description": "Enable advanced mode"
    }
  },
  "dependencies": {
    "python": ["numpy>=1.20.0"]
  }
}
```

### Step 3: Implement Plugin Class

**plugin.py:**
```python
from typing import Dict, Any
from pathlib import Path
import logging
from svt_core.plugin_base import SVTPlugin, PluginMetadata

logger = logging.getLogger(__name__)


class MyPlugin(SVTPlugin):
    """My custom SVT plugin."""

    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        # Load from metadata.json
        metadata_path = Path(__file__).parent / "metadata.json"
        with open(metadata_path) as f:
            data = json.load(f)
        return PluginMetadata(**data)

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        self.threshold = config.get("threshold", 0.5)
        self.enable_advanced = config.get("enable_advanced", False)

        logger.info(f"MyPlugin initialized with threshold={self.threshold}")

        # Load resources, models, etc.
        if self.enable_advanced:
            self._load_advanced_model()

    def execute(self, slot: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plugin for a specific slot."""
        if slot == "annotation":
            return self._annotate(data)
        return data

    def _annotate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add annotations to segments."""
        segments = data["segments"]

        for segment in segments:
            text = segment.get("text", "")

            # Perform annotation logic
            if self._should_annotate(text):
                # Add marker to segment
                if "markers" not in segment:
                    segment["markers"] = []
                segment["markers"].append({
                    "type": "MY_MARKER",
                    "confidence": 0.9,
                    "source": "my_plugin"
                })

        return data

    def _should_annotate(self, text: str) -> bool:
        """Determine if text should be annotated."""
        # Your detection logic here
        return "keyword" in text.lower()

    def _load_advanced_model(self):
        """Load advanced model (example)."""
        # Load ML model, external resources, etc.
        pass

    def cleanup(self) -> None:
        """Release resources."""
        logger.info("MyPlugin cleanup")
        # Close files, connections, release memory, etc.
```

### Step 4: Add Default Config

**config.yaml:**
```yaml
threshold: 0.6
enable_advanced: false
```

### Step 5: Specify Dependencies

**requirements.txt:**
```
numpy>=1.20.0
scikit-learn>=1.0.0
```

### Step 6: Write Documentation

**README.md:**
```markdown
# My Plugin

## Description
This plugin does X, Y, and Z.

## Installation
```bash
pip install -r requirements.txt
```

## Configuration
- `threshold` (float): Detection threshold (default: 0.5)
- `enable_advanced` (bool): Enable advanced mode (default: false)

## Usage
Enable in SVT settings or via API:
```json
{
  "plugins": ["my_plugin"]
}
```

## License
MIT
```

### Step 7: Test Plugin

```bash
# From SVT root directory
python -m pytest tests/test_plugin_my_plugin.py
```

**tests/test_plugin_my_plugin.py:**
```python
import pytest
from pathlib import Path
from app.services.plugin_manager import PluginManager

def test_my_plugin_loads():
    """Test that plugin loads successfully."""
    manager = PluginManager()
    assert "my_plugin" in manager.plugins

def test_my_plugin_executes():
    """Test plugin execution."""
    manager = PluginManager()
    plugin = manager.plugins["my_plugin"]

    data = {
        "segments": [
            {"text": "This contains keyword"}
        ]
    }

    result = plugin.execute("annotation", data)

    assert "markers" in result["segments"][0]
    assert result["segments"][0]["markers"][0]["type"] == "MY_MARKER"
```

---

## Built-in Plugins

### 1. ATO Markers Plugin

**ID**: `ato_markers`
**Slots**: `annotation`, `post_transcription`
**Description**: Detects ATO semantic markers in transcripts

**Configuration:**
```yaml
confidence_threshold: 0.6
max_markers_per_segment: 5
use_curated: true  # Use curated 40-marker set
marker_directories:
  - VP_ATO/
  - ATO_*.yaml
```

---

### 2. Psychoanalysis Dashboard Plugin

**ID**: `psychoanalysis_dashboard`
**Slots**: `visualization`, `post_processing`
**Description**: Generates interactive psychoanalysis dashboards with VAD, UED, turnpoints

**Configuration:**
```yaml
llm_provider: ollama
turnpoint_threshold: 0.5
dashboard_output_dir: Transkripte_LLM/
auto_open_browser: true
```

---

### 3. Prosody Correlation Plugin

**ID**: `prosody_correlation`
**Slots**: `post_prosody`, `annotation`
**Description**: Correlates prosody features with ATO markers using trained models

**Configuration:**
```yaml
correlation_threshold: 0.5
enable_training: false
model_path: models/prosody_correlation.pkl
```

---

### 4. ELAN Export Plugin

**ID**: `elan_export`
**Slots**: `post_processing`
**Description**: Exports transcripts to ELAN .eaf format

**Configuration:**
```yaml
include_prosody_tier: true
include_marker_tier: true
time_format: milliseconds
```

---

### 5. Speaker Memory Plugin

**ID**: `speaker_memory`
**Slots**: `post_diarization`, `post_processing`
**Description**: Loads and updates speaker profiles from Memory/

**Configuration:**
```yaml
memory_dir: Memory/
auto_create_profiles: true
update_prosody_patterns: true
```

---

## Plugin API Reference

### Base Class: `SVTPlugin`

```python
class SVTPlugin(ABC):
    """Abstract base class for all SVT plugins."""

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize plugin with configuration.

        Args:
            config: Plugin configuration (validated against schema)

        Raises:
            PluginInitializationError: If initialization fails
        """
        pass

    @abstractmethod
    def execute(self, slot: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute plugin for a specific slot.

        Args:
            slot: Slot name (e.g., "annotation")
            data: Input data for the slot

        Returns:
            Modified data (must include all original keys)

        Raises:
            PluginExecutionError: If execution fails
        """
        pass

    def cleanup(self) -> None:
        """
        Release resources (optional).

        Called when plugin is unloaded or on shutdown.
        """
        pass

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration (optional override).

        Args:
            config: Configuration to validate

        Returns:
            True if valid

        Raises:
            ConfigValidationError: If config is invalid
        """
        # Default: use metadata config_schema
        return True

    def on_enable(self) -> None:
        """Called when plugin is enabled (optional)."""
        pass

    def on_disable(self) -> None:
        """Called when plugin is disabled (optional)."""
        pass
```

### Data Classes

**PluginMetadata:**
```python
@dataclass
class PluginMetadata:
    id: str
    name: str
    version: str
    author: str
    description: str
    license: str
    svt_version_min: str
    svt_version_max: Optional[str] = None
    slots: List[str] = field(default_factory=list)
    requires_llm: bool = False
    requires_internet: bool = False
    config_schema: Dict[str, ConfigParam] = field(default_factory=dict)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    critical: bool = False  # If True, pipeline fails if plugin fails
```

**Segment:**
```python
@dataclass
class Segment:
    id: int
    start: float
    end: float
    text: str
    speaker: Optional[str] = None
    confidence: float = 1.0
    prosody: Optional[ProsodyFeature] = None
    markers: List[Marker] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**Marker:**
```python
@dataclass
class Marker:
    type: str  # e.g., "ATO_AFFIRMATION"
    confidence: float
    source: str  # Plugin ID that created marker
    position: Optional[Tuple[int, int]] = None  # Character range in text
    metadata: Dict[str, Any] = field(default_factory=dict)
```

---

## Example Plugins

### Example 1: Keyword Highlighter

**Purpose**: Highlight specific keywords in transcripts

```python
class KeywordHighlighterPlugin(SVTPlugin):
    @property
    def metadata(self):
        return PluginMetadata(
            id="keyword_highlighter",
            name="Keyword Highlighter",
            version="1.0.0",
            author="SVT Team",
            description="Highlights specified keywords",
            slots=["annotation"],
            config_schema={
                "keywords": {
                    "type": "list",
                    "default": [],
                    "description": "Keywords to highlight"
                }
            }
        )

    def initialize(self, config):
        self.keywords = config.get("keywords", [])

    def execute(self, slot, data):
        if slot == "annotation":
            segments = data["segments"]

            for segment in segments:
                text = segment.get("text", "").lower()

                for keyword in self.keywords:
                    if keyword.lower() in text:
                        segment["markers"].append(Marker(
                            type="KEYWORD",
                            confidence=1.0,
                            source=self.metadata.id,
                            metadata={"keyword": keyword}
                        ))

        return data
```

---

### Example 2: Cloud Storage Export

**Purpose**: Upload results to S3/MinIO

```python
import boto3
from botocore.exceptions import BotoCoreError

class CloudStoragePlugin(SVTPlugin):
    @property
    def metadata(self):
        return PluginMetadata(
            id="cloud_storage",
            name="Cloud Storage Export",
            version="1.0.0",
            slots=["post_processing"],
            requires_internet=True,
            config_schema={
                "bucket": {"type": "str", "required": True},
                "region": {"type": "str", "default": "us-east-1"},
                "prefix": {"type": "str", "default": "transcripts/"}
            }
        )

    def initialize(self, config):
        self.s3_client = boto3.client(
            "s3",
            region_name=config["region"]
        )
        self.bucket = config["bucket"]
        self.prefix = config.get("prefix", "")

    def execute(self, slot, data):
        if slot == "post_processing":
            output_files = data["output_files"]
            job_id = data["job_id"]

            for file_type, file_path in output_files.items():
                s3_key = f"{self.prefix}{job_id}/{file_path.name}"

                try:
                    self.s3_client.upload_file(
                        str(file_path),
                        self.bucket,
                        s3_key
                    )
                    logger.info(f"Uploaded {file_path.name} to s3://{self.bucket}/{s3_key}")

                except BotoCoreError as e:
                    logger.error(f"S3 upload failed: {e}")

        return data

    def cleanup(self):
        # Close S3 connections if needed
        pass
```

---

## Testing Plugins

### Unit Tests

```python
import pytest
from app.services.plugin_manager import PluginManager
from app.plugins.my_plugin.plugin import MyPlugin

@pytest.fixture
def plugin():
    """Create plugin instance."""
    p = MyPlugin()
    p.initialize({"threshold": 0.6})
    return p

def test_plugin_metadata(plugin):
    """Test metadata is correct."""
    assert plugin.metadata.id == "my_plugin"
    assert "annotation" in plugin.metadata.slots

def test_plugin_execution(plugin):
    """Test plugin executes correctly."""
    data = {
        "segments": [
            {"text": "This has keyword"},
            {"text": "This does not"}
        ]
    }

    result = plugin.execute("annotation", data)

    assert len(result["segments"][0]["markers"]) == 1
    assert len(result["segments"][1].get("markers", [])) == 0
```

### Integration Tests

```python
def test_plugin_in_pipeline():
    """Test plugin works in full pipeline."""
    from app.services.transcription_service import TranscriptionService

    service = TranscriptionService()
    config = {
        "plugins": ["my_plugin"]
    }

    result = service.transcribe("test_audio.m4a", config)

    # Verify plugin modified result
    assert any(
        marker["source"] == "my_plugin"
        for segment in result["segments"]
        for marker in segment.get("markers", [])
    )
```

---

## Best Practices

1. **Error Handling**: Always wrap plugin logic in try/except, log errors clearly
2. **Configuration Validation**: Validate config thoroughly, provide sensible defaults
3. **Performance**: Avoid blocking operations, use async if possible
4. **Resource Management**: Release resources in `cleanup()`, avoid memory leaks
5. **Logging**: Use structured logging with plugin ID prefix
6. **Testing**: Write unit tests for all plugin logic
7. **Documentation**: Provide clear README with examples
8. **Versioning**: Use semantic versioning, specify SVT compatibility
9. **Dependencies**: Minimize dependencies, specify exact versions
10. **Backwards Compatibility**: Maintain config schema compatibility across versions

---

**Status**: ✅ **Production-Ready Architecture**
**Extensibility**: High (unlimited plugin possibilities)
**Developer Experience**: Excellent (simple API, auto-discovery, hot-reload)
