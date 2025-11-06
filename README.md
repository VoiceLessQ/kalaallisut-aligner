# Kalaallisut-Danish Sentence Aligner

[![Test](https://github.com/VoiceLessQ/kalaallisut-aligner/actions/workflows/test.yml/badge.svg)](https://github.com/VoiceLessQ/kalaallisut-aligner/actions/workflows/test.yml)

Complete NLP toolkit for Kalaallisut language processing and Danish-Kalaallisut parallel corpus alignment.

## 🎯 Features

### ✅ Core Components
- **Morphological Analyzer** - Full Kalaallisut morphology using lang-kal/GiellaLT
- **Sentence Aligner** - hunalign-based alignment with cognate dictionary (34.7% high-confidence)
- **Glosser** - Morpheme-by-morpheme analysis with 16,819 dictionary entries
- **Cognate Extractor** - 1,526 Danish-Kalaallisut shared terms

### 📊 Dataset
- **6,812 aligned sentence pairs** (5,450 train / 1,362 test)
- Extracted from parallel Danish-Kalaallisut government documents
- Smart date-aware sentence splitting
- Avg word ratio: 1.36 (Danish/Kalaallisut)

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

### 1. Align Documents
```bash
# Align two parallel documents (one sentence per line)
./scripts/align_production.sh danish.txt kalaallisut.txt > output.txt

# High-quality alignments only (confidence > 0.5)
./scripts/align_production.sh danish.txt kalaallisut.txt | awk -F'\t' '$3 > 0.5'
```

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

## 📚 Documentation

### Project Documentation
- **[CODE_RECOMMENDATIONS.md](CODE_RECOMMENDATIONS.md)** - Comprehensive code improvement guide
  - Critical fixes (error handling, security)
  - Best practices (type hints, logging, testing)
  - Performance optimizations
  - Implementation roadmap

- **[BROWSER_EXTENSION_FEASIBILITY.md](BROWSER_EXTENSION_FEASIBILITY.md)** - Browser extension analysis
  - Feasibility assessment for creating a browser extension
  - Four architectural approaches evaluated
  - Implementation plan and cost estimates
  - Technical specifications and use cases

- **[REFERENCE_ANALYSIS.md](REFERENCE_ANALYSIS.md)** - Academic reference analysis
  - Detailed analysis of all cited tools and papers
  - License compatibility review
  - Data source documentation

- **[ANALYSIS.md](ANALYSIS.md)** - Project analysis and overview
  - Comprehensive project assessment
  - Feature breakdown and capabilities
  - Development recommendations

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
│   ├── aligner.py        # Sentence alignment (backup)
│   └── utils.py          # Helper functions (load/save pairs)
├── glosser/
│   ├── glosser_v2_fixed.py           # Main glosser
│   ├── morpheme_glosses.json         # Tag translations
│   └── kalaallisut_english_dict.json # 16,819 entries
├── scripts/
│   ├── align_production.sh    # Production aligner
│   ├── extract_cognates.py    # Cognate extraction
│   ├── extract_da_kal_dict.py # Dictionary extraction
│   └── test_morphology.py     # Interactive morphology tester
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
- `data/processed/alignment_stats.json` - Training corpus statistics
- `data/aligned/corpus_6798_pairs.txt` - 6,812 aligned training pairs
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
- **✅ Comprehensive Testing**: 41 unit tests with pytest, CI/CD via GitHub Actions
- **✅ Error Handling**: Robust error handling with proper exceptions and validation
- **✅ Structured Logging**: Logging framework for debugging and monitoring
- **✅ Code Formatting**: Black formatter with consistent style
- **✅ Modular Design**: Centralized morphology module, no code duplication
- **✅ Security**: Input validation, command injection prevention

See [CODE_RECOMMENDATIONS.md](CODE_RECOMMENDATIONS.md) for detailed code quality documentation.

## 🤝 Contributing

Contributions welcome! Please see [CODE_RECOMMENDATIONS.md](CODE_RECOMMENDATIONS.md) for detailed improvement suggestions.

### Priority Areas (Updated November 2025)
- **✅ Completed**: Type hints, error handling, security fixes, input validation, unit tests, code deduplication
- **🔄 In Progress**: Logging implementation, configuration module
- **Features**: Additional cognate extraction, neural alignment models, improved glossing accuracy, web interface

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

### Environment Variables

- `LANG_KAL_PATH`: Path to lang-kal installation (default: `~/lang-kal`)
- `HUNALIGN_PATH`: Path to hunalign binary (default: `~/hunalign/src/hunalign/hunalign`)

### Data Version Tracking

See `data/DATA_VERSIONS.md` for:
- Dictionary versions and update procedures
- Data provenance and licensing
- Corpus statistics and version history

---

**Built:** November 2025
**Version:** 1.0
**Status:** Production ready
**Maintainer:** VoiceLessQ
