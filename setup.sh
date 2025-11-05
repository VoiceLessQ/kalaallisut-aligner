#!/bin/bash
# Setup script for kalaallisut-aligner project
# Handles dependency management and initial setup

set -e

echo "╔════════════════════════════════════════════╗"
echo "║  Kalaallisut-Danish Aligner Setup         ║"
echo "╚════════════════════════════════════════════╝"
echo ""

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Check if already set up
if [ -f ".setup_complete" ]; then
    echo "⚠️  Project already set up!"
    echo "   To re-setup, delete .setup_complete and run again."
    exit 0
fi

echo "📦 Step 1/7: Installing system dependencies..."
# Check if running as root for system package installation
if [ "$EUID" -eq 0 ]; then
    echo "   Installing build-essential, git, make, hunalign..."
    apt-get update -qq
    apt-get install -y build-essential git make hunalign
    echo "   ✅ System dependencies installed"
else
    echo "   ⚠️  Not running as root - system dependencies may not be installed"
    echo "   Please run with sudo or install manually:"
    echo "      sudo apt install build-essential git make hunalign"
fi
echo ""

echo "🐍 Step 2/7: Setting up Python environment..."
# Check Python availability
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3."
    exit 1
fi

# Install Python packages
echo "   Installing Python packages..."
pip3 install --break-system-packages pandas odfpy
echo "   ✅ Python environment set up"
echo ""

echo "📥 Step 3/7: Downloading and configuring lang-kal/GiellaLT..."
# Check if lang-kal exists
if [ ! -d "$HOME/lang-kal" ]; then
    echo "   Downloading lang-kal..."
    cd ~
    git clone https://github.com/giellalt/lang-kal.git
    cd lang-kal
    
    echo "   Configuring lang-kal..."
    ./autogen.sh
    ./configure --disable-syntax --enable-tokenisers --enable-analysers
    
    echo "   Building lang-kal (this may take a while)..."
    make -j$(nproc)
    
    echo "   ✅ lang-kal installed successfully"
else
    echo "   ✅ lang-kal already exists at ~/lang-kal"
fi
echo ""

echo "📁 Step 4/7: Setting up directory structure..."
# Create directory structure
mkdir -p data/{raw,processed,aligned,test}
mkdir -p src
mkdir -p scripts
mkdir -p glosser
mkdir -p docs
mkdir -p tests

# Create necessary subdirectories
mkdir -p data/aligned
mkdir -p data/processed
mkdir -p data/raw
mkdir -p data/test

echo "   ✅ Directory structure created"
echo ""

echo "📝 Step 5/7: Creating configuration files..."
# Create .gitignore
cat > .gitignore << 'GITEOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
venv/
env/

# Data
data/raw/*.txt
data/test/*.txt
*.zip
*.tar.gz

# Temporary
*.tmp
*.log
.DS_Store
*.swp

# IDE
.vscode/
.idea/

# Keep important files
!data/processed/cognates.json
!data/processed/hunalign_dict_full.txt
!data/processed/alignment_stats.json
!README.md
GITEOF

# Create config.json
cat > config.json << 'CONFIGEOF'
{
    "hunalign_path": "~/hunalign/src/hunalign/hunalign",
    "lang_kal_path": "~/lang-kal",
    "data_paths": {
        "raw": "data/raw",
        "processed": "data/processed",
        "aligned": "data/aligned",
        "test": "data/test"
    },
    "alignment": {
        "confidence_threshold": 0.5,
        "realign": true,
        "text_mode": true
    },
    "glosser": {
        "dictionary": "glosser/kalaallisut_english_dict.json",
        "morpheme_glosses": "glosser/morpheme_glosses.json"
    }
}
CONFIGEOF

echo "   ✅ Configuration files created"
echo ""

echo "🧪 Step 6/7: Verifying installation..."
# Test morphology if available
if command -v hfst-lookup &> /dev/null; then
    echo "   Testing morphological analyzer..."
    if echo "inuit" | hfst-lookup ~/lang-kal/src/fst/morphology/analyser-gt-desc.hfstol &> /dev/null; then
        echo "   ✅ Morphology analyzer working"
    else
        echo "   ⚠️  Morphology analyzer test failed"
    fi
else
    echo "   ⚠️  hfst-lookup not found (optional for morphology testing)"
fi

# Check hunalign
if [ -f "$HOME/hunalign/src/hunalign/hunalign" ]; then
    echo "   ✅ hunalign found at ~/hunalign/src/hunalign/hunalign"
else
    echo "   ⚠️  hunalign not found at expected location"
    echo "   Please install hunalign from: https://github.com/danielvarga/hunalign"
fi

# Check Python packages
if python3 -c "import pandas, odfpy" 2>/dev/null; then
    echo "   ✅ Python packages (pandas, odfpy) installed"
else
    echo "   ⚠️  Python packages not properly installed"
fi
echo ""

echo "📋 Step 7/7: Creating setup instructions..."
# Create setup instructions
cat > SETUP_INSTRUCTIONS.md << 'INSTRUCTIONSEOF'
# Setup Instructions

## Quick Setup
Run the setup script:
```bash
./setup.sh
```

## Manual Setup Steps

### 1. System Dependencies
```bash
sudo apt install build-essential git make hunalign
```

### 2. Python Environment
```bash
pip3 install pandas odfpy
```

### 3. lang-kal/GiellaLT
```bash
cd ~
git clone https://github.com/giellalt/lang-kal.git
cd lang-kal
./autogen.sh
./configure --disable-syntax --enable-tokenisers --enable-analysers
make
```

### 4. Verify Installation
```bash
# Test morphology
echo "inuit" | hfst-lookup ~/lang-kal/src/fst/morphology/analyser-gt-desc.hfstol

# Test hunalign
~/hunalign/src/hunalign/hunalign -help

# Test Python packages
python3 -c "import pandas, odfpy"
```

## Directory Structure
```
kalaallisut-aligner/
├── data/
│   ├── raw/          # Original data files
│   ├── processed/    # Processed data and dictionaries
│   ├── aligned/      # Alignment outputs
│   └── test/         # Test data
├── src/              # Source code
├── scripts/          # Utility scripts
├── glosser/          # Glossing tools
├── docs/            # Documentation
└── tests/           # Test files
```

## Configuration
Edit `config.json` to customize:
- Paths to tools
- Alignment parameters
- Glosser settings

## Troubleshooting
- If setup fails, check dependencies are installed
- Ensure all scripts have execute permissions
- Verify Python packages are installed correctly
- Check lang-kal compiled successfully
INSTRUCTIONSEOF

echo "   ✅ Setup instructions created"
echo ""

# Create completion marker
touch .setup_complete

echo "╔════════════════════════════════════════════╗"
echo "║  ✅ Setup Complete!                        ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "🚀 Quick Start:"
echo "   # Align documents"
echo "   ./scripts/align_production.sh danish.txt kal.txt > output.txt"
echo ""
echo "   # Gloss text"
echo "   cd glosser && python3 glosser_v2_fixed.py"
echo ""
echo "   # Test morphology"
echo "   python3 test_morphology.py"
echo ""
echo "📖 See README.md and SETUP_INSTRUCTIONS.md for documentation"
echo ""