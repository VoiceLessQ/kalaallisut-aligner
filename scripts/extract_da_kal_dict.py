#!/usr/bin/env python3
"""
Extract Danish-Kalaallisut word dictionary from aligned pairs.
"""

import json
from collections import defaultdict
from src.utils import load_aligned_pairs

# Load aligned pairs
pairs = load_aligned_pairs("data/raw/existing_alignments.txt")
print(f"Loaded {len(pairs)} sentence pairs")

# Count word co-occurrences
word_counts = defaultdict(lambda: defaultdict(int))

for pair in pairs:
    da_words = pair['danish'].lower().split()
    kal_words = pair['kalaallisut'].lower().split()
    
    # Count co-occurrences (simple approach)
    for da_word in da_words:
        for kal_word in kal_words:
            word_counts[da_word][kal_word] += 1

# Extract best translations (most frequent co-occurrence)
da_kal_dict = {}

for da_word, kal_counts in word_counts.items():
    # Skip if too short or punctuation
    if len(da_word) < 3 or da_word in '.,;:!?()[]':
        continue
    
    # Get most frequent Kalaallisut word
    if kal_counts:
        best_kal = max(kal_counts.items(), key=lambda x: x[1])
        # Only keep if appears at least 3 times
        if best_kal[1] >= 3:
            da_kal_dict[da_word] = best_kal[0]

print(f"\nExtracted {len(da_kal_dict)} word pairs")

# Save
with open('data/processed/danish_kalaallisut_dict.json', 'w', encoding='utf-8') as f:
    json.dump(da_kal_dict, f, indent=2, ensure_ascii=False)

print("Saved to: data/processed/danish_kalaallisut_dict.json")

# Show samples
print("\nSample entries:")
for i, (da, kal) in enumerate(list(da_kal_dict.items())[:20]):
    print(f"  {da} → {kal}")
