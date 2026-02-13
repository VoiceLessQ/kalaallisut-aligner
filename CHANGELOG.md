# Changelog

## 1.2 -- 2026-02-13

- Added lexical/cognate scoring to the Python aligner. It now loads `cognates.json` and uses shared loanwords and proper nouns to improve matching. Falls back gracefully if the cognates file is missing.
- Rebalanced scoring weights: word ratio 0.3, char ratio 0.2, position 0.2, lexical overlap 0.3.
- 4 new tests for the lexical scoring (45 total).
- Removed stale docs: `clean up.md`, `MERGE_INSTRUCTIONS.md`, `.gitignore.README.md`, `PROJECT_ANALYSIS.md`, `REFERENCE_ANALYSIS.md`.

## 1.1 -- 2025-11-16

- Expanded training data from 5,438 to 8,178 pairs (+50%) by adding a news corpus, filtered at confidence >= 0.5.
- Updated alignment stats: word ratio 1.364 -> 1.553, char ratio 0.730 -> 0.796.
- New scripts: `append_parallel_corpus.py`, `calculate_stats.py`, `calculate_stats_fast.py`.
- Added `examples/align_example.py` showing basic aligner usage.
- Automatic backups when modifying train.txt or alignment_stats.json.

## 1.0 -- 2025-11-01

Initial release.

- hunalign-based sentence alignment + Python statistical aligner
- Morphological analyzer integration (lang-kal/GiellaLT)
- Glosser with 16,819 dictionary entries (Oqaasileriffik)
- Cognate extraction (1,526 pairs)
- 6,812 aligned sentence pairs
- Test suite, type hints, error handling
