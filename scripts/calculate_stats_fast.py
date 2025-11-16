#!/usr/bin/env python3
"""
Fast version: Calculate alignment statistics from training data using simple tokenization.
Computes average word ratio and character ratio for Danish-Kalaallisut pairs.
"""

import json
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from utils import load_aligned_pairs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def calculate_statistics_fast(pairs):
    """Calculate word and character ratios using simple tokenization.

    Args:
        pairs: List of dictionaries with 'danish' and 'kalaallisut' keys

    Returns:
        Dictionary with 'avg_word_ratio' and 'avg_char_ratio'
    """
    word_ratios = []
    char_ratios = []

    for i, pair in enumerate(pairs):
        if (i + 1) % 1000 == 0:
            logger.info(f"  Processed {i + 1}/{len(pairs)} pairs...")

        danish = pair['danish']
        kalaallisut = pair['kalaallisut']

        # Simple word count (fast)
        da_words = len(danish.split())
        kal_words = len(kalaallisut.split())

        # Character count
        da_chars = len(danish)
        kal_chars = len(kalaallisut)

        # Calculate ratios (avoid division by zero)
        if kal_words > 0 and kal_chars > 0:
            word_ratios.append(da_words / kal_words)
            char_ratios.append(da_chars / kal_chars)

    # Calculate averages
    avg_word_ratio = sum(word_ratios) / len(word_ratios) if word_ratios else 0
    avg_char_ratio = sum(char_ratios) / len(char_ratios) if char_ratios else 0

    return {
        'avg_word_ratio': avg_word_ratio,
        'avg_char_ratio': avg_char_ratio
    }


def main():
    # Paths
    base_dir = Path(__file__).parent.parent
    train_file = base_dir / "data" / "processed" / "train.txt"
    stats_file = base_dir / "data" / "processed" / "alignment_stats.json"
    backup_stats = base_dir / "data" / "processed" / "alignment_stats.json.backup"

    logger.info("=" * 60)
    logger.info("CALCULATING ALIGNMENT STATISTICS (FAST MODE)")
    logger.info("=" * 60)

    # Check if training file exists
    if not train_file.exists():
        logger.error(f"Training file not found: {train_file}")
        sys.exit(1)

    # Backup existing stats
    if stats_file.exists():
        logger.info(f"Backing up existing stats to: {backup_stats}")
        with open(stats_file, 'r') as f:
            old_stats = json.load(f)
        with open(backup_stats, 'w') as f:
            json.dump(old_stats, f, indent=2)
        logger.info(f"Old stats: {old_stats}")

    # Load training pairs
    logger.info(f"Loading training pairs from: {train_file}")
    pairs = load_aligned_pairs(str(train_file))
    logger.info(f"Loaded {len(pairs)} training pairs")

    # Calculate statistics
    logger.info("Calculating statistics (using simple tokenization)...")
    stats = calculate_statistics_fast(pairs)

    logger.info("=" * 60)
    logger.info("NEW STATISTICS")
    logger.info("=" * 60)
    logger.info(f"Average word ratio (DA/KL):  {stats['avg_word_ratio']:.4f}")
    logger.info(f"Average char ratio (DA/KL):  {stats['avg_char_ratio']:.4f}")

    if stats_file.exists():
        logger.info("")
        logger.info("COMPARISON WITH OLD STATS")
        logger.info("=" * 60)
        with open(stats_file, 'r') as f:
            old_stats = json.load(f)
        word_diff = stats['avg_word_ratio'] - old_stats['avg_word_ratio']
        char_diff = stats['avg_char_ratio'] - old_stats['avg_char_ratio']
        logger.info(f"Word ratio change: {word_diff:+.4f}")
        logger.info(f"Char ratio change: {char_diff:+.4f}")

    # Save new statistics
    logger.info("")
    logger.info(f"Saving statistics to: {stats_file}")
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)

    logger.info("=" * 60)
    logger.info("SUCCESS!")
    logger.info("=" * 60)
    logger.info("Statistics updated. Your aligner will now use these new ratios.")


if __name__ == "__main__":
    main()
