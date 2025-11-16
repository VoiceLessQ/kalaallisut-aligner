#!/usr/bin/env python3
"""
Script to parse parallel_corpus_clean.txt and append to training data.
Converts from DA/KL/CONF format to 'danish @ kalaallisut' format.
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from utils import load_aligned_pairs, save_pairs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_parallel_corpus(filepath: str, min_confidence: float = 0.0):
    """Parse parallel_corpus_clean.txt format.

    Format:
        DA: <danish text>
        KL: <kalaallisut text>
        CONF: <confidence>
        <empty line>

    Args:
        filepath: Path to parallel corpus file
        min_confidence: Minimum confidence threshold (0.0-1.0)

    Returns:
        List of dictionaries with 'danish' and 'kalaallisut' keys
    """
    pairs = []
    current_pair = {}

    logger.info(f"Reading from: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            if not line:
                # Empty line - process current pair
                if 'danish' in current_pair and 'kalaallisut' in current_pair:
                    confidence = current_pair.get('confidence', 1.0)

                    if confidence >= min_confidence:
                        pairs.append({
                            'danish': current_pair['danish'],
                            'kalaallisut': current_pair['kalaallisut']
                        })
                    else:
                        logger.debug(f"Skipping pair (low confidence {confidence:.3f})")

                current_pair = {}
                continue

            # Parse line
            if line.startswith('DA:'):
                current_pair['danish'] = line[3:].strip()
            elif line.startswith('KL:'):
                current_pair['kalaallisut'] = line[3:].strip()
            elif line.startswith('CONF:'):
                try:
                    current_pair['confidence'] = float(line[5:].strip())
                except ValueError:
                    logger.warning(f"Invalid confidence at line {line_num}: {line}")
                    current_pair['confidence'] = 0.0

    # Handle last pair if file doesn't end with empty line
    if 'danish' in current_pair and 'kalaallisut' in current_pair:
        confidence = current_pair.get('confidence', 1.0)
        if confidence >= min_confidence:
            pairs.append({
                'danish': current_pair['danish'],
                'kalaallisut': current_pair['kalaallisut']
            })

    logger.info(f"Parsed {len(pairs)} valid pairs")
    return pairs


def main():
    # Paths
    base_dir = Path(__file__).parent.parent
    new_corpus = base_dir / "data" / "test" / "parallel_corpus_clean.txt"
    train_file = base_dir / "data" / "processed" / "train.txt"
    backup_file = base_dir / "data" / "processed" / "train.txt.backup"

    # Check if new corpus exists
    if not new_corpus.exists():
        logger.error(f"File not found: {new_corpus}")
        sys.exit(1)

    # Parse new corpus
    logger.info("=" * 60)
    logger.info("APPENDING PARALLEL CORPUS TO TRAINING DATA")
    logger.info("=" * 60)

    new_pairs = parse_parallel_corpus(str(new_corpus), min_confidence=0.5)

    if not new_pairs:
        logger.error("No valid pairs found in new corpus!")
        sys.exit(1)

    logger.info(f"New pairs: {len(new_pairs)}")

    # Load existing training data
    if train_file.exists():
        logger.info(f"Loading existing training data from: {train_file}")
        existing_pairs = load_aligned_pairs(str(train_file))
        logger.info(f"Existing pairs: {len(existing_pairs)}")

        # Create backup
        logger.info(f"Creating backup: {backup_file}")
        save_pairs(existing_pairs, str(backup_file))

        # Combine
        all_pairs = existing_pairs + new_pairs
    else:
        logger.warning("No existing training file found, creating new one")
        all_pairs = new_pairs

    logger.info(f"Total pairs: {len(all_pairs)}")

    # Save combined data
    logger.info(f"Saving to: {train_file}")
    save_pairs(all_pairs, str(train_file))

    logger.info("=" * 60)
    logger.info("SUCCESS!")
    logger.info("=" * 60)
    logger.info(f"Added {len(new_pairs)} new pairs to training data")
    logger.info(f"Total training pairs: {len(all_pairs)}")
    logger.info("")
    logger.info("Sample from new data:")
    for i, pair in enumerate(new_pairs[:3], 1):
        logger.info(f"  {i}. DA: {pair['danish'][:60]}...")
        logger.info(f"     KL: {pair['kalaallisut'][:60]}...")
        logger.info("")

    logger.info("Next step: Regenerate alignment statistics")
    logger.info("Run: python scripts/calculate_stats.py")


if __name__ == "__main__":
    main()
