#!/usr/bin/env python3
"""
Example script demonstrating how to use the Kalaallisut-Danish aligner.

This script shows how to:
1. Initialize the aligner
2. Align Danish and Kalaallisut text
3. Filter results by confidence
4. Save alignments to file
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aligner import SentenceAligner


def main():
    print("=" * 70)
    print("Kalaallisut-Danish Sentence Aligner - Example Usage")
    print("=" * 70)
    print()

    # Sample Danish text
    danish_text = """
Grønlands parlament mødes i dag.
Regeringen præsenterer det nye budget.
Der er store forventninger til de nye tiltag.
Økonomien er blevet diskuteret indgående.
    """.strip()

    # Sample Kalaallisut text
    kalaallisut_text = """
Kalaallit Nunaanni inatsisartut ullumi ataatsimiinnissavaat.
Naalakkersuisut kingorna aningaasanik nalunaaruteqarnermi saqqummiunneqartartunik saqqummiunneqarput.
Suliassaqarneq kingullermi oqallinneqarpoq.
    """.strip()

    print("Input Texts:")
    print("-" * 70)
    print("DANISH:")
    print(danish_text)
    print()
    print("KALAALLISUT:")
    print(kalaallisut_text)
    print()

    # Initialize aligner
    print("Initializing aligner...")
    stats_file = Path(__file__).parent.parent / "data" / "processed" / "alignment_stats.json"
    aligner = SentenceAligner(str(stats_file))
    print(f"Using alignment statistics from: {stats_file}")
    print(f"  - Expected word ratio (DA/KL): {aligner.expected_word_ratio:.2f}")
    print(f"  - Expected char ratio (DA/KL): {aligner.expected_char_ratio:.2f}")
    print()

    # Align documents
    print("Aligning documents...")
    alignments = aligner.align_documents(danish_text, kalaallisut_text)
    print()

    # Display results
    print("=" * 70)
    print("ALIGNMENT RESULTS")
    print("=" * 70)
    print()

    for i, align in enumerate(alignments, 1):
        conf = align['confidence']
        quality = "HIGH" if conf > 0.7 else "MEDIUM" if conf > 0.4 else "LOW"

        print(f"Alignment {i} - Confidence: {conf:.3f} ({quality})")
        print(f"  DA [{align['da_index']}]: {align['danish']}")
        print(f"  KL [{align['kal_index']}]: {align['kalaallisut']}")
        print()

    # Statistics
    high_conf = sum(1 for a in alignments if a['confidence'] > 0.5)
    medium_conf = sum(1 for a in alignments if 0.3 < a['confidence'] <= 0.5)
    low_conf = sum(1 for a in alignments if a['confidence'] <= 0.3)

    print("=" * 70)
    print("STATISTICS")
    print("=" * 70)
    print(f"Total alignments:       {len(alignments)}")
    print(f"High confidence (>0.5): {high_conf} ({100*high_conf/len(alignments):.1f}%)")
    print(f"Medium (0.3-0.5):       {medium_conf} ({100*medium_conf/len(alignments):.1f}%)")
    print(f"Low (<0.3):             {low_conf} ({100*low_conf/len(alignments):.1f}%)")
    print()

    # Save to file (optional)
    output_file = Path(__file__).parent / "example_output.txt"
    aligner.save_alignments(alignments, str(output_file))
    print(f"Results saved to: {output_file}")
    print()

    # Show how to filter by confidence
    print("=" * 70)
    print("FILTERED RESULTS (Confidence > 0.5)")
    print("=" * 70)
    print()

    high_quality = [a for a in alignments if a['confidence'] > 0.5]
    if high_quality:
        for i, align in enumerate(high_quality, 1):
            print(f"{i}. [{align['confidence']:.3f}]")
            print(f"   DA: {align['danish']}")
            print(f"   KL: {align['kalaallisut']}")
            print()
    else:
        print("No alignments with confidence > 0.5")
        print()

    print("=" * 70)
    print("Example completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
