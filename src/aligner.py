#!/usr/bin/env python3
"""
Core alignment algorithm for Danish-Kalaallisut sentence pairs.
"""

import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Set, Any
from morphology import tokenize_text
from config import config

# Set up logging
logger = logging.getLogger(__name__)


class SentenceAligner:
    def __init__(self, stats_file: str = "data/processed/alignment_stats.json") -> None:
        """Initialize with training statistics.

        Args:
            stats_file: Path to JSON file with alignment statistics

        Raises:
            FileNotFoundError: If stats file doesn't exist
            ValueError: If stats file is invalid or missing required fields
        """
        stats_path = Path(stats_file)
        if not stats_path.exists():
            raise FileNotFoundError(
                f"Statistics file not found: {stats_file}\n"
                f"Run data preparation scripts first."
            )

        try:
            with open(stats_file, "r") as f:
                self.stats = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {stats_file}: {e}")

        # Validate required fields
        required_fields = ["avg_word_ratio", "avg_char_ratio"]
        missing = [f for f in required_fields if f not in self.stats]
        if missing:
            raise ValueError(f"Missing required fields in stats: {missing}")

        self.expected_word_ratio = self.stats["avg_word_ratio"]  # 1.48
        self.expected_char_ratio = self.stats["avg_char_ratio"]  # 0.75

    def split_sentences(self, text: str) -> List[str]:
        """Split text into sentences with date-aware splitting.

        Args:
            text: Input text to split

        Returns:
            List of sentence strings

        Raises:
            ValueError: If text is empty
        """
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")

        # Month names in Danish and Kalaallisut
        months = {
            "januar",
            "februar",
            "marts",
            "april",
            "maj",
            "juni",
            "juli",
            "august",
            "september",
            "oktober",
            "november",
            "december",
            "januaari",
            "februaari",
            "martsi",
            "apriili",
            "maaji",
            "juuni",
            "juuli",
            "aggusti",
            "septembari",
            "oktobari",
            "novembari",
            "decembari",
        }

        sentences = []
        current_chars = []

        for i, char in enumerate(text):
            current_chars.append(char)

            if char in ".!?":
                current = "".join(current_chars)
                if len(current.strip()) < config.min_sentence_length:
                    continue

                # Look ahead
                next_text = text[i + 1 :].strip()
                if not next_text:
                    sentences.append(current.strip())
                    current_chars = []
                    continue

                # Check if last token before period is a number
                words = current.strip().split()
                last_word = words[-1][:-1] if words else ""  # Remove period

                # Get next word
                next_word = next_text.split()[0] if next_text.split() else ""

                # Don't split if: number + period + month name
                if last_word.isdigit() and next_word.lower() in months:
                    continue

                # Don't split if next char is lowercase (abbreviations)
                if next_text[0].islower():
                    continue

                # Split on uppercase (new sentence)
                sentences.append(current.strip())
                current_chars = []

        if current_chars:
            sentences.append("".join(current_chars).strip())

        return sentences

    def calculate_similarity(
        self, danish_sent: str, kal_sent: str, da_pos: float, kal_pos: float
    ) -> float:
        """Calculate similarity score between two sentences.

        Args:
            danish_sent: Danish sentence
            kal_sent: Kalaallisut sentence
            da_pos: Relative position of Danish sentence (0.0-1.0)
            kal_pos: Relative position of Kalaallisut sentence (0.0-1.0)

        Returns:
            Similarity score (0.0-1.0)

        Raises:
            ValueError: If inputs are invalid
        """
        if not danish_sent or not danish_sent.strip():
            raise ValueError("Danish sentence cannot be empty")
        if not kal_sent or not kal_sent.strip():
            raise ValueError("Kalaallisut sentence cannot be empty")

        # Feature extraction
        da_words = len(danish_sent.split())
        da_chars = len(danish_sent)

        try:
            kal_tokens = tokenize_text(kal_sent)
        except (RuntimeError, ValueError):
            # If tokenization fails, fall back to simple split
            kal_tokens = kal_sent.split()

        kal_words = len([t for t in kal_tokens if t.strip() and t not in ".,;:!?"])
        kal_chars = len(kal_sent)

        # Validate all values are non-zero before division
        if kal_words == 0 or kal_chars == 0 or da_words == 0 or da_chars == 0:
            return 0.0

        # Calculate ratios (safe now - all values are non-zero)
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

        # Weighted combination (weights from config)
        similarity = (
            config.word_score_weight * max(0, word_score)
            + config.char_score_weight * max(0, char_score)
            + config.position_score_weight * max(0, position_score)
        )

        return similarity

    def align_greedy(
        self, danish_sentences: List[str], kal_sentences: List[str]
    ) -> List[Dict[str, Any]]:
        """Greedy alignment: match each Danish sentence to best Kalaallisut."""
        alignments: List[Dict[str, Any]] = []
        used_kal: Set[int] = set()

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

    def align_documents(self, danish_text: str, kal_text: str) -> List[Dict[str, Any]]:
        """Align two documents.

        Args:
            danish_text: Danish document text
            kal_text: Kalaallisut document text

        Returns:
            List of alignment dictionaries

        Raises:
            ValueError: If inputs are invalid
        """
        if not danish_text or not danish_text.strip():
            raise ValueError("Danish text cannot be empty")
        if not kal_text or not kal_text.strip():
            raise ValueError("Kalaallisut text cannot be empty")

        # Warn about large documents
        if len(danish_text) > 1_000_000:
            logger.warning(f"Large document ({len(danish_text)} chars)")

        logger.info("Splitting sentences...")
        try:
            danish_sents = self.split_sentences(danish_text)
            kal_sents = self.split_sentences(kal_text)
        except ValueError as e:
            raise ValueError(f"Sentence splitting failed: {e}")

        logger.info(f"Danish: {len(danish_sents)} sentences")
        logger.info(f"Kalaallisut: {len(kal_sents)} sentences")

        if not danish_sents or not kal_sents:
            raise ValueError("No sentences found after splitting")

        logger.info("Aligning...")
        alignments = self.align_greedy(danish_sents, kal_sents)

        logger.info(f"Created {len(alignments)} alignments")

        return alignments

    def save_alignments(
        self, alignments: List[Dict[str, Any]], output_file: str
    ) -> None:
        """Save alignments to file.

        Args:
            alignments: List of alignment dictionaries
            output_file: Path to output file

        Raises:
            ValueError: If alignments is empty
            IOError: If file cannot be written
        """
        if not alignments:
            raise ValueError("Cannot save empty alignments list")

        output_path = Path(output_file)
        # Create parent directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                for align in alignments:
                    f.write(f"{align['danish']} @ {align['kalaallisut']}\n")
        except IOError as e:
            raise IOError(f"Failed to write to {output_file}: {e}")

        logger.info(f"Saved to: {output_file}")


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
