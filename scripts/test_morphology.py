#!/usr/bin/env python3
"""
Interactive Kalaallisut morphological analysis tester.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from morphology import analyze_word


def explain_morphology(analysis_str):
    """Break down morphological tags into readable explanation."""
    parts = analysis_str.split("+")

    tag_meanings = {
        "V": "Verb",
        "N": "Noun",
        "A": "Adjective",
        "Ind": "Indicative mood",
        "Imp": "Imperative mood",
        "Int": "Interrogative",
        "1Sg": "1st person singular (I)",
        "2Sg": "2nd person singular (you)",
        "3Sg": "3rd person singular (he/she/it)",
        "1Pl": "1st person plural (we)",
        "2Pl": "2nd person plural (you all)",
        "3Pl": "3rd person plural (they)",
        "1SgO": "object: me",
        "2SgO": "object: you",
        "3SgO": "object: him/her/it",
        "Sg": "Singular",
        "Pl": "Plural",
        "Abs": "Absolutive case",
        "Rel": "Relative case",
        "Trm": "Terminalis case",
        "Lok": "Locative case",
        "Abl": "Ablative case",
        "Gram/TV": "Transitive verb",
        "Gram/IV": "Intransitive verb",
        "Gram/Refl": "Reflexive",
        "Der/vv": "Verb-to-verb derivation",
        "SSA": "Future/intention marker",
    }

    explained = []
    root = parts[0]
    explained.append(f"ROOT: {root}")

    for part in parts[1:]:
        meaning = tag_meanings.get(part, part)
        explained.append(f"  + {part}: {meaning}")

    return "\n".join(explained)


def interactive_mode():
    """Interactive testing mode."""
    print("=== Kalaallisut Morphological Analyzer ===")
    print("Type words to analyze, or 'quit' to exit.\n")

    test_words = ["Takussaanga", "aalisartut", "inuit", "Kalaallit Nunaat", "pisuppoq"]

    print("Example words to try:")
    for word in test_words:
        print(f"  - {word}")
    print()

    while True:
        word = input("Word to analyze: ").strip()

        if word.lower() in ["quit", "exit", "q"]:
            break

        if not word:
            continue

        print(f"\nAnalyzing: {word}")
        print("-" * 60)

        try:
            analyses = analyze_word(word)
        except (RuntimeError, ValueError) as e:
            print(f"❌ Error: {e}")
            analyses = []

        if not analyses:
            print("❌ No analysis found (unknown word or not in lexicon)")
        else:
            for i, analysis in enumerate(analyses, 1):
                print(f"\nAnalysis {i}:")
                print(explain_morphology(analysis["analysis"]))
                print(f"Weight: {analysis['weight']:.2f}")

        print("\n" + "=" * 60 + "\n")


def batch_mode(words):
    """Analyze a list of words."""
    print("=== Batch Analysis ===\n")

    for word in words:
        print(f"Word: {word}")
        try:
            analyses = analyze_word(word)
        except (RuntimeError, ValueError) as e:
            print(f"❌ Error: {e}")
            analyses = []

        if analyses:
            # Show only first analysis
            print(explain_morphology(analyses[0]["analysis"]))
        else:
            print("❌ Not found")
        print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Batch mode with command line args
        batch_mode(sys.argv[1:])
    else:
        # Interactive mode
        interactive_mode()
