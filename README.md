# Kalaallisut-Danish Sentence Aligner

[![Test](https://github.com/VoiceLessQ/kalaallisut-aligner/actions/workflows/test.yml/badge.svg)](https://github.com/VoiceLessQ/kalaallisut-aligner/actions/workflows/test.yml)

Complete NLP toolkit for Kalaallisut language processing and Danish-Kalaallisut parallel corpus alignment.

## 🎯 Features

### ✅ Core Components
- **Morphological Analyzer** - Full Kalaallisut morphology using lang-kal/GiellaLT
- **Sentence Aligner** - hunalign-based alignment with cognate-boosted scoring (34.7% high-confidence)
- **Glosser** - Morpheme-by-morpheme analysis with 16,819 dictionary entries
- **Cognate Extractor** - 1,526 Danish-Kalaallisut shared terms

### 📊 Dataset
- **8,178 aligned sentence pairs** (train) + 1,362 test pairs
- Extracted from parallel Danish-Kalaallisut government documents and news corpus
- Smart date-aware sentence splitting
- Avg word ratio: 1.55 (Danish/Kalaallisut)
- Avg char ratio: 0.80 (Danish/Kalaallisut)

## 🚀 Quick Start

### Prerequisites
```bash
# Install dependencies
sudo apt install build-essential git make hunalign
pip3 install -r requirements.txt

# Install lang-kal (morphological analyzer)
cd ~
git clone https://github.com/giellalt/lang-kal.git
cd lang-kal
./autogen.sh
./configure --disable-syntax --enable-tokenisers --enable-analysers
make

# Optional: Set custom paths (if installed elsewhere)
export LANG_KAL_PATH=/path/to/lang-kal
export HUNALIGN_PATH=/path/to/hunalign/hunalign
```

### Installation
```bash
cd ~
git clone [your-repo-url] kalaallisut-aligner
cd kalaallisut-aligner
chmod +x scripts/*.sh
```

## 📖 Usage

### Quick Start: Run the Example

Try the complete example script first to see the aligner in action:

```bash
python3 examples/align_example.py
```

This demonstrates:
- Initializing the aligner
- Aligning Danish-Kalaallisut text
- Filtering by confidence scores
- Saving results to file

### 1. Align New Document Pairs

The aligner can align Danish and Kalaallisut documents using two methods:

#### Method A: Production Aligner (hunalign - Recommended)
```bash
# Align two parallel documents (one sentence per line)
./scripts/align_production.sh danish.txt kalaallisut.txt > output.txt

# High-quality alignments only (confidence > 0.5)
./scripts/align_production.sh danish.txt kalaallisut.txt | awk -F'\t' '$3 > 0.5'
```

**Output format:** `danish_sentence <TAB> kalaallisut_sentence <TAB> confidence_score`

#### Method B: Statistical Aligner (Python - For pre-split text)
```bash
# For documents that are already split into parallel paragraphs/sections
python3 -c "
from src.aligner import SentenceAligner
import sys

# Read input files
with open('danish.txt', 'r') as f:
    danish_text = f.read()
with open('kalaallisut.txt', 'r') as f:
    kal_text = f.read()

# Initialize aligner with training statistics
aligner = SentenceAligner('data/processed/alignment_stats.json')

# Align documents
alignments = aligner.align_documents(danish_text, kal_text)

# Save results
aligner.save_alignments(alignments, 'output.txt')

# Print statistics
high_conf = sum(1 for a in alignments if a['confidence'] > 0.5)
print(f'Total alignments: {len(alignments)}', file=sys.stderr)
print(f'High confidence (>0.5): {high_conf} ({100*high_conf/len(alignments):.1f}%)', file=sys.stderr)
"
```

**Output format:** `danish_sentence @ kalaallisut_sentence`

**When to use each method:**
- **hunalign (Method A)**: Best for large documents with no prior alignment, handles unbalanced documents
- **Python aligner (Method B)**: Best for pre-aligned paragraphs, faster for small documents, customizable weights

### 2. Gloss Kalaallisut Text
```bash
# Interactive mode
cd glosser
python3 glosser_v2_fixed.py

# From file
python3 glosser_v2_fixed.py input.txt -o output.txt

# HTML output
python3 glosser_v2_fixed.py input.txt -f html -o output.html
```

### 3. Test Morphology
```bash
python3 test_morphology.py
# Enter Kalaallisut words interactively
```

### 4. Extract Cognates
```bash
python3 scripts/extract_cognates.py
# Creates: data/processed/cognates.json
```

### 5. Add New Training Data

If you have additional parallel corpus data to improve the aligner:

```bash
# Step 1: Place your parallel corpus file in data/test/
# Format: DA: <danish>\nKL: <kalaallisut>\nCONF: <score>\n\n
# Example: data/test/parallel_corpus_clean.txt

# Step 2: Parse and append to training data
python3 scripts/append_parallel_corpus.py
# - Parses DA/KL/CONF format
# - Filters by confidence threshold (>= 0.5)
# - Appends to data/processed/train.txt
# - Creates backup at train.txt.backup

# Step 3: Recalculate alignment statistics
python3 scripts/calculate_stats_fast.py
# - Updates data/processed/alignment_stats.json
# - Creates backup at alignment_stats.json.backup
# - Shows before/after comparison
```

**What this does:**
- Expands the training dataset with new parallel sentences
- Recalculates word/character ratios for better alignment accuracy
- Backups are created automatically for safety

## 📚 Documentation

### API Documentation

Full API documentation is available via Sphinx:

```bash
# Install documentation dependencies
pip3 install sphinx sphinx-rtd-theme

# Build HTML documentation
cd docs
make html

# View documentation
# Open docs/build/html/index.html in your browser
```

The API documentation includes:
- **Morphology Module** - HFST tokenization and analysis functions
- **Aligner Module** - Sentence alignment algorithms
- **Preprocessor Module** - Text preprocessing and sentence splitting
- **Utils Module** - Helper functions for loading/saving pairs
- **Glosser Module** - Morpheme-by-morpheme glossing
- **Config Module** - Centralized configuration management

### Project Documentation
- **[CODE_RECOMMENDATIONS.md](CODE_RECOMMENDATIONS.md)** - Comprehensive code improvement guide
  - Critical fixes (error handling, security)
  - Best practices (type hints, logging, testing)
  - Performance optimizations
  - Implementation roadmap

- **[CLEANUP_REPO.md](CLEANUP_REPO.md)** - Repository cleanup guide
  - What files should/shouldn't be tracked
  - How to clean up large data files
  - .gitignore best practices
  - Repository maintenance

- **[BROWSER_EXTENSION_FEASIBILITY.md](BROWSER_EXTENSION_FEASIBILITY.md)** - Browser extension analysis
  - Feasibility assessment for creating a browser extension
  - Four architectural approaches evaluated
  - Implementation plan and cost estimates

- **[ANALYSIS.md](ANALYSIS.md)** - Consolidated project analysis
  - Architecture overview, dependencies, and data assets
  - Reference analysis and license compatibility
  - Roadmap and areas for improvement

## 📁 Project Structure

```
kalaallisut-aligner/
├── data/
│   ├── raw/              # Original data
│   ├── processed/        # Cognates, dictionaries, stats
│   ├── aligned/          # Alignment outputs
│   └── test/             # Test data
├── src/
│   ├── morphology.py     # HFST morphological analysis (centralized)
│   ├── preprocessor.py   # Text preprocessing & sentence processing
│   ├── aligner.py        # Sentence alignment algorithm
│   ├── config.py         # Configuration management
│   └── utils.py          # Helper functions (load/save pairs)
├── glosser/
│   ├── glosser_v2_fixed.py           # Main glosser
│   ├── morpheme_glosses.json         # Tag translations
│   └── kalaallisut_english_dict.json # 16,819 entries
├── examples/
│   ├── align_example.py          # Complete alignment example
│   └── tts_alignment_demo.py     # TTS alignment demo
├── scripts/
│   ├── align_production.sh       # Production aligner (hunalign)
│   ├── extract_cognates.py       # Cognate extraction
│   ├── extract_da_kal_dict.py    # Dictionary extraction
│   ├── test_morphology.py        # Interactive morphology tester
│   ├── append_parallel_corpus.py # Add new training data
│   ├── calculate_stats.py        # Recalculate alignment statistics
│   └── calculate_stats_fast.py   # Fast statistics calculation
├── tests/
│   ├── test_aligner.py        # Aligner unit tests
│   ├── test_preprocessor.py   # Preprocessor unit tests
│   └── test_utils.py          # Utilities unit tests
└── docs/
    └── GUIDE.md          # Detailed usage guide
```

## 🔧 Key Files

### Dictionaries
- `data/processed/cognates.json` - 1,526 Danish-Kalaallisut cognates
- `data/processed/hunalign_dict_full.txt` - hunalign format dictionary
- `glosser/kalaallisut_english_dict.json` - Kalaallisut→English (16,819 entries)

### Models & Stats
- `data/processed/alignment_stats.json` - Training corpus statistics (updated: 8,178 pairs)
- `data/processed/train.txt` - 8,178 aligned training pairs
- `data/processed/test.txt` - 1,362 test pairs
- `data/DATA_VERSIONS.md` - Data version tracking and provenance

## 📈 Performance

### Alignment Quality (100 sentence test)
- **Average confidence:** 0.481
- **High confidence (>0.5):** 34.7%
- **Very high (>1.0):** 13.9%
- **Low confidence (<0.2):** 31.7%

### Glosser Coverage
- **16,819 dictionary entries** from Oqaasileriffik
- **Morphological analysis** using lang-kal FST
- **HTML/text/JSON output** formats

## 🛠️ Advanced Usage

### Complete Alignment Example

Here's a complete workflow for aligning a new Danish-Kalaallisut document pair:

```bash
# 1. Create your input files (one sentence per line, or raw text)
cat > danish.txt << 'EOF'
Grønlands parlament mødes i dag.
Regeringen præsenterer det nye budget.
EOF

cat > kalaallisut.txt << 'EOF'
Kalaallit Nunaanni inatsisartut ullumi ataatsimiinnissavaat.
Naalakkersuisut kingorna aningaasanik nalunaaruteqarnermi saqqummiunneqartartunik saqqummiunneqarput.
EOF

# 2. Align using hunalign (recommended for production)
./scripts/align_production.sh danish.txt kalaallisut.txt > aligned.txt

# View results
cat aligned.txt
# Output:
# Grønlands parlament mødes i dag.	Kalaallit Nunaanni inatsisartut ullumi ataatsimiinnissavaat.	0.82
# Regeringen præsenterer det nye budget.	Naalakkersuisut kingorna aningaasanik...	0.65

# 3. Filter by confidence
awk -F'\t' '$3 > 0.7' aligned.txt > high_confidence.txt
```

### Extract Word Dictionary from Aligned Pairs
```python
python3 scripts/extract_da_kal_dict.py
# Extracts Danish↔Kalaallisut word pairs from aligned sentences
```

### Run Alignment with Custom Parameters
```bash
~/hunalign/src/hunalign/hunalign \
    -text \
    -realign \
    -thresh=50 \
    data/processed/hunalign_dict_full.txt \
    danish.txt \
    kalaallisut.txt
```

### Batch Processing
```bash
# Process multiple file pairs
for da_file in data/raw/*.da.txt; do
    kal_file="${da_file/.da.txt/.kl.txt}"
    output="${da_file/.da.txt/.aligned.txt}"
    ./scripts/align_production.sh "$da_file" "$kal_file" > "$output"
done
```

### Using the Python Aligner Programmatically

For integration into Python scripts:

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')
from aligner import SentenceAligner

# Initialize aligner
aligner = SentenceAligner('data/processed/alignment_stats.json')

# Your Danish and Kalaallisut texts
danish_text = """
Grønlands parlament mødes i dag.
Regeringen præsenterer det nye budget.
"""

kalaallisut_text = """
Kalaallit Nunaanni inatsisartut ullumi ataatsimiinnissavaat.
Naalakkersuisut kingorna aningaasanik nalunaaruteqarnermi saqqummiunneqartartunik saqqummiunneqarput.
"""

# Align
alignments = aligner.align_documents(danish_text, kalaallisut_text)

# Process results
for i, align in enumerate(alignments, 1):
    print(f"Pair {i} (confidence: {align['confidence']:.2f})")
    print(f"  DA: {align['danish']}")
    print(f"  KL: {align['kalaallisut']}")
    print()

# Save to file
aligner.save_alignments(alignments, 'output.txt')

# Filter high-confidence alignments
high_conf = [a for a in alignments if a['confidence'] > 0.5]
print(f"High-confidence alignments: {len(high_conf)}/{len(alignments)}")
```

**Key Parameters:**
- `stats_file`: Path to alignment statistics (default: `data/processed/alignment_stats.json`)
- `cognates_file`: Path to cognate dictionary (default: `data/processed/cognates.json`) -- optional, boosts alignment accuracy via lexical overlap
- Alignment weights can be customized in `src/config.py`
- Returns list of dictionaries with keys: `danish`, `kalaallisut`, `confidence`, `da_index`, `kal_index`

## 📚 References

### Software & Tools

- **lang-kal:** Kalaallisut morphological analyzer
  https://github.com/giellalt/lang-kal
  License: GPL-3.0

- **hunalign:** Bilingual sentence alignment tool
  https://github.com/danielvarga/hunalign
  Varga, D., Halácsy, P., Kornai, A., Nagy, V., Németh, L., & Trón, V. (2005). "Parallel corpora for medium density languages." *RANLP 2005*.
  License: LGPL-3.0

- **GiellaLT:** Infrastructure for indigenous language technology
  https://giellalt.github.io/
  Moshagen, S. N., Pirinen, T. A., & Trosterud, T. (2022). "Building an open-source development infrastructure for language technology projects." *LREC 2022*.
  License: Dual CC-BY-SA / GPL

### Data Sources

- **Oqaasileriffik:** Greenland Language Secretariat
  https://oqaasileriffik.gl/ | https://github.com/Oqaasileriffik/dicts
  2018 Chicago Greenlandic-English Dictionary
  License: CC-BY-SA 4.0

### Academic Citations

If you use this toolkit in research, please cite:

```bibtex
@misc{kalaallisut-aligner-2025,
  author = {VoiceLessQ},
  title = {Kalaallisut-Danish Sentence Aligner},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/VoiceLessQ/kalaallisut-aligner}
}
```

And cite the underlying tools as appropriate.

## 💎 Code Quality

This project follows modern Python best practices:

- **✅ Type Hints**: Full type annotations across all modules (List, Dict, Optional, etc.)
- **✅ Comprehensive Testing**: 45 unit tests with pytest, CI/CD via GitHub Actions
- **✅ Error Handling**: Robust error handling with proper exceptions and validation
- **✅ Structured Logging**: Logging framework for debugging and monitoring
- **✅ Code Formatting**: Black formatter with consistent style
- **✅ Modular Design**: Centralized morphology module, no code duplication
- **✅ Security**: Input validation, command injection prevention
- **✅ Performance Optimized**: Efficient string operations, dictionary caching, O(n) algorithms
- **✅ Centralized Configuration**: Config file support with environment variable overrides

See [CODE_RECOMMENDATIONS.md](CODE_RECOMMENDATIONS.md) for detailed code quality documentation.

## 🤝 Contributing

Contributions welcome! Please see [CODE_RECOMMENDATIONS.md](CODE_RECOMMENDATIONS.md) for detailed improvement suggestions.

### Priority Areas (Updated November 2025)
- **✅ Completed**: Type hints, error handling, security fixes, input validation, unit tests, code deduplication, configuration module, performance optimizations
- **🔄 In Progress**: Logging implementation (on feature branch)
- **Future Features**: Neural alignment models, improved glossing accuracy, web interface, Sphinx documentation

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Follow the code quality guidelines in CODE_RECOMMENDATIONS.md
4. Add tests for new functionality (use pytest)
5. Run `black` formatter before committing
6. Submit a pull request

See [CODE_RECOMMENDATIONS.md](CODE_RECOMMENDATIONS.md) for detailed implementation guidelines and best practices.

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Data Sources
- **Kalaallisut-English Dictionary**: Oqaasileriffik (Greenland Language Secretariat)
- **Morphological Analyzer**: GiellaLT/lang-kal (GPL v3/LGPL)
- **Alignment Tool**: hunalign by Daniel Varga
- **Parallel Corpus**: Danish-Kalaallisut government documents (public domain)

The MIT License applies to the code and processed data in this repository. Users should comply with the licenses of underlying tools (particularly lang-kal's GPL/LGPL license when using morphological analysis features).

## 🙏 Acknowledgments

- **Oqaasileriffik** (Greenland Language Secretariat) for the Kalaallisut-English dictionary
- **GiellaLT/Divvun/Giellatekno** for the lang-kal morphological analyzer infrastructure
- **Daniel Varga et al.** for hunalign sentence alignment tool
- **University of Chicago** for the 2018 Greenlandic-English dictionary collaboration

## 🔧 Advanced Configuration

### Configuration File

The project uses a centralized configuration system. Create a `config.json` file in the project root to customize settings:

```bash
# Copy the example configuration
cp config.json.example config.json

# Edit to customize paths and parameters
nano config.json
```

**Example `config.json`:**
```json
{
  "lang_kal_path": "~/lang-kal",
  "hunalign_path": "~/hunalign/src/hunalign/hunalign",
  "alignment": {
    "word_score_weight": 0.3,
    "char_score_weight": 0.2,
    "position_score_weight": 0.2,
    "lexical_score_weight": 0.3,
    "min_sentence_length": 5
  },
  "cognates": {
    "min_word_length": 3,
    "max_edit_distance": 2
  }
}
```

**Configuration Options:**
- **`lang_kal_path`**: Path to lang-kal installation
- **`hunalign_path`**: Path to hunalign binary
- **`alignment.word_score_weight`**: Weight for word count similarity (default: 0.3)
- **`alignment.char_score_weight`**: Weight for character count similarity (default: 0.2)
- **`alignment.position_score_weight`**: Weight for sentence position similarity (default: 0.2)
- **`alignment.lexical_score_weight`**: Weight for cognate/loanword lexical overlap (default: 0.3)
- **`alignment.min_sentence_length`**: Minimum characters for sentence splitting (default: 5)
- **`cognates.min_word_length`**: Minimum word length for cognate extraction (default: 3)
- **`cognates.max_edit_distance`**: Maximum edit distance for cognate matching (default: 2)

### Environment Variables

Environment variables override `config.json` settings:

- `LANG_KAL_PATH`: Path to lang-kal installation (default: `~/lang-kal`)
- `HUNALIGN_PATH`: Path to hunalign binary (default: `~/hunalign/src/hunalign/hunalign`)

**Priority:** Environment Variables > config.json > Default Values

### Data Version Tracking

See `data/DATA_VERSIONS.md` for:
- Dictionary versions and update procedures
- Data provenance and licensing
- Corpus statistics and version history

---

**Built:** November 2025
**Version:** 1.2
**Last Updated:** February 2026
**Status:** Production ready
**Maintainer:** VoiceLessQ

**Recent Updates (v1.2):**
- Integrated cognate dictionary into alignment scoring (lexical overlap feature)
- Rebalanced scoring weights: word=0.3, char=0.2, position=0.2, lexical=0.3
- 45 unit tests (up from 41)

**Previous (v1.1):**
- Expanded training dataset from 5,438 to 8,178 pairs (+50%)
- Updated alignment statistics (word ratio: 1.55, char ratio: 0.80)
- Added scripts for appending new parallel corpus data
