#!/bin/bash
# Verify kalaallisut-aligner installation

echo "🔍 Checking installation..."

ERRORS=0

# Check lang-kal
if [ ! -d "$HOME/lang-kal" ]; then
    echo "❌ lang-kal not found"
    ((ERRORS++))
else
    echo "✅ lang-kal found"
fi

# Check hunalign
if [ ! -f "$HOME/hunalign/src/hunalign/hunalign" ]; then
    echo "❌ hunalign not found"
    ((ERRORS++))
else
    echo "✅ hunalign found"
fi

# Check required files
for file in data/processed/cognates.json glosser/kalaallisut_english_dict.json; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing: $file"
        ((ERRORS++))
    else
        echo "✅ Found: $file"
    fi
done

if [ $ERRORS -eq 0 ]; then
    echo ""
    echo "✅ All checks passed!"
    exit 0
else
    echo ""
    echo "❌ $ERRORS errors found. See README.md for setup."
    exit 1
fi
