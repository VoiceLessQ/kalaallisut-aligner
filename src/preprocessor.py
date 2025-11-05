#!/usr/bin/env python3
"""
Preprocessor for Kalaallisut text alignment.
Uses lang-kal tools for tokenization and morphological analysis.
"""

import subprocess
import json
import os
import sys
from pathlib import Path

# Paths to lang-kal tools (support environment variable with fallback)
LANG_KAL_ROOT = Path(os.environ.get('LANG_KAL_PATH', Path.home() / "lang-kal"))
TOKENIZER = LANG_KAL_ROOT / "tools/tokenisers/tokeniser-disamb-gt-desc.pmhfst"
ANALYZER = LANG_KAL_ROOT / "src/fst/analyser-gt-desc.hfst"

# Validate paths on import
if not ANALYZER.exists():
    print(f"ERROR: lang-kal analyzer not found at {ANALYZER}", file=sys.stderr)
    print(f"Install lang-kal or set LANG_KAL_PATH environment variable", file=sys.stderr)
    print(f"See: https://github.com/giellalt/lang-kal", file=sys.stderr)


def tokenize_text(text):
    """Tokenize Kalaallisut text using lang-kal tokenizer."""
    try:
        result = subprocess.run(
            ["hfst-tokenize", str(TOKENIZER)],
            input=text,
            capture_output=True,
            text=True,
            check=True
        )
    except FileNotFoundError:
        print(f"ERROR: hfst-tokenize not found. Install HFST tools.", file=sys.stderr)
        return []
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Tokenization failed: {e.stderr}", file=sys.stderr)
        return []

    tokens = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
    return tokens


def analyze_word(word):
    """Get morphological analysis of a word."""
    try:
        result = subprocess.run(
            ["hfst-lookup", str(ANALYZER)],
            input=word,
            capture_output=True,
            text=True,
            check=False  # hfst-lookup returns non-zero for unknown words
        )
    except FileNotFoundError:
        print(f"ERROR: hfst-lookup not found. Install HFST tools.", file=sys.stderr)
        return []

    # Parse output (format: word\tanalysis\tweight)
    analyses = []
    for line in result.stdout.strip().split('\n'):
        if line.startswith('>') or not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) >= 2:
            analyses.append({
                'surface': parts[0],
                'analysis': parts[1],
                'weight': float(parts[2]) if len(parts) > 2 else 0.0
            })

    return analyses


def process_sentence(sentence):
    """Process a single sentence: tokenize and analyze."""
    tokens = tokenize_text(sentence)
    
    processed = []
    for token in tokens:
        analysis = analyze_word(token)
        processed.append({
            'token': token,
            'analyses': analysis,
            'word_count': 1 if analysis else 0,
            'morpheme_count': len(analysis[0]['analysis'].split('+')) if analysis else 0
        })
    
    return processed


if __name__ == "__main__":
    # Test
    test_sentence = "Takussaanga."
    result = process_sentence(test_sentence)
    print(json.dumps(result, indent=2, ensure_ascii=False))