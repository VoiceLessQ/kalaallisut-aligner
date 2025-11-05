# Kalaallisut-Danish Sentence Aligner

Complete NLP toolkit for Kalaallisut language processing and Danish-Kalaallisut parallel corpus alignment.

## 🎯 Features

### ✅ Core Components
- **Morphological Analyzer** - Full Kalaallisut morphology using lang-kal/GiellaLT
- **Sentence Aligner** - hunalign-based alignment with cognate dictionary (34.7% high-confidence)
- **Glosser** - Morpheme-by-morpheme analysis with 16,819 dictionary entries
- **Cognate Extractor** - 1,526 Danish-Kalaallisut shared terms

### 📊 Dataset
- **6,798 aligned sentence pairs** (5,438 train / 1,360 test)
- Extracted from parallel Danish-Kalaallisut government documents
- Smart date-aware sentence splitting
- Avg word ratio: 1.48 (Danish/Kalaallisut)

## 🚀 Quick Start

### Prerequisites
```bash
# Install dependencies
sudo apt install build-essential git make hunalign
pip3 install --break-system-packages pandas odfpy

# Install lang-kal (morphological analyzer)
cd ~
git clone https://github.com/giellalt/lang-kal.git
cd lang-kal
./autogen.sh
./configure --disable-syntax --enable-tokenisers --enable-analysers
make
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

## 📁 Project Structure

```
kalaallisut-aligner/
├── data/
│   ├── raw/              # Original data
│   ├── processed/        # Cognates, dictionaries, stats
│   ├── aligned/          # Alignment outputs
│   └── test/             # Test data
├── src/
│   ├── preprocessor.py   # Tokenization & morphology
│   ├── aligner.py        # Sentence alignment (backup)
│   ├── utils.py          # Helper functions
│   └── feature_extractor.py
├── glosser/
│   ├── glosser_v2_fixed.py           # Main glosser
│   ├── morpheme_glosses.json         # Tag translations
│   └── kalaallisut_english_dict.json # 16,819 entries
├── scripts/
│   ├── align_production.sh    # Production aligner
│   ├── extract_cognates.py    # Cognate extraction
│   └── extract_da_kal_dict.py # Dictionary extraction
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
- `data/raw/existing_alignments.txt` - 6,798 training pairs

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

- **lang-kal:** https://github.com/giellalt/lang-kal
- **hunalign:** https://github.com/danielvarga/hunalign
- **Oqaasileriffik:** Dictionary source
- **GiellaLT:** Giella infrastructure for indigenous languages

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional cognate extraction
- Neural alignment models
- Improved glossing accuracy
- Web interface

## 📄 License

[Your license here]

## 🙏 Acknowledgments

- Oqaasileriffik for Kalaallisut dictionary
- GiellaLT for lang-kal infrastructure
- Daniel Varga for hunalign

---

**Built:** November 2025  
**Status:** Production-ready  
**Maintainer:** [Your name]
