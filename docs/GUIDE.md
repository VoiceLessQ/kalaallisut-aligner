# Kalaallisut-Danish Aligner User Guide

## Table of Contents
1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Alignment Workflow](#alignment-workflow)
4. [Glossing Text](#glossing-text)
5. [Troubleshooting](#troubleshooting)

## Installation

See README.md for full installation instructions.

## Quick Start

### Align Two Documents
```bash
./scripts/align_production.sh input_danish.txt input_kal.txt > aligned.txt
```

### Gloss Kalaallisut Text
```bash
cd glosser
python3 glosser_v2_fixed.py input.txt -f html -o output.html
```

## Alignment Workflow

### 1. Prepare Input Files
- One sentence per line
- UTF-8 encoding
- Parallel structure (same number of sentences)

### 2. Run Alignment
```bash
./scripts/align_production.sh danish.txt kal.txt > output.txt
```

### 3. Filter Results
```bash
# Keep only high-confidence alignments (>0.5)
awk -F'\t' '$3 > 0.5' output.txt > high_quality.txt

# Convert to training format (@ separator)
awk -F'\t' '{print $1 " @ " $2}' high_quality.txt > training_pairs.txt
```

## Glossing Text

### Interactive Mode
```bash
cd glosser
python3 glosser_v2_fixed.py
# Enter text, press Ctrl+D when done
```

### Batch Processing
```bash
# Process all files in a directory
for file in input/*.txt; do
    python3 glosser_v2_fixed.py "$file" -f html -o "output/${file%.txt}.html"
done
```

## Troubleshooting

### hunalign Not Found
```bash
cd ~
git clone https://github.com/danielvarga/hunalign.git
cd hunalign/src/hunalign
make
```

### Dictionary Missing
```bash
cd ~/kalaallisut-aligner
python3 scripts/extract_cognates.py
```

### Morphology Not Working
```bash
cd ~/lang-kal
make clean
make
```

For more help, see: [project issues page]
