#!/usr/bin/env python3
"""
Extract cognates and loan words (reliable matches only).
"""

import json
from src.utils import load_aligned_pairs

pairs = load_aligned_pairs("data/raw/existing_alignments.txt")
print(f"Loaded {len(pairs)} pairs")

cognates = {}

for pair in pairs:
    da_words = [w.strip('.,;:!?()[]"').lower() for w in pair["danish"].split()]
    kal_words = [w.strip('.,;:!?()[]"').lower() for w in pair["kalaallisut"].split()]

    for da_word in da_words:
        for kal_word in kal_words:
            # Check if words are cognates (similar)
            if len(da_word) < 3 or len(kal_word) < 3:
                continue

            # Exact match
            if da_word == kal_word:
                cognates[da_word] = kal_word
            # Very similar (edit distance 1-2)
            elif (da_word in kal_word or kal_word in da_word) and abs(
                len(da_word) - len(kal_word)
            ) <= 2:
                if da_word not in cognates:  # Keep first match
                    cognates[da_word] = kal_word

print(f"Found {len(cognates)} cognates/loan words")

# Save
with open("data/processed/cognates.json", "w", encoding="utf-8") as f:
    json.dump(cognates, f, indent=2, ensure_ascii=False, sort_keys=True)

print("Saved to: data/processed/cognates.json")

print("\nSamples:")
for word in list(cognates.items())[:30]:
    print(f"  {word[0]} → {word[1]}")
