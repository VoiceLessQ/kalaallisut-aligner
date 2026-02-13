# Changelog

## [1.2] - 2026-02-13

### Added
- **Lexical/Cognate Scoring** in the Python sentence aligner
  - `SentenceAligner` now loads `data/processed/cognates.json` at init
  - New `_lexical_score()` method detects shared loanwords, proper nouns, and known cognate pairs between sentence pairs
  - Cognate file is optional -- aligner degrades gracefully when absent
- **New Tests**
  - `TestLexicalScoring` class with 4 tests (exact match boost, cognate dict lookup, missing file fallback, empty sentence handling)
  - Total unit tests: 41 → 45

### Changed
- **Scoring Weights Rebalanced**
  - Word ratio: 0.4 → 0.3
  - Character ratio: 0.3 → 0.2
  - Position: 0.3 → 0.2
  - Lexical overlap (new): 0.3
- **`SentenceAligner.__init__`** accepts optional `cognates_file` parameter
- **`config.py`** adds `lexical_score_weight` setting
- Updated README with new configuration options and version info

### Removed
- `clean up.md` -- superseded by `CLEANUP_REPO.md`
- `MERGE_INSTRUCTIONS.md` -- one-time merge instructions, no longer needed
- `.gitignore.README.md` -- unnecessary
- `PROJECT_ANALYSIS.md` -- consolidated into `ANALYSIS.md`
- `REFERENCE_ANALYSIS.md` -- consolidated into `ANALYSIS.md`

## [1.1] - 2025-11-16

### Added
- **New Scripts**
  - `scripts/append_parallel_corpus.py` - Parse and append new parallel corpus data in DA/KL/CONF format
  - `scripts/calculate_stats.py` - Recalculate alignment statistics from training data
  - `scripts/calculate_stats_fast.py` - Fast version using simple tokenization (recommended)

- **Examples**
  - `examples/align_example.py` - Complete working example demonstrating aligner usage
  - Shows initialization, alignment, filtering by confidence, and saving results

- **Documentation**
  - Comprehensive usage guide for both hunalign and Python aligner methods
  - Complete alignment workflow examples with sample input/output
  - Programmatic Python API usage guide
  - Instructions for adding new training data
  - Quick start example script

### Changed
- **Dataset Expansion**
  - Training pairs: 5,438 → 8,178 (+2,740 pairs, +50% increase)
  - Source: Added news corpus from `parallel_corpus_clean.txt`
  - Filtered by confidence threshold ≥ 0.5

- **Updated Statistics**
  - Word ratio (DA/KL): 1.364 → 1.553 (+0.189)
  - Char ratio (DA/KL): 0.730 → 0.796 (+0.065)
  - Statistics file: `data/processed/alignment_stats.json`

- **Documentation**
  - Updated README.md to version 1.1
  - Added alignment usage examples and workflows
  - Updated dataset statistics throughout documentation
  - Enhanced project structure documentation

### Improved
- **Backup System**
  - Automatic backups created for:
    - `data/processed/train.txt.backup`
    - `data/processed/alignment_stats.json.backup`

- **Performance**
  - Fast statistics calculation script for large datasets
  - Simple tokenization fallback for speed (calculate_stats_fast.py)

## [1.0] - 2025-11-01

### Initial Release
- Sentence alignment using hunalign
- Statistical Python aligner
- Morphological analyzer integration
- Glosser with 16,819 dictionary entries
- Cognate extraction (1,526 pairs)
- 6,812 aligned sentence pairs
- Comprehensive test suite
- Full type hints and error handling
