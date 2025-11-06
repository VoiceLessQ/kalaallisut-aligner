#!/usr/bin/env python3
"""
Core alignment algorithm for Danish-Kalaallisut sentence pairs.
"""

import json
from pathlib import Path
from preprocessor import tokenize_text


class SentenceAligner:
    def __init__(self, stats_file="data/processed/alignment_stats.json"):
        """Initialize with training statistics."""
        with open(stats_file, "r") as f:
            self.stats = json.load(f)

        self.expected_word_ratio = self.stats["avg_word_ratio"]  # 1.48
        self.expected_char_ratio = self.stats["avg_char_ratio"]  # 0.75

    def split_sentences(self, text):
        """Split text into sentences (simple version)."""
        # Basic sentence splitting on periods, exclamation, question marks
        sentences = []
        current = ""

        for char in text:
            current += char
            if char in ".!?" and len(current.strip()) > 5:
                sentences.append(current.strip())
                current = ""

        if current.strip():
            sentences.append(current.strip())

        return sentences

    def calculate_similarity(self, danish_sent, kal_sent, da_pos, kal_pos):
        """Calculate similarity score between two sentences."""
        # Feature extraction
        da_words = len(danish_sent.split())
        da_chars = len(danish_sent)

        kal_tokens = tokenize_text(kal_sent)
        kal_words = len([t for t in kal_tokens if t.strip() and t not in ".,;:!?"])
        kal_chars = len(kal_sent)

        if kal_words == 0 or kal_chars == 0:
            return 0.0

        # Calculate ratios
        word_ratio = da_words / kal_words
        char_ratio = da_chars / kal_chars

        # Similarity scores (lower difference = higher score)
        word_score = (
            1.0 - abs(word_ratio - self.expected_word_ratio) / self.expected_word_ratio
        )
        char_score = (
            1.0 - abs(char_ratio - self.expected_char_ratio) / self.expected_char_ratio
        )

        # Position similarity (prefer same relative position)
        position_score = 1.0 - abs(da_pos - kal_pos)

        # Weighted combination
        similarity = (
            0.4 * max(0, word_score)
            + 0.3 * max(0, char_score)
            + 0.3 * max(0, position_score)
        )

        return similarity

    def align_greedy(self, danish_sentences, kal_sentences):
        """Greedy alignment: match each Danish sentence to best Kalaallisut."""
        alignments = []
        used_kal = set()

        for da_idx, da_sent in enumerate(danish_sentences):
            da_pos = da_idx / len(danish_sentences)

            best_score = -1
            best_kal_idx = -1

            # Find best matching Kalaallisut sentence
            for kal_idx, kal_sent in enumerate(kal_sentences):
                if kal_idx in used_kal:
                    continue

                kal_pos = kal_idx / len(kal_sentences)
                score = self.calculate_similarity(da_sent, kal_sent, da_pos, kal_pos)

                if score > best_score:
                    best_score = score
                    best_kal_idx = kal_idx

            if best_kal_idx >= 0:
                used_kal.add(best_kal_idx)
                alignments.append(
                    {
                        "danish": da_sent,
                        "kalaallisut": kal_sentences[best_kal_idx],
                        "confidence": best_score,
                        "da_index": da_idx,
                        "kal_index": best_kal_idx,
                    }
                )

        return alignments

    def align_documents(self, danish_text, kal_text):
        """Align two documents."""
        print("Splitting sentences...")
        danish_sents = self.split_sentences(danish_text)
        kal_sents = self.split_sentences(kal_text)

        print(f"  Danish: {len(danish_sents)} sentences")
        print(f"  Kalaallisut: {len(kal_sents)} sentences")

        print("\nAligning...")
        alignments = self.align_greedy(danish_sents, kal_sents)

        print(f"  Created {len(alignments)} alignments")

        return alignments

    def save_alignments(self, alignments, output_file):
        """Save alignments to file."""
        with open(output_file, "w", encoding="utf-8") as f:
            for align in alignments:
                f.write(f"{align['danish']} @ {align['kalaallisut']}\n")

        print(f"\nSaved to: {output_file}")


if __name__ == "__main__":
    # Test with a sample from test set
    from utils import load_aligned_pairs

    print("=== TESTING ALIGNER ===\n")

    # Load test data
    test_pairs = load_aligned_pairs("data/processed/test.txt")[:10]  # First 10

    # Simulate unaligned input
    danish_text = " ".join([p["danish"] for p in test_pairs])
    kal_text = " ".join([p["kalaallisut"] for p in test_pairs])

    # Align
    aligner = SentenceAligner()
    alignments = aligner.align_documents(danish_text, kal_text)

    # Show results
    print("\n=== SAMPLE ALIGNMENTS ===")
    for i, align in enumerate(alignments[:3]):
        print(f"\n{i+1}. Confidence: {align['confidence']:.2f}")
        print(f"   DA: {align['danish'][:80]}...")
        print(f"   KL: {align['kalaallisut'][:80]}...")

    # Save
    aligner.save_alignments(alignments, "data/aligned/test_output.txt")
