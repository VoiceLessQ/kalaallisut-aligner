#!/usr/bin/env python3
"""
Utility functions for the aligner.
"""

import random
from pathlib import Path


def load_aligned_pairs(filepath):
    """Load existing aligned sentence pairs."""
    pairs = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "@" not in line:
                continue

            parts = line.split(" @ ")
            if len(parts) == 2:
                danish, kalaallisut = parts
                pairs.append(
                    {"danish": danish.strip(), "kalaallisut": kalaallisut.strip()}
                )

    return pairs


def split_train_test(pairs, test_ratio=0.2, seed=42):
    """Split data into train/test sets."""
    random.seed(seed)
    shuffled = pairs.copy()
    random.shuffle(shuffled)

    split_point = int(len(shuffled) * (1 - test_ratio))
    train = shuffled[:split_point]
    test = shuffled[split_point:]

    return train, test


def save_pairs(pairs, filepath):
    """Save pairs to file."""
    with open(filepath, "w", encoding="utf-8") as f:
        for pair in pairs:
            f.write(f"{pair['danish']} @ {pair['kalaallisut']}\n")


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
