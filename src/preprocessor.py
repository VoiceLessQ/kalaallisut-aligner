#!/usr/bin/env python3
"""
Preprocessor for Kalaallisut text alignment.
Uses lang-kal tools for tokenization and morphological analysis.
"""

import json
import sys
from typing import List, Dict, Any
from morphology import tokenize_text, analyze_word
import logging

logger = logging.getLogger(__name__)


def process_sentence(sentence: str) -> List[Dict[str, Any]]:
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
            logger.warning(f"Failed to analyze '{token}': {e}")
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
