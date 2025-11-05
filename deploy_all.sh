#!/bin/bash
# All-in-one deployment script for kalaallisut-aligner
# Executes the entire cleanup and setup process in one command

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to handle errors
handle_error() {
    print_error "Step failed: $1"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   1. Check if you're in the correct directory: kalaallisut-aligner"
    echo "   2. Ensure all dependencies are installed"
    echo "   3. Check file permissions"
    echo "   4. Review the error messages above"
    echo ""
    echo "💡 For help, see: cat docs/GUIDE.md"
    exit 1
}

# Main deployment function
main() {
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║  Kalaallisut-Danish Aligner - All-in-One Deployment             ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""

    # Step 1: Check if we're in the correct directory
    print_status "Step 1/7: Checking directory..."
    if [[ "$(basename "$PWD")" != "kalaallisut-aligner" ]]; then
        print_error "Not in the kalaallisut-aligner directory"
        echo "   Current directory: $PWD"
        echo "   Please navigate to the kalaallisut-aligner directory and run this script again"
        handle_error "Directory check failed"
    fi
    
    if [[ ! -f "deploy_clean.sh" || ! -f "setup.sh" ]]; then
        print_error "Required scripts not found"
        echo "   Make sure deploy_clean.sh and setup.sh are in the current directory"
        handle_error "Script check failed"
    fi
    
    print_success "Directory check passed"
    echo ""

    # Step 2: Create backup of current project
    print_status "Step 2/7: Creating backup..."
    if [[ -d "$HOME/kalaallisut-aligner" ]]; then
        BACKUP_DIR="$HOME/kalaallisut-aligner.backup.$(date +%Y%m%d_%H%M%S)"
        echo "   📦 Creating backup at: $BACKUP_DIR"
        
        if cp -r "$HOME/kalaallisut-aligner" "$BACKUP_DIR"; then
            print_success "Backup created successfully"
        else
            handle_error "Backup creation failed"
        fi
    else
        print_warning "No existing project found to backup"
    fi
    echo ""

    # Step 3: Execute the deploy_clean.sh script
    print_status "Step 3/7: Running deployment cleanup..."
    echo "   🧹 Executing deploy_clean.sh..."
    
    if bash deploy_clean.sh; then
        print_success "Deployment cleanup completed"
    else
        handle_error "Deployment cleanup failed"
    fi
    echo ""

    # Step 4: Run setup.sh to verify dependencies
    print_status "Step 4/7: Running setup verification..."
    echo "   🔧 Executing setup.sh..."
    
    if bash setup.sh; then
        print_success "Setup verification completed"
    else
        handle_error "Setup verification failed"
    fi
    echo ""

    # Step 5: Test the reorganized project structure
    print_status "Step 5/7: Testing project structure..."
    
    # Check if required directories exist
    REQUIRED_DIRS=(
        "data/raw"
        "data/processed"
        "data/aligned"
        "data/test"
        "src"
        "scripts"
        "glosser"
        "docs"
        "tests"
    )
    
    MISSING_DIRS=""
    for dir in "${REQUIRED_DIRS[@]}"; do
        if [[ ! -d "$dir" ]]; then
            MISSING_DIRS="$MISSING_DIRS\n   - $dir"
        fi
    done
    
    if [[ -n "$MISSING_DIRS" ]]; then
        print_error "Missing directories:$MISSING_DIRS"
        handle_error "Directory structure test failed"
    else
        print_success "All required directories exist"
    fi
    
    # Check if required files exist
    REQUIRED_FILES=(
        "PROJECT_INFO.txt"
        "README.md"
        "docs/GUIDE.md"
        ".gitignore"
        "config.json"
    )
    
    MISSING_FILES=""
    for file in "${REQUIRED_FILES[@]}"; do
        if [[ ! -f "$file" ]]; then
            MISSING_FILES="$MISSING_FILES\n   - $file"
        fi
    done
    
    if [[ -n "$MISSING_FILES" ]]; then
        print_warning "Missing files:$MISSING_FILES"
    else
        print_success "All required files exist"
    fi
    
    # Check if scripts are executable
    if [[ -x "scripts/align_production.sh" ]]; then
        print_success "Production aligner script is executable"
    else
        print_warning "Production aligner script not executable"
    fi
    
    if [[ -x "setup.sh" ]]; then
        print_success "Setup script is executable"
    else
        print_warning "Setup script not executable"
    fi
    echo ""

    # Step 6: Run a basic functionality test
    print_status "Step 6/7: Running basic functionality test..."
    
    # Test if Python can import required packages
    if python3 -c "import pandas, odfpy" 2>/dev/null; then
        print_success "Python packages (pandas, odfpy) are working"
    else
        print_warning "Python packages may not be properly installed"
    fi
    
    # Test if hunalign exists
    if [[ -f "$HOME/hunalign/src/hunalign/hunalign" ]]; then
        print_success "hunalign found at expected location"
    else
        print_warning "hunalign not found at expected location"
        echo "   Install with: git clone https://github.com/danielvarga/hunalign.git"
    fi
    
    # Test if lang-kal exists
    if [[ -d "$HOME/lang-kal" ]]; then
        print_success "lang-kal found at expected location"
    else
        print_warning "lang-kal not found at expected location"
        echo "   Install with: git clone https://github.com/giellalt/lang-kal.git"
    fi
    
    # Test morphology if available
    if command -v hfst-lookup &> /dev/null && [[ -f "$HOME/lang-kal/src/fst/morphology/analyser-gt-desc.hfstol" ]]; then
        if echo "inuit" | hfst-lookup "$HOME/lang-kal/src/fst/morphology/analyser-gt-desc.hfstol" &> /dev/null; then
            print_success "Morphological analyzer is working"
        else
            print_warning "Morphological analyzer test failed"
        fi
    else
        print_warning "Morphological analyzer not available for testing"
    fi
    echo ""

    # Step 7: Show final project status and next steps
    print_status "Step 7/7: Generating final status report..."
    
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║  ✅ Deployment Complete!                                         ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
    
    echo "📊 Project Status:"
    echo "   📁 Project Directory: $PWD"
    echo "   📦 Backup Location: ${BACKUP_DIR:-'No backup created'}"
    echo "   📅 Deployment Date: $(date)"
    echo ""
    
    echo "📁 Final Project Structure:"
    tree -L 2 -I '__pycache__|*.pyc' 2>/dev/null || (
        echo "   Directory structure:"
        find . -maxdepth 2 -type d | sed 's|^\./||' | grep -v '^\.' | sort | while read dir; do
            echo "   📂 $dir/"
        done
    )
    
    echo ""
    echo "🚀 Next Steps:"
    echo "   1. 📖 Read the documentation:"
    echo "      - cat README.md"
    echo "      - cat docs/GUIDE.md"
    echo ""
    echo "   2. 🔧 Test the components:"
    echo "      - python3 scripts/test_morphology.py"
    echo "      - cd glosser && python3 glosser_v2_fixed.py"
    echo ""
    echo "   3. 📚 Generate dictionaries (if needed):"
    echo "      - python3 scripts/extract_cognates.py"
    echo ""
    echo "   4. 🎯 Align documents:"
    echo "      - ./scripts/align_production.sh danish.txt kalaallisut.txt > output.txt"
    echo ""
    echo "   5. 📋 View project information:"
    echo "      - cat PROJECT_INFO.txt"
    echo ""
    
    echo "🔧 Troubleshooting:"
    echo "   - If something doesn't work, check the backup: ${BACKUP_DIR:-'N/A'}"
    echo "   - Run setup again: ./setup.sh"
    echo "   - Check documentation: cat docs/GUIDE.md"
    echo ""
    
    echo "💡 Tips:"
    echo "   - Keep your backup until you're satisfied with the deployment"
    echo "   - Update PROJECT_INFO.txt with your contact information"
    echo "   - Customize config.json for your specific needs"
    echo ""
    
    print_success "All-in-one deployment completed successfully!"
}

# Run main function with error handling
main "$@" || handle_error "Deployment process failed"