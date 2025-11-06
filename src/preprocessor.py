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
LANG_KAL_ROOT = Path(os.environ.get("LANG_KAL_PATH", Path.home() / "lang-kal"))
TOKENIZER = LANG_KAL_ROOT / "tools/tokenisers/tokeniser-disamb-gt-desc.pmhfst"
ANALYZER = LANG_KAL_ROOT / "src/fst/analyser-gt-desc.hfst"

# Validate paths on import
if not ANALYZER.exists():
    print(f"ERROR: lang-kal analyzer not found at {ANALYZER}", file=sys.stderr)
    print(
        f"Install lang-kal or set LANG_KAL_PATH environment variable", file=sys.stderr
    )
    print(f"See: https://github.com/giellalt/lang-kal", file=sys.stderr)


def tokenize_text(text):
    """Tokenize Kalaallisut text using lang-kal tokenizer.

    Args:
        text: Input text to tokenize

    Returns:
        List of tokens

    Raises:
        RuntimeError: If HFST tools are not available or tokenization fails
        ValueError: If input text is empty
    """
    if not text or not text.strip():
        raise ValueError("Input text cannot be empty")

    if not TOKENIZER.exists():
        raise RuntimeError(
            f"Tokenizer not found at {TOKENIZER}\n"
            f"Install lang-kal or set LANG_KAL_PATH environment variable\n"
            f"See: https://github.com/giellalt/lang-kal"
        )

    try:
        result = subprocess.run(
            ["hfst-tokenize", str(TOKENIZER)],
            input=text,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,  # Add timeout to prevent hanging
        )
    except FileNotFoundError:
        raise RuntimeError(
            "hfst-tokenize command not found. Install HFST tools.\n"
            "See: https://github.com/giellalt/lang-kal"
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Tokenization timed out for text: {text[:100]}...")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Tokenization failed: {e.stderr}")

    tokens = [
        line.strip() for line in result.stdout.strip().split("\n") if line.strip()
    ]
    return tokens


def analyze_word(word):
    """Get morphological analysis of a word.

    Args:
        word: Kalaallisut word to analyze

    Returns:
        List of analysis dictionaries with keys:
        - surface: The analyzed word
        - analysis: Morphological analysis string
        - weight: Analysis weight (lower is better)

    Raises:
        RuntimeError: If HFST tools are not available
        ValueError: If word is empty
    """
    if not word or not word.strip():
        raise ValueError("Word cannot be empty")

    if not ANALYZER.exists():
        raise RuntimeError(
            f"Analyzer not found at {ANALYZER}\n"
            f"Install lang-kal or set LANG_KAL_PATH environment variable\n"
            f"See: https://github.com/giellalt/lang-kal"
        )

    try:
        result = subprocess.run(
            ["hfst-lookup", str(ANALYZER)],
            input=word,
            capture_output=True,
            text=True,
            check=False,  # hfst-lookup returns non-zero for unknown words
            timeout=10,  # Add timeout
        )
    except FileNotFoundError:
        raise RuntimeError(
            "hfst-lookup command not found. Install HFST tools.\n"
            "See: https://github.com/giellalt/lang-kal"
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Analysis timed out for word: {word}")

    # Parse output (format: word\tanalysis\tweight)
    analyses = []
    for line in result.stdout.strip().split("\n"):
        if line.startswith(">") or not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            analyses.append(
                {
                    "surface": parts[0],
                    "analysis": parts[1],
                    "weight": float(parts[2]) if len(parts) > 2 else 0.0,
                }
            )

    return analyses


def process_sentence(sentence):
    """Process a single sentence: tokenize and analyze.

    Args:
        sentence: Input sentence to process

    Returns:
        List of processed token dictionaries

    Raises:
        ValueError: If sentence is empty
        RuntimeError: If processing fails
    """
    if not sentence or not sentence.strip():
        raise ValueError("Sentence cannot be empty")

    try:
        tokens = tokenize_text(sentence)
    except (RuntimeError, ValueError) as e:
        raise RuntimeError(f"Tokenization failed: {e}")

    processed = []
    for token in tokens:
        # Skip empty tokens and punctuation
        if not token.strip() or token in ".,;:!?":
            continue

        try:
            analysis = analyze_word(token)
        except ValueError:
            # Skip empty words
            continue
        except RuntimeError as e:
            # Log error but continue processing
            print(f"Warning: Failed to analyze '{token}': {e}", file=sys.stderr)
            analysis = []

        processed.append(
            {
                "token": token,
                "analyses": analysis,
                "word_count": 1 if analysis else 0,
                "morpheme_count": (
                    len(analysis[0]["analysis"].split("+")) if analysis else 0
                ),
            }
        )

    return processed


if __name__ == "__main__":
    # Test
    test_sentence = "Takussaanga."
    result = process_sentence(test_sentence)
    print(json.dumps(result, indent=2, ensure_ascii=False))
