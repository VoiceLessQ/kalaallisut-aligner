# Changelog

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
