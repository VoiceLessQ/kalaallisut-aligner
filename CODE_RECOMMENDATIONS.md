# Code Improvement Recommendations

## 📋 Status Update (November 2025)

**COMPLETED** ✅:
- **Phase 1 (Critical Fixes)** - All Priority 1 🔴 items implemented
- **Phase 3 (Testing)** - Test suite with 41 passing tests
- **CI/CD Pipeline** - GitHub Actions with passing badge

**IN PROGRESS** 🔄:
- Phase 2 (Structure & Quality) - Type hints ✅ COMPLETED, logging (on branch), configuration, code deduplication
- Phase 4 (Polish) - Sphinx docs, performance optimizations

See [Implementation Status](#implementation-status) for details.

---

## Executive Summary

This document provides actionable recommendations to improve code quality, maintainability, and robustness of the Kalaallisut-Danish Sentence Aligner project.

**Priority Levels**:
- 🔴 **CRITICAL**: Security or data integrity issues
- 🟠 **HIGH**: Significant quality/maintainability improvements
- 🟡 **MEDIUM**: Nice-to-have improvements
- 🟢 **LOW**: Optional enhancements

---

## 1. Error Handling & Robustness 🔴 CRITICAL ✅ COMPLETED

### Issue 1.1: Missing File Validation
**Files affected**: `src/aligner.py`, `src/utils.py`, `glosser/glosser_v2_fixed.py`

**Problem**:
```python
# aligner.py:14
with open(stats_file, 'r') as f:
    self.stats = json.load(f)
# No error handling if file doesn't exist or is malformed
```

**Recommendation**:
```python
def __init__(self, stats_file="data/processed/alignment_stats.json"):
    """Initialize with training statistics."""
    try:
        with open(stats_file, 'r') as f:
            self.stats = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Statistics file not found: {stats_file}\n"
            f"Run data preparation scripts first."
        )
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {stats_file}: {e}")

    # Validate required fields
    required_fields = ['avg_word_ratio', 'avg_char_ratio']
    missing = [f for f in required_fields if f not in self.stats]
    if missing:
        raise ValueError(f"Missing required fields in stats: {missing}")
```

**Impact**: Prevents cryptic errors when files are missing or corrupted

---

### Issue 1.2: Unsafe Division Operations
**Files affected**: `src/aligner.py:81-86`

**Problem**:
```python
# aligner.py:81
if kal_words == 0 or kal_chars == 0:
    return 0.0

word_ratio = da_words / kal_words  # kal_words could be 0 after check
char_ratio = da_chars / kal_chars
```

The check prevents division by zero, but logic is unclear. Also no check for `da_words == 0`.

**Recommendation**:
```python
def calculate_similarity(self, danish_sent, kal_sent, da_pos, kal_pos):
    """Calculate similarity score between two sentences."""
    # Feature extraction
    da_words = len(danish_sent.split())
    da_chars = len(danish_sent)

    kal_tokens = tokenize_text(kal_sent)
    kal_words = len([t for t in kal_tokens if t.strip() and t not in '.,;:!?'])
    kal_chars = len(kal_sent)

    # Validate inputs
    if kal_words == 0 or kal_chars == 0 or da_words == 0 or da_chars == 0:
        return 0.0

    # Calculate ratios (safe now)
    word_ratio = da_words / kal_words
    char_ratio = da_chars / kal_chars

    # ... rest of function
```

---

### Issue 1.3: No Error Handling for External Commands
**Files affected**: `src/preprocessor.py:28-40`

**Problem**:
```python
try:
    result = subprocess.run(
        ["hfst-tokenize", str(TOKENIZER)],
        input=text,
        capture_output=True,
        text=True,
        check=True
    )
except FileNotFoundError:
    print(f"ERROR: hfst-tokenize not found. Install HFST tools.", file=sys.stderr)
    return []  # Silent failure
```

**Recommendation**:
```python
def tokenize_text(text):
    """Tokenize Kalaallisut text using lang-kal tokenizer.

    Args:
        text: Input text to tokenize

    Returns:
        List of tokens

    Raises:
        RuntimeError: If HFST tools are not available
    """
    if not TOKENIZER.exists():
        raise RuntimeError(
            f"Tokenizer not found at {TOKENIZER}\n"
            f"Install lang-kal or set LANG_KAL_PATH environment variable\n"
            f"See: https://github.com/giellalt/lang-kal"
        )

    try:
        result = subprocess.run(
            ["hfst-tokenize", str(TOKENIZER)],
            input=text,
            capture_output=True,
            text=True,
            check=True,
            timeout=30  # Add timeout
        )
    except FileNotFoundError:
        raise RuntimeError(
            "hfst-tokenize command not found. Install HFST tools.\n"
            "See: https://github.com/giellalt/lang-kal"
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Tokenization timed out for text: {text[:100]}...")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Tokenization failed: {e.stderr}")

    tokens = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
    return tokens
```

**Impact**: Better error messages and proper exception propagation

---

## 2. Code Organization & Structure 🟠 HIGH

### Issue 2.1: Missing Type Hints
**Files affected**: All Python files

**Problem**: No type hints, making it harder to understand function signatures and catch bugs

**Recommendation**:
```python
from typing import List, Dict, Optional, Tuple

def split_sentences(self, text: str) -> List[str]:
    """Split text into sentences with date-aware splitting.

    Args:
        text: Input text to split

    Returns:
        List of sentence strings
    """
    # ... implementation

def load_aligned_pairs(filepath: str) -> List[Dict[str, str]]:
    """Load existing aligned sentence pairs.

    Args:
        filepath: Path to aligned pairs file

    Returns:
        List of dictionaries with 'danish' and 'kalaallisut' keys
    """
    # ... implementation

def calculate_similarity(
    self,
    danish_sent: str,
    kal_sent: str,
    da_pos: float,
    kal_pos: float
) -> float:
    """Calculate similarity score between two sentences.

    Args:
        danish_sent: Danish sentence
        kal_sent: Kalaallisut sentence
        da_pos: Relative position of Danish sentence (0.0-1.0)
        kal_pos: Relative position of Kalaallisut sentence (0.0-1.0)

    Returns:
        Similarity score (0.0-1.0)
    """
    # ... implementation
```

**Impact**: Better IDE support, catches type errors, improves documentation

---

### Issue 2.2: Magic Numbers
**Files affected**: `src/aligner.py`, `scripts/extract_cognates.py`

**Problem**:
```python
# aligner.py:96-100
similarity = (
    0.4 * max(0, word_score) +
    0.3 * max(0, char_score) +
    0.3 * max(0, position_score)
)

# extract_cognates.py:21
if len(da_word) < 3 or len(kal_word) < 3:
    continue
```

**Recommendation**:
```python
# At top of file or in a config class
class AlignmentConfig:
    """Configuration for sentence alignment."""
    WORD_SCORE_WEIGHT = 0.4
    CHAR_SCORE_WEIGHT = 0.3
    POSITION_SCORE_WEIGHT = 0.3
    MIN_COGNATE_LENGTH = 3
    MIN_SENTENCE_LENGTH = 5
    MAX_EDIT_DISTANCE = 2

# Then use in code
similarity = (
    AlignmentConfig.WORD_SCORE_WEIGHT * max(0, word_score) +
    AlignmentConfig.CHAR_SCORE_WEIGHT * max(0, char_score) +
    AlignmentConfig.POSITION_SCORE_WEIGHT * max(0, position_score)
)
```

**Impact**: Easier to tune parameters, self-documenting code

---

### Issue 2.3: Hard-coded Paths
**Files affected**: `src/preprocessor.py`, `glosser/glosser_v2_fixed.py`

**Problem**:
```python
# preprocessor.py:14-16
LANG_KAL_ROOT = Path(os.environ.get('LANG_KAL_PATH', Path.home() / "lang-kal"))
TOKENIZER = LANG_KAL_ROOT / "tools/tokenisers/tokeniser-disamb-gt-desc.pmhfst"
ANALYZER = LANG_KAL_ROOT / "src/fst/analyser-gt-desc.hfst"
```

Better, but still some hard-coding.

**Recommendation**: Create a central configuration module

```python
# src/config.py
"""Central configuration for the project."""
import os
import json
from pathlib import Path
from typing import Dict, Any

class Config:
    """Project configuration singleton."""

    _instance = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Load configuration from file or environment."""
        config_file = Path(__file__).parent.parent / "config.json"

        if config_file.exists():
            with open(config_file) as f:
                self._config = json.load(f)
        else:
            # Default configuration
            self._config = self._get_default_config()

        # Override with environment variables
        self._apply_env_overrides()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "lang_kal_path": str(Path.home() / "lang-kal"),
            "hunalign_path": str(Path.home() / "hunalign/src/hunalign/hunalign"),
            "data_paths": {
                "raw": "data/raw",
                "processed": "data/processed",
                "aligned": "data/aligned",
                "test": "data/test"
            },
            "alignment": {
                "confidence_threshold": 0.5,
                "word_score_weight": 0.4,
                "char_score_weight": 0.3,
                "position_score_weight": 0.3,
                "min_sentence_length": 5
            },
            "cognates": {
                "min_word_length": 3,
                "max_edit_distance": 2
            }
        }

    def _apply_env_overrides(self):
        """Override config with environment variables."""
        if "LANG_KAL_PATH" in os.environ:
            self._config["lang_kal_path"] = os.environ["LANG_KAL_PATH"]
        if "HUNALIGN_PATH" in os.environ:
            self._config["hunalign_path"] = os.environ["HUNALIGN_PATH"]

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    @property
    def lang_kal_root(self) -> Path:
        """Get lang-kal root directory."""
        return Path(self.get("lang_kal_path"))

    @property
    def tokenizer_path(self) -> Path:
        """Get tokenizer path."""
        return self.lang_kal_root / "tools/tokenisers/tokeniser-disamb-gt-desc.pmhfst"

    @property
    def analyzer_path(self) -> Path:
        """Get analyzer path."""
        return self.lang_kal_root / "src/fst/analyser-gt-desc.hfst"

# Global config instance
config = Config()
```

Then use in other files:
```python
from src.config import config

TOKENIZER = config.tokenizer_path
ANALYZER = config.analyzer_path
```

**Impact**: Central configuration, easier to modify, better for testing

---

### Issue 2.4: Duplicate Code
**Files affected**: `src/preprocessor.py`, `scripts/test_morphology.py`

**Problem**: `analyze_word()` function is duplicated

**Recommendation**: Consolidate into a single module

```python
# src/morphology.py
"""Kalaallisut morphological analysis utilities."""
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from src.config import config

def analyze_word(word: str) -> List[Dict[str, any]]:
    """Get morphological analysis of a word.

    Args:
        word: Kalaallisut word to analyze

    Returns:
        List of analysis dictionaries with keys:
        - surface: The analyzed word
        - analysis: Morphological analysis string
        - weight: Analysis weight (lower is better)

    Raises:
        RuntimeError: If HFST tools are not available
    """
    analyzer = config.analyzer_path

    if not analyzer.exists():
        raise RuntimeError(
            f"Analyzer not found at {analyzer}\n"
            f"Install lang-kal or set LANG_KAL_PATH environment variable"
        )

    try:
        result = subprocess.run(
            ["hfst-lookup", str(analyzer)],
            input=word,
            capture_output=True,
            text=True,
            check=False,  # Returns non-zero for unknown words
            timeout=10
        )
    except FileNotFoundError:
        raise RuntimeError(
            "hfst-lookup not found. Install HFST tools.\n"
            "See: https://github.com/giellalt/lang-kal"
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Analysis timed out for word: {word}")

    # Parse output
    analyses = []
    for line in result.stdout.strip().split('\n'):
        if line.startswith('>') or not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) >= 2:
            analyses.append({
                'surface': parts[0],
                'analysis': parts[1],
                'weight': float(parts[2]) if len(parts) > 2 else 0.0
            })

    return analyses
```

Then import everywhere:
```python
from src.morphology import analyze_word
```

**Impact**: Single source of truth, easier to maintain and test

---

## 3. Logging & Debugging 🟠 HIGH

### Issue 3.1: Print Statements Instead of Logging
**Files affected**: All Python files

**Problem**:
```python
print(f"Loaded {len(self.kal_eng)} dictionary entries", file=sys.stderr)
print("Splitting sentences...")
print(f"  Danish: {len(danish_sents)} sentences")
```

**Recommendation**:
```python
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Use logging
logger.info(f"Loaded {len(self.kal_eng)} dictionary entries")
logger.debug(f"Danish: {len(danish_sents)} sentences")
logger.error(f"ERROR: Analyzer not found at {ANALYZER}")
```

**Benefits**:
- Can control verbosity with log levels
- Can redirect to files
- Can filter by module
- Professional logging format
- No mixing with actual output

---

## 4. Testing 🟠 HIGH

### Issue 4.1: No Unit Tests
**Problem**: No automated tests

**Recommendation**: Add pytest-based tests

```python
# tests/test_aligner.py
import pytest
from src.aligner import SentenceAligner

class TestSentenceAligner:
    @pytest.fixture
    def aligner(self, tmp_path):
        """Create a test aligner with mock stats."""
        stats_file = tmp_path / "stats.json"
        stats_file.write_text('{"avg_word_ratio": 1.48, "avg_char_ratio": 0.75}')
        return SentenceAligner(str(stats_file))

    def test_split_sentences_basic(self, aligner):
        """Test basic sentence splitting."""
        text = "First sentence. Second sentence. Third sentence."
        sentences = aligner.split_sentences(text)
        assert len(sentences) == 3
        assert sentences[0] == "First sentence."

    def test_split_sentences_dates(self, aligner):
        """Test that dates are not split."""
        text = "Mødet blev holdt den 15. januar 2024. Det var godt."
        sentences = aligner.split_sentences(text)
        assert len(sentences) == 2
        assert "15. januar 2024" in sentences[0]

    def test_calculate_similarity_identical_position(self, aligner):
        """Test similarity calculation for aligned sentences."""
        score = aligner.calculate_similarity(
            "Dette er en test.",
            "Uanga tassaavoq.",
            0.5,  # Same position
            0.5
        )
        assert 0.0 <= score <= 1.0

    def test_calculate_similarity_empty_sentence(self, aligner):
        """Test handling of empty sentences."""
        score = aligner.calculate_similarity("Test", "", 0.5, 0.5)
        assert score == 0.0

# tests/test_utils.py
import pytest
from src.utils import load_aligned_pairs, split_train_test

class TestUtils:
    def test_load_aligned_pairs(self, tmp_path):
        """Test loading aligned pairs from file."""
        pairs_file = tmp_path / "pairs.txt"
        pairs_file.write_text(
            "Danish sentence 1 @ Kalaallisut sentence 1\n"
            "Danish sentence 2 @ Kalaallisut sentence 2\n"
        )

        pairs = load_aligned_pairs(str(pairs_file))
        assert len(pairs) == 2
        assert pairs[0]['danish'] == "Danish sentence 1"
        assert pairs[0]['kalaallisut'] == "Kalaallisut sentence 1"

    def test_split_train_test(self):
        """Test train/test splitting."""
        pairs = [{'danish': f'da{i}', 'kalaallisut': f'kal{i}'} for i in range(100)]
        train, test = split_train_test(pairs, test_ratio=0.2, seed=42)

        assert len(train) == 80
        assert len(test) == 20
        assert len(train) + len(test) == 100

        # Test reproducibility
        train2, test2 = split_train_test(pairs, test_ratio=0.2, seed=42)
        assert train == train2
        assert test == test2

# tests/conftest.py
"""Pytest configuration and shared fixtures."""
import pytest
from pathlib import Path

@pytest.fixture
def sample_kal_text():
    """Sample Kalaallisut text for testing."""
    return "Takussaanga. Inuit Kalaallit Nunaat."

@pytest.fixture
def sample_aligned_pairs():
    """Sample aligned pairs for testing."""
    return [
        {'danish': 'Hej verden', 'kalaallisut': 'Aluu silarsuaq'},
        {'danish': 'God dag', 'kalaallisut': 'Kutaa'}
    ]
```

Add to `requirements.txt`:
```
pytest>=7.0.0
pytest-cov>=4.0.0
```

Run tests:
```bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html
```

**Impact**: Catch bugs early, enable refactoring with confidence, document expected behavior

---

## 5. Documentation 🟡 MEDIUM

### Issue 5.1: Missing Docstrings
**Problem**: Many functions lack proper documentation

**Recommendation**: Add comprehensive docstrings

```python
def align_greedy(self, danish_sentences: List[str], kal_sentences: List[str]) -> List[Dict[str, any]]:
    """Align Danish and Kalaallisut sentences using greedy algorithm.

    This method iterates through Danish sentences and finds the best matching
    Kalaallisut sentence based on similarity score. Each Kalaallisut sentence
    can only be matched once.

    Args:
        danish_sentences: List of Danish sentences
        kal_sentences: List of Kalaallisut sentences

    Returns:
        List of alignment dictionaries with keys:
        - danish: Danish sentence text
        - kalaallisut: Kalaallisut sentence text
        - confidence: Similarity score (0.0-1.0)
        - da_index: Index of Danish sentence
        - kal_index: Index of Kalaallisut sentence

    Example:
        >>> aligner = SentenceAligner()
        >>> danish = ["Hello world.", "How are you?"]
        >>> kal = ["Aluu silarsuaq.", "Qanoq ippit?"]
        >>> alignments = aligner.align_greedy(danish, kal)
        >>> alignments[0]['confidence']
        0.85

    Notes:
        This is a greedy algorithm and may not find the globally optimal
        alignment. For better results, use hunalign via align_production.sh.
    """
    # ... implementation
```

**Impact**: Better understanding, easier onboarding, API documentation

---

### Issue 5.2: Missing API Documentation
**Recommendation**: Generate API docs with Sphinx

```bash
# Install Sphinx
pip install sphinx sphinx-rtd-theme

# Setup
cd docs
sphinx-quickstart

# Configure docs/conf.py
import os
import sys
sys.path.insert(0, os.path.abspath('../src'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # Google/NumPy docstring support
    'sphinx.ext.viewcode'
]

# Build docs
make html
```

**Impact**: Professional documentation, easier for contributors

---

## 6. Performance Optimization 🟡 MEDIUM

### Issue 6.1: Inefficient String Operations
**Files affected**: `src/aligner.py:32-64`

**Problem**:
```python
for i, char in enumerate(text):
    current += char  # String concatenation in loop - O(n²)
```

**Recommendation**:
```python
def split_sentences(self, text: str) -> List[str]:
    """Split text into sentences with date-aware splitting."""
    # Use list for O(1) append, join at end
    sentences = []
    current_chars = []

    for i, char in enumerate(text):
        current_chars.append(char)

        if char in '.!?':
            current = ''.join(current_chars)

            if len(current.strip()) < 5:
                continue

            # ... rest of logic

            sentences.append(current.strip())
            current_chars = []

    if current_chars:
        sentences.append(''.join(current_chars).strip())

    return sentences
```

**Impact**: Better performance for large documents

---

### Issue 6.2: Repeated External Calls
**Files affected**: `glosser/glosser_v2_fixed.py:57`

**Problem**: Calls `analyze_word()` for every token (subprocess overhead)

**Recommendation**: Batch processing

```python
def analyze_words_batch(words: List[str]) -> Dict[str, List[Dict]]:
    """Analyze multiple words in a single call.

    Args:
        words: List of words to analyze

    Returns:
        Dictionary mapping word -> list of analyses
    """
    analyzer = config.analyzer_path

    # Send all words at once
    input_text = '\n'.join(words)

    result = subprocess.run(
        ["hfst-lookup", str(analyzer)],
        input=input_text,
        capture_output=True,
        text=True,
        check=False,
        timeout=30
    )

    # Parse results
    analyses_by_word = {}
    current_word = None

    for line in result.stdout.strip().split('\n'):
        if line.startswith('>'):
            # New word
            current_word = line[1:].strip()
            analyses_by_word[current_word] = []
        elif current_word and line.strip():
            parts = line.split('\t')
            if len(parts) >= 2:
                analyses_by_word[current_word].append({
                    'surface': parts[0],
                    'analysis': parts[1],
                    'weight': float(parts[2]) if len(parts) > 2 else 0.0
                })

    return analyses_by_word
```

**Impact**: Significant performance improvement (10-100x faster)

---

### Issue 6.3: Caching Dictionary Lookups
**Files affected**: `glosser/glosser_v2_fixed.py`

**Recommendation**:
```python
from functools import lru_cache

class KalaallisutGlosser:
    # ... existing code

    @lru_cache(maxsize=1000)
    def translate_root_cached(self, root: str) -> Optional[str]:
        """Cached version of translate_root."""
        return self.translate_root(root)

    @lru_cache(maxsize=5000)
    def gloss_morpheme_cached(self, morpheme: str) -> str:
        """Cached version of gloss_morpheme."""
        return self.gloss_morpheme(morpheme)
```

**Impact**: Faster processing of repeated words

---

## 7. Security & Safety 🔴 CRITICAL

### Issue 7.1: Command Injection Risk
**Files affected**: Shell scripts

**Problem**:
```bash
# align_production.sh:16
"$HUNALIGN_PATH" -text -realign "$DICT" "$1" "$2"
```

If `$1` or `$2` contain shell metacharacters, could be exploited.

**Recommendation**:
```bash
#!/bin/bash
# Production aligner with input validation

set -euo pipefail  # Fail on errors, undefined vars, pipe failures

# Input validation
if [ $# -ne 2 ]; then
    echo "Usage: $0 <danish_file> <kalaallisut_file>" >&2
    exit 1
fi

DANISH_FILE="$1"
KAL_FILE="$2"

# Validate files exist and are readable
if [ ! -f "$DANISH_FILE" ]; then
    echo "ERROR: Danish file not found: $DANISH_FILE" >&2
    exit 1
fi

if [ ! -r "$DANISH_FILE" ]; then
    echo "ERROR: Danish file not readable: $DANISH_FILE" >&2
    exit 1
fi

if [ ! -f "$KAL_FILE" ]; then
    echo "ERROR: Kalaallisut file not found: $KAL_FILE" >&2
    exit 1
fi

if [ ! -r "$KAL_FILE" ]; then
    echo "ERROR: Kalaallisut file not readable: $KAL_FILE" >&2
    exit 1
fi

# Validate files are text files (not binaries)
if ! file "$DANISH_FILE" | grep -q text; then
    echo "ERROR: Danish file is not a text file" >&2
    exit 1
fi

if ! file "$KAL_FILE" | grep -q text; then
    echo "ERROR: Kalaallisut file is not a text file" >&2
    exit 1
fi

# Support environment variable with fallback
HUNALIGN_PATH="${HUNALIGN_PATH:-$HOME/hunalign/src/hunalign/hunalign}"

# Validate hunalign exists and is executable
if [ ! -f "$HUNALIGN_PATH" ]; then
    echo "ERROR: hunalign not found at $HUNALIGN_PATH" >&2
    echo "Install hunalign or set HUNALIGN_PATH environment variable" >&2
    echo "See: https://github.com/danielvarga/hunalign" >&2
    exit 1
fi

if [ ! -x "$HUNALIGN_PATH" ]; then
    echo "ERROR: hunalign not executable: $HUNALIGN_PATH" >&2
    exit 1
fi

# Validate dictionary exists
DICT="data/processed/hunalign_dict_full.txt"
if [ ! -f "$DICT" ]; then
    echo "ERROR: Dictionary not found: $DICT" >&2
    echo "Run data preparation scripts first" >&2
    exit 1
fi

# Run hunalign with validated inputs
"$HUNALIGN_PATH" -text -realign "$DICT" "$DANISH_FILE" "$KAL_FILE"
```

**Impact**: Prevents potential security issues

---

### Issue 7.2: Unsafe setup.sh
**Files affected**: `setup.sh:45`

**Problem**:
```bash
pip3 install --break-system-packages pandas odfpy
```

The `--break-system-packages` flag can cause system instability.

**Recommendation**:
```bash
echo "🐍 Step 2/7: Setting up Python environment..."

# Check if running in virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo "   Running in virtual environment: $VIRTUAL_ENV"
    pip3 install pandas odfpy
elif command -v pipx &> /dev/null; then
    echo "   Using pipx for isolated installation"
    pipx install pandas odfpy
else
    echo "   ⚠️  Not in virtual environment"
    echo "   Recommended: Create a virtual environment first"
    echo ""
    read -p "   Install to user directory? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip3 install --user pandas odfpy
    else
        echo "   Skipping Python package installation"
        echo "   Create virtual environment and run: pip install -r requirements.txt"
    fi
fi
```

**Impact**: Safer installation, follows best practices

---

## 8. Code Style & Conventions 🟡 MEDIUM

### Issue 8.1: Inconsistent Naming
**Problem**: Mix of styles

```python
# Some use snake_case
def load_aligned_pairs():

# Some use camelCase in variables
kal_eng = {}  # Good

# Class names good
class KalaallisutGlosser:  # Good
```

**Recommendation**: Follow PEP 8 strictly

- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

---

### Issue 8.2: No Code Formatting
**Recommendation**: Use `black` and `isort`

```bash
# Install
pip install black isort flake8

# Format
black src/ glosser/ scripts/
isort src/ glosser/ scripts/

# Check style
flake8 src/ glosser/ scripts/
```

Add to `pyproject.toml`:
```toml
[tool.black]
line-length = 100
target-version = ['py38']

[tool.isort]
profile = "black"
line_length = 100
```

**Impact**: Consistent code style, easier to read

---

## 9. CLI & Usability 🟡 MEDIUM

### Issue 9.1: Poor CLI Argument Handling
**Files affected**: `glosser/glosser_v2_fixed.py:99-105`

**Problem**: Minimal argument validation

**Recommendation**: Use `argparse` properly

```python
def main():
    parser = argparse.ArgumentParser(
        description="Gloss Kalaallisut text with morphological analysis",
        epilog="Example: python glosser_v2_fixed.py input.txt -o output.html -f html"
    )

    parser.add_argument(
        'input',
        nargs='?',
        type=argparse.FileType('r', encoding='utf-8'),
        default=sys.stdin,
        help='Input file (default: stdin)'
    )

    parser.add_argument(
        '-f', '--format',
        choices=['text', 'html', 'json'],
        default='text',
        help='Output format (default: text)'
    )

    parser.add_argument(
        '-o', '--output',
        type=argparse.FileType('w', encoding='utf-8'),
        default=sys.stdout,
        help='Output file (default: stdout)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0'
    )

    args = parser.parse_args()

    # Use args properly
    text = args.input.read()
    glosser = KalaallisutGlosser()
    glossed = glosser.gloss_text(text)

    if args.format == 'text':
        output = glosser.output_text(glossed)
    elif args.format == 'html':
        output = glosser.output_html(glossed)
    elif args.format == 'json':
        output = json.dumps(glossed, ensure_ascii=False, indent=2)

    args.output.write(output)
```

**Impact**: Better UX, proper error messages, help text

---

## 10. Data Validation 🟠 HIGH

### Issue 10.1: No Input Validation
**Files affected**: `src/aligner.py`, `glosser/glosser_v2_fixed.py`

**Recommendation**: Validate inputs

```python
def align_documents(self, danish_text: str, kal_text: str) -> List[Dict]:
    """Align two documents.

    Args:
        danish_text: Danish document text
        kal_text: Kalaallisut document text

    Returns:
        List of alignment dictionaries

    Raises:
        ValueError: If inputs are invalid
    """
    # Validate inputs
    if not danish_text or not danish_text.strip():
        raise ValueError("Danish text cannot be empty")

    if not kal_text or not kal_text.strip():
        raise ValueError("Kalaallisut text cannot be empty")

    if len(danish_text) > 1_000_000:
        logger.warning(f"Large document: {len(danish_text)} chars")

    # ... rest of implementation
```

---

## Implementation Status

### Phase 1: Critical Fixes 🔴 ✅ COMPLETED
1. ✅ Add error handling to file operations - **DONE**
2. ✅ Fix division by zero issues - **DONE**
3. ✅ Add input validation - **DONE**
4. ✅ Fix security issues in shell scripts - **DONE**

**Commits**: cf4e030, 5431c20, 8f05d03

### Phase 2: Structure & Quality 🟠 🔄 IN PROGRESS
1. ✅ Add type hints - **DONE** (All core modules: preprocessor, aligner, utils, glosser)
2. ⏳ Implement logging (on feature branch)
3. ⏳ Create configuration module
4. ⏳ Remove code duplication

### Phase 3: Testing 🟠 ✅ COMPLETED
1. ✅ Set up pytest - **DONE**
2. ✅ Write unit tests for core modules - **DONE** (41 tests)
3. ⏳ Add integration tests (marked for HFST tools)
4. ✅ Set up CI/CD - **DONE** (GitHub Actions)

**Test Results**: 41 passed, 3 deselected (integration)

### Phase 4: Polish 🟡 🔄 PARTIALLY COMPLETED
1. ✅ Add comprehensive docstrings - **DONE**
2. ⏳ Set up Sphinx documentation
3. ✅ Apply code formatting (black) - **DONE**
4. ⏳ Performance optimizations

---

## Automated Checks

Add pre-commit hooks (`.pre-commit-config.yaml`):
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=100', '--extend-ignore=E203,W503']

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/shellcheck-py/shellcheck-py
    rev: v0.9.0.2
    hooks:
      - id: shellcheck
```

Install:
```bash
pip install pre-commit
pre-commit install
```

---

## Metrics to Track

Progress on improvements:

| Metric | Before | Current | Target | Status |
|--------|--------|---------|--------|--------|
| Test Coverage | 0% | ~70% | >80% | 🟡 In Progress |
| Unit Tests | 0 | 41 passing | 50+ | ✅ Good |
| Type Coverage | 0% | 100% | 100% | ✅ Complete |
| Cyclomatic Complexity | Unknown | <10 | <10 per function | ✅ Good |
| Lines of Code | ~800 | ~1,900 | ~2,000 | ✅ On Track |
| Documentation Coverage | ~30% | ~70% | 100% | 🟡 In Progress |
| Security Issues | 3 | 0 | 0 | ✅ Fixed |
| CI/CD | ❌ None | ✅ Passing | ✅ Passing | ✅ Complete |

---

## Conclusion

### Achievements ✅

These improvements have significantly enhanced:
- ✅ **Reliability**: Comprehensive error handling and validation implemented
- ✅ **Security**: All potential vulnerabilities fixed
- ✅ **Testing**: 41 unit tests with CI/CD pipeline
- ✅ **Developer Experience**: Better docs, tests, tooling in place
- ✅ **Maintainability**: Type hints throughout codebase, cleaner code
- ⏳ **Performance**: Baseline established (optimizations pending)

### Completed Work

**Phase 1 (Critical)** - 100% Complete
- Error handling throughout
- Input validation and security fixes
- Division by zero fix
- Shell script hardening

**Phase 3 (Testing)** - 95% Complete
- 41 passing unit tests
- GitHub Actions CI/CD
- Integration test markers
- Test documentation

**Phase 4 (Polish)** - 50% Complete
- Comprehensive docstrings added
- Black formatting applied
- CI badge added

### Remaining Work

**Phase 2 (Structure & Quality)** - Highest ROI remaining:
1. ✅ ~~Type hints~~ - **COMPLETED**
2. Logging (easier debugging) - on feature branch
3. Configuration module (flexibility)
4. Remove code duplication

**Phase 4 (Polish)** - Nice to have:
1. Sphinx documentation
2. Performance optimizations
3. Pre-commit hooks

---

**Created**: November 2025
**Updated**: November 2025
**For**: Kalaallisut-Danish Sentence Aligner
**Status**: ✅ **Production Ready** (Critical issues resolved)
**Next Priority**: Phase 2 (Logging, configuration, code deduplication)
