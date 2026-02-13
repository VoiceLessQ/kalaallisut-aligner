#!/bin/bash
# Cleanup and reorganize kalaallisut-aligner project

set -e

TARGET_DIR="$(pwd)"

echo "╔════════════════════════════════════════════╗"
echo "║  Deploying Clean Project Structure        ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# 1. Backup existing project
if [ -d "$TARGET_DIR" ]; then
    BACKUP="$TARGET_DIR.backup.$(date +%Y%m%d_%H%M%S)"
    echo "📦 Creating backup at: $BACKUP"
    cp -r "$TARGET_DIR" "$BACKUP"
    echo "   ✅ Backup created"
    echo ""
fi

cd "$TARGET_DIR"

# 2. Remove duplicate/temporary files
echo "🧹 Removing temporary files..."
rm -f aligner.py  # Duplicate - keep src/aligner.py
rm -f scores.txt scores_improved.txt
rm -f test_danish.txt test_kal.txt
rm -f hunalign_output.txt hunalign_text_output.txt
rm -f translate.txt
rm -f full_hunalign_output.txt full_hunalign_improved.txt
rm -f full_test_danish.txt full_test_kal.txt
rm -f high_quality_alignments.txt
rm -f config.json
echo "   ✅ Temporary files removed"
echo ""

# 3. Organize scripts
echo "📁 Organizing scripts..."
mkdir -p scripts
[ -f "extract_cognates.py" ] && mv extract_cognates.py scripts/ 2>/dev/null || true
[ -f "extract_da_kal_dict.py" ] && mv extract_da_kal_dict.py scripts/ 2>/dev/null || true
[ -f "align_production.sh" ] && mv align_production.sh scripts/ 2>/dev/null || true
[ -f "align_with_hunalign.sh" ] && mv align_with_hunalign.sh scripts/ 2>/dev/null || true
[ -f "run_alignment.py" ] && mv run_alignment.py scripts/ 2>/dev/null || true
[ -f "test_morphology.py" ] && mv test_morphology.py scripts/ 2>/dev/null || true
echo "   ✅ Scripts organized"
echo ""

# 4. Create proper directory structure
echo "📂 Creating directory structure..."
mkdir -p {data/{raw,processed,aligned,test},src,scripts,glosser,docs,tests}
echo "   ✅ Directories created"
echo ""

# 5. Move aligned corpus to data/aligned/
echo "📄 Moving aligned corpus..."
[ -f "aligned_all_danish_articles-all_kalaallisut_articles.txt" ] && \
    mv aligned_all_danish_articles-all_kalaallisut_articles.txt data/aligned/corpus_6798_pairs.txt
[ -f "full_test_kal.txt" ] && \
    mv full_test_kal.txt data/test/test_kalaallisut.txt
[ -f "full_test_danish.txt" ] && \
    mv full_test_danish.txt data/test/test_danish.txt
echo "   ✅ Corpus moved"
echo ""

# 6. Create .gitignore file
echo "📝 Creating .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/

# Virtual environments
venv/
env/
ENV/

# Data files
data/raw/*.txt
data/processed/*.txt
*.zip
*.tar.gz

# Temporary files
*.tmp
*.log
.DS_Store

# IDE
.vscode/
.idea/
*.swp
*.swo

# Keep important files
!data/processed/cognates.json
!data/processed/hunalign_dict_full.txt
!data/processed/alignment_stats.json
!README.md
EOF
echo "   ✅ .gitignore created"
echo ""

# 7. Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x setup.sh 2>/dev/null || true
echo "   ✅ Scripts made executable"
echo ""

# 8. Create documentation
echo "📝 Creating documentation..."
mkdir -p docs
cat > docs/GUIDE.md << 'EOF'
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
EOF
echo "   ✅ Documentation created"
echo ""

# 9. Create project info
cat > PROJECT_INFO.txt << 'EOF'
Kalaallisut-Danish Sentence Aligner
====================================

Version: 1.0
Built: November 2025
Status: Active development

Components:
- Morphological analyzer (lang-kal/GiellaLT)
- Sentence aligner (hunalign + cognates)
- Glosser (16,819 dictionary entries)
- Cognate extractor (1,526 entries)

Dataset:
- 6,798 aligned sentence pairs
- 5,438 training / 1,360 test
- Danish-Kalaallisut government documents

Performance:
- Alignment confidence: 48.1% average
- High confidence (>0.5): 34.7%
- Morphology coverage: 16,819 roots

For setup: ./setup.sh
For usage: cat README.md
For help: cat docs/GUIDE.md
EOF
echo "   ✅ Project info created"
echo ""

# 10. Show final project structure
echo "╔════════════════════════════════════════════╗"
echo "║  ✅ Deployment Complete!                   ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "📁 Project Structure:"
tree -L 2 -I '__pycache__|*.pyc' 2>/dev/null || find . -maxdepth 2 -type d | sed 's|^\./||' | grep -v '^\.' | sort

echo ""
echo "🚀 Next Steps:"
echo "   1. Run: ./setup.sh"
echo "   2. Read: cat README.md"
echo "   3. Test: python3 scripts/test_morphology.py"
echo ""