"""
Extract alignment features from training data.
"""

import json
import logging
from pathlib import Path
from morphology import tokenize_text, analyze_word
from utils import load_aligned_pairs

logger = logging.getLogger(__name__)


def extract_features(pair):
    """Extract features from a sentence pair."""
    danish = pair["danish"]
    kalaallisut = pair["kalaallisut"]

    # Danish features (simple tokenization)
    danish_tokens = danish.split()
    danish_word_count = len(danish_tokens)
    danish_char_count = len(danish)

    # Kalaallisut features (using lang-kal)
    kal_tokens = tokenize_text(kalaallisut)
    kal_word_count = len([t for t in kal_tokens if t.strip() and not t in ".,;:!?"])
    kal_char_count = len(kalaallisut)

    # Morpheme count (sample first word only for speed)
    kal_morpheme_count = 0
    if kal_tokens:
        first_word = kal_tokens[0]
        analyses = analyze_word(first_word)
        if analyses:
            kal_morpheme_count = len(analyses[0]["analysis"].split("+"))

    return {
        "danish_words": danish_word_count,
        "danish_chars": danish_char_count,
        "kalaallisut_words": kal_word_count,
        "kalaallisut_chars": kal_char_count,
        "kalaallisut_morphemes": kal_morpheme_count,
        "word_ratio": danish_word_count / kal_word_count if kal_word_count > 0 else 0,
        "char_ratio": danish_char_count / kal_char_count if kal_char_count > 0 else 0,
    }


def analyze_training_data(pairs, sample_size=100):
    """Analyze training data to extract patterns."""
    logger.info(f"Analyzing {sample_size} pairs...")

    features = []
    for i, pair in enumerate(pairs[:sample_size]):
        if i % 20 == 0:
            logger.info(f"  Processing {i}/{sample_size}...")

        feat = extract_features(pair)
        features.append(feat)

    # Calculate statistics
    word_ratios = [f["word_ratio"] for f in features if f["word_ratio"] > 0]
    char_ratios = [f["char_ratio"] for f in features if f["char_ratio"] > 0]

    stats = {
        "avg_word_ratio": sum(word_ratios) / len(word_ratios),
        "avg_char_ratio": sum(char_ratios) / len(char_ratios),
        "sample_count": len(features),
    }

    return stats


if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("Loading training data...")
    train_pairs = load_aligned_pairs("data/processed/train.txt")

    logger.info(f"Loaded {len(train_pairs)} training pairs")

    # Analyze subset (100 pairs for speed)
    stats = analyze_training_data(train_pairs, sample_size=100)

    logger.info("=== ALIGNMENT STATISTICS ===")
    logger.info(f"Average word ratio (DA:KL): {stats['avg_word_ratio']:.2f}")
    logger.info(f"Average char ratio (DA:KL): {stats['avg_char_ratio']:.2f}")

    # Save stats
    with open("data/processed/alignment_stats.json", "w") as f:
        json.dump(stats, f, indent=2)

    logger.info("Saved to: data/processed/alignment_stats.json")
