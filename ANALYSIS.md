# Kalaallisut-Danish Aligner -- Project Analysis

**Last updated:** February 2026 | **Version:** 1.2

## Executive Summary

Production-ready NLP toolkit for Kalaallisut (West Greenlandic) language processing and Danish-Kalaallisut parallel corpus alignment. Combines FST-based morphological analysis, statistical sentence alignment, cognate-boosted scoring, and morpheme-level glossing.

### Key Metrics

| Metric | Value |
|--------|-------|
| Training pairs | 8,178 |
| Test pairs | 1,362 |
| Dictionary entries | 16,819 |
| Cognate pairs | 1,526 |
| Unit tests | 45 |
| Avg alignment confidence | 48.1% |
| High-confidence (>0.5) | 34.7% |

---

## Architecture

```
Raw Text ─► Sentence Splitting ─► Tokenization ─► Morphological Analysis
                                                          │
                                                          ▼
Danish text ──► Similarity Scoring (word ratio + char ratio + position + lexical overlap)
                          │
                          ▼
                   Greedy Matching ─► Confidence Filtering ─► Output
```

### Core Components

1. **Morphological Analyzer** (`src/morphology.py`)
   - HFST-based tokenization and analysis via lang-kal/GiellaLT
   - Timeout protection, fallback mechanisms

2. **Sentence Aligner** (`src/aligner.py`)
   - Greedy alignment with 4-feature similarity scoring
   - Weights: word ratio (0.3), char ratio (0.2), position (0.2), lexical/cognate overlap (0.3)
   - Date-aware sentence splitting for Danish/Kalaallisut month names
   - Cognate dictionary integration for loanword/proper noun matching

3. **Glosser** (`glosser/glosser_v2_fixed.py`)
   - 16,819-entry Kalaallisut-English dictionary (Oqaasileriffik)
   - Text, HTML, JSON output formats

4. **Cognate Extractor** (`scripts/extract_cognates.py`)
   - Edit distance-based cognate detection
   - 1,526 pairs used by hunalign and Python aligner

### Configuration

Centralized in `src/config.py` (singleton). Override hierarchy: environment variables > `config.json` > defaults.

---

## External Dependencies

| Dependency | License | Purpose | Integration |
|-----------|---------|---------|-------------|
| [lang-kal](https://github.com/giellalt/lang-kal) | GPL-3.0 | Morphological FST analyzer | `hfst-tokenize`, `hfst-lookup` |
| [hunalign](https://github.com/danielvarga/hunalign) | LGPL-3.0 | Production sentence alignment | `scripts/align_production.sh` |
| [GiellaLT](https://giellalt.github.io/) | CC-BY-SA / GPL | Language technology infrastructure | Build system for lang-kal |
| [Oqaasileriffik](https://oqaasileriffik.gl/) | CC-BY-SA 4.0 | Kalaallisut-English dictionary | `glosser/kalaallisut_english_dict.json` |

### Unused resources worth exploring

- **Martha TTS** (Oqaasileriffik) -- pronunciation generation
- **Nutserut** (https://nutserut.gl/) -- Greenlandic-Danish MT
- **hunalign `--realign`** -- two-pass alignment for quality improvement

---

## Data Assets

### Aligned Corpus
- `data/processed/train.txt` -- 8,178 pairs (format: `Danish @ Kalaallisut`)
- `data/processed/test.txt` -- 1,362 pairs
- Source: government documents + news corpus

### Dictionaries
- `data/processed/cognates.json` -- 1,526 entries (785 word cognates + 587 date/number cognates)
- `data/processed/hunalign_dict_full.txt` -- hunalign-format dictionary
- `glosser/kalaallisut_english_dict.json` -- 16,819 entries from Oqaasileriffik

### Statistics
- `data/processed/alignment_stats.json`
- Word ratio (DA/KL): 1.553 | Char ratio: 0.796

---

## Strengths

- Robust alignment pipeline with hunalign + Python fallback
- Cognate-boosted scoring for improved sentence matching
- Rich morphological processing via GiellaLT FST
- Full type annotations, 45 unit tests, CI/CD
- Centralized configuration with environment variable overrides
- Comprehensive documentation

## Areas for Improvement

- External tool calls (HFST) are a performance bottleneck
- CLI-only -- no web interface yet
- Limited to Danish-Kalaallisut pairs
- Could benefit from neural alignment models

---

## Roadmap

### Short-term
- Complete logging framework integration
- Experiment with hunalign `--realign` for quality gains
- Docker container for easier deployment

### Long-term
- Web interface (Flask/FastAPI)
- Neural alignment model (transformer-based)
- Additional language support (Tunumiisut, Inuktun)
- Export to standard formats (TMX, XLIFF, Moses)
- Martha TTS integration for pronunciation

---

## Licensing

| Component | License |
|-----------|---------|
| Project code | MIT |
| lang-kal | GPL-3.0 / LGPL |
| hunalign | LGPL-3.0 |
| Dictionary data | CC-BY-SA 4.0 |

Users must comply with GPL terms when using lang-kal morphological analysis features. Proper citation of Oqaasileriffik dictionaries required.

---

**Maintained by:** VoiceLessQ
