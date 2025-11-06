#!/usr/bin/env python3
"""
Kalaallisut morphological analysis utilities.
Consolidated module for tokenization and morphological analysis using HFST tools.
"""

import subprocess
from pathlib import Path
from typing import List, Dict, Any
import logging

from config import config

logger = logging.getLogger(__name__)

# Get paths from config
TOKENIZER = config.tokenizer_path
ANALYZER = config.analyzer_path

# Validate paths on import
if not ANALYZER.exists():
    logger.error(f"lang-kal analyzer not found at {ANALYZER}")
    logger.info("Install lang-kal or set LANG_KAL_PATH environment variable")
    logger.info("See: https://github.com/giellalt/lang-kal")


def tokenize_text(text: str) -> List[str]:
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


def analyze_word(word: str) -> List[Dict[str, Any]]:
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
