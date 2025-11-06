#!/usr/bin/env python3
"""
Utility functions for the aligner.
"""

import random
import sys
from pathlib import Path


def load_aligned_pairs(filepath):
    """Load existing aligned sentence pairs.

    Args:
        filepath: Path to file with aligned pairs (format: "danish @ kalaallisut")

    Returns:
        List of dictionaries with 'danish' and 'kalaallisut' keys

    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file cannot be read
        ValueError: If file format is invalid
    """
    file_path = Path(filepath)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    if not file_path.is_file():
        raise ValueError(f"Not a file: {filepath}")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            pairs = []
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or "@" not in line:
                    continue

                parts = line.split(" @ ")
                if len(parts) != 2:
                    print(
                        f"Warning: Skipping malformed line {line_num}: {line[:50]}...",
                        file=sys.stderr,
                    )
                    continue

                danish, kalaallisut = parts
                if not danish.strip() or not kalaallisut.strip():
                    print(
                        f"Warning: Skipping empty sentence at line {line_num}",
                        file=sys.stderr,
                    )
                    continue

                pairs.append(
                    {"danish": danish.strip(), "kalaallisut": kalaallisut.strip()}
                )
    except IOError as e:
        raise IOError(f"Failed to read {filepath}: {e}")
    except UnicodeDecodeError as e:
        raise ValueError(f"Invalid encoding in {filepath}: {e}")

    if not pairs:
        raise ValueError(f"No valid pairs found in {filepath}")

    return pairs


def split_train_test(pairs, test_ratio=0.2, seed=42):
    """Split data into train/test sets.

    Args:
        pairs: List of aligned pairs
        test_ratio: Fraction of data for test set (0.0-1.0)
        seed: Random seed for reproducibility

    Returns:
        Tuple of (train_pairs, test_pairs)

    Raises:
        ValueError: If inputs are invalid
    """
    if not pairs:
        raise ValueError("Cannot split empty pairs list")

    if not 0.0 < test_ratio < 1.0:
        raise ValueError(f"test_ratio must be between 0 and 1, got {test_ratio}")

    if len(pairs) < 2:
        raise ValueError("Need at least 2 pairs to split")

    random.seed(seed)
    shuffled = pairs.copy()
    random.shuffle(shuffled)

    split_point = int(len(shuffled) * (1 - test_ratio))

    # Ensure at least one item in each split
    if split_point == 0:
        split_point = 1
    elif split_point == len(shuffled):
        split_point = len(shuffled) - 1

    train = shuffled[:split_point]
    test = shuffled[split_point:]

    return train, test


def save_pairs(pairs, filepath):
    """Save pairs to file.

    Args:
        pairs: List of pair dictionaries
        filepath: Path to output file

    Raises:
        ValueError: If pairs is empty
        IOError: If file cannot be written
    """
    if not pairs:
        raise ValueError("Cannot save empty pairs list")

    file_path = Path(filepath)
    # Create parent directory if it doesn't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            for pair in pairs:
                if "danish" not in pair or "kalaallisut" not in pair:
                    raise ValueError(
                        f"Invalid pair format: {pair}. Must have 'danish' and 'kalaallisut' keys"
                    )
                f.write(f"{pair['danish']} @ {pair['kalaallisut']}\n")
    except IOError as e:
        raise IOError(f"Failed to write to {filepath}: {e}")


if __name__ == "__main__":
    # Test: split existing alignments
    input_file = Path("data/raw/existing_alignments.txt")

    print(f"Loading pairs from {input_file}...")
    pairs = load_aligned_pairs(input_file)
    print(f"Loaded {len(pairs)} pairs")

    print("\nSplitting into train/test...")
    train, test = split_train_test(pairs)
    print(f"Train: {len(train)} pairs")
    print(f"Test: {len(test)} pairs")

    # Save splits
    save_pairs(train, "data/processed/train.txt")
    save_pairs(test, "data/processed/test.txt")

    print("\nSaved:")
    print("  data/processed/train.txt")
    print("  data/processed/test.txt")

    # Show sample
    print("\nSample pair:")
    sample = train[0]
    print(f"  DA: {sample['danish']}")
    print(f"  KL: {sample['kalaallisut']}")
