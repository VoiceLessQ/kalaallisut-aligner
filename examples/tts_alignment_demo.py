"""
Demo: Using Martha TTS for forced alignment and transcription assistance.

This demonstrates the "reverse engineering" approach:
- Use TTS to generate candidate audio
- Compare with source audio for alignment/transcription

Usage:
    python examples/tts_alignment_demo.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tts_aligner import MarthaTTS, TTSBasedAligner
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_basic_tts():
    """
    Demo 1: Basic TTS synthesis with Martha.

    Shows how to:
    1. Send text to Martha TTS
    2. Get back audio + word-level timestamps
    3. Download the generated audio
    """
    print("\n" + "="*60)
    print("DEMO 1: Basic TTS Synthesis")
    print("="*60 + "\n")

    tts = MarthaTTS()

    # Example Kalaallisut sentences
    examples = [
        "Aasaqqussuaq",  # "Summer"
        "Kalaallit Nunaat",  # "Greenland"
        "Imaqa",  # "Maybe"
        "Takussaanga",  # "I see him/her"
    ]

    print("Synthesizing Kalaallisut text using Martha TTS...\n")

    for text in examples:
        try:
            print(f"Text: {text}")
            result = tts.synthesize(text)

            print(f"  ✓ Generated: {result['fn']}")
            print(f"  ✓ Duration: {result['du']:.2f} seconds")
            print(f"  ✓ Size: {result['sz']:,} bytes")
            print(f"  ✓ URL: {result['audio_url']}")

            # Check for word-level timestamps
            if 'ts' in result and result['ts']:
                print(f"  ✓ Timestamps: {len(result['ts'])} timing points")
                print(f"    First few: {result['ts'][:3] if len(result['ts']) > 3 else result['ts']}")
            else:
                print("  ⚠ No timestamps available")

            print()

        except Exception as e:
            print(f"  ✗ Error: {e}\n")

    print("Note: Audio files can be downloaded from the URLs above")


def demo_corpus_synthesis():
    """
    Demo 2: Batch synthesize from aligned corpus.

    Shows how to:
    1. Load Kalaallisut sentences from corpus
    2. Generate TTS audio for each
    3. Build a reference audio dataset
    """
    print("\n" + "="*60)
    print("DEMO 2: Corpus-based TTS Generation")
    print("="*60 + "\n")

    tts = MarthaTTS()

    # Load some sentences from the aligned corpus
    corpus_file = Path("data/aligned/corpus_6798_pairs.txt")

    if not corpus_file.exists():
        print(f"⚠ Corpus file not found: {corpus_file}")
        print("This demo requires the aligned corpus.")
        return

    print(f"Loading sentences from {corpus_file}...\n")

    # Read first 5 sentence pairs
    sentences_kal = []
    sentences_da = []

    try:
        with open(corpus_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= 5:  # Just first 5 for demo
                    break

                parts = line.strip().split(' @ ')
                if len(parts) == 2:
                    da, kal = parts
                    sentences_da.append(da.strip())
                    sentences_kal.append(kal.strip())

        print(f"Loaded {len(sentences_kal)} sentence pairs\n")

        # Synthesize Kalaallisut sentences
        print("Synthesizing Kalaallisut sentences...\n")

        for i, (da, kal) in enumerate(zip(sentences_da, sentences_kal), 1):
            print(f"[{i}] Danish: {da}")
            print(f"    Kalaallisut: {kal}")

            try:
                # Check length
                if len(kal) > 200:  # Keep it short for demo
                    print(f"    ⚠ Skipped (too long: {len(kal)} chars)\n")
                    continue

                result = tts.synthesize(kal)
                print(f"    ✓ TTS: {result['du']:.2f}s - {result['audio_url']}")

                # Could download here:
                # output_path = Path(f"data/tts_output/sentence_{i}.mp3")
                # tts.download_audio(result['audio_url'], output_path)

            except Exception as e:
                print(f"    ✗ Error: {e}")

            print()

    except Exception as e:
        print(f"Error loading corpus: {e}")


def demo_alignment_concept():
    """
    Demo 3: Conceptual demo of TTS-based alignment.

    Shows the workflow for:
    1. Source audio + text → forced alignment
    2. Source audio only → transcription search
    """
    print("\n" + "="*60)
    print("DEMO 3: TTS-based Alignment Concept")
    print("="*60 + "\n")

    print("APPROACH 1: Forced Alignment (you have text + audio)")
    print("-" * 60)
    print("""
Workflow:
1. Input: source_audio.wav + "Takussaanga Kalaallit Nunaat"
2. Send text to Martha TTS → get reference.mp3 + word timestamps
3. Extract MFCC features from both audios
4. Run DTW alignment:
   - Compare source MFCCs vs reference MFCCs
   - Find optimal alignment path
5. Map Martha's timestamps to your audio using DTW path
6. Output: Word-level timestamps for your audio

Benefits:
✓ No ASR model needed
✓ Word-level timestamps from Martha
✓ Works with any Kalaallisut audio that matches the text

Challenges:
⚠ Requires DTW libraries (librosa, dtaidistance)
⚠ Accuracy depends on speaker/accent similarity
⚠ Computational cost for long audio
    """)

    print("\n\nAPPROACH 2: Transcription Search (audio only)")
    print("-" * 60)
    print("""
Workflow:
1. Input: source_audio.wav (unknown text)
2. Generate candidate sentences:
   - From aligned corpus (6,812 sentences)
   - From language model combinations
   - From dictionary n-grams
3. For each candidate:
   a. Martha TTS → generate audio
   b. Extract MFCCs
   c. DTW distance to source audio
4. Rank candidates by similarity
5. Output: Best matching text(s)

Benefits:
✓ No ASR model needed
✓ Works with constrained vocabulary (e.g., government docs)
✓ Can use existing corpus

Challenges:
⚠ Computationally expensive (many TTS calls)
⚠ Limited by API rate limits
⚠ Best for short utterances
⚠ Requires good candidate generation
    """)

    print("\n\nPRACTICAL USE CASES:")
    print("-" * 60)
    print("""
1. **Forced Alignment for Audiobooks**
   - You have: Kalaallisut text + audio recording
   - Need: Timestamps for each word/sentence
   - Solution: TTS + DTW alignment

2. **Corpus Alignment Verification**
   - You have: Danish-Kalaallisut aligned sentences
   - You have: Kalaallisut audio recordings
   - Need: Verify which audio matches which text
   - Solution: TTS synthesis + similarity matching

3. **Pronunciation Learning**
   - You have: Student audio recordings
   - You have: Reference text
   - Need: Compare student vs. reference pronunciation
   - Solution: TTS reference + DTW comparison

4. **Data Augmentation**
   - You have: Limited Kalaallisut audio dataset
   - Need: More training data for ASR
   - Solution: Use Martha TTS to generate synthetic audio
    """)


def demo_practical_example():
    """
    Demo 4: Practical code example for alignment.
    """
    print("\n" + "="*60)
    print("DEMO 4: Practical Code Example")
    print("="*60 + "\n")

    print("Here's how you would use the TTSBasedAligner:\n")

    print("""
from src.tts_aligner import TTSBasedAligner
from pathlib import Path

# Initialize aligner
aligner = TTSBasedAligner()

# Example 1: Forced alignment
source_audio = Path("my_audio.wav")
kalaallisut_text = "Kalaallit Nunaat"

result = aligner.align_audio(
    source_audio=source_audio,
    text=kalaallisut_text,
    output_dir=Path("alignment_output")
)

print(f"Word timings: {result['word_timings']}")
print(f"DTW distance: {result['dtw_distance']:.2f}")
print(f"Reference audio: {result['reference_audio']}")

# Example 2: Batch alignment from corpus
from src.utils import load_aligned_pairs

# Load corpus
pairs = load_aligned_pairs("data/aligned/corpus_6798_pairs.txt")

# Align first 10 pairs (if you have audio for them)
for i, (danish, kalaallisut) in enumerate(pairs[:10]):
    audio_file = Path(f"audio_data/sentence_{i}.wav")

    if audio_file.exists():
        result = aligner.align_audio(audio_file, kalaallisut)
        print(f"Aligned sentence {i}: {result['dtw_distance']:.2f}")
    """)

    print("\nNote: This requires audio files and librosa/dtaidistance packages")


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print(" Martha TTS Alignment Demo - Reverse Engineering Approach")
    print("="*70)
    print("""
This demo shows how to use Oqaasileriffik's Martha TTS for:
- Forced alignment (text + audio → timestamps)
- Transcription assistance (audio → text candidates)
- Audio similarity comparison

Martha TTS API: https://oqaasileriffik.gl/martha/tts/
    """)

    demos = [
        ("1. Basic TTS Synthesis", demo_basic_tts),
        ("2. Corpus-based TTS Generation", demo_corpus_synthesis),
        ("3. TTS-based Alignment Concept", demo_alignment_concept),
        ("4. Practical Code Example", demo_practical_example),
    ]

    print("\nAvailable demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")

    print("\nRunning all demos...\n")

    for name, demo_func in demos:
        try:
            demo_func()
        except KeyboardInterrupt:
            print("\n\nDemo interrupted by user")
            break
        except Exception as e:
            print(f"\nError in {name}: {e}")
            logger.exception("Demo failed")

    print("\n" + "="*70)
    print("Demo complete!")
    print("="*70)
    print("""
Next steps:
1. Install audio processing dependencies:
   pip install librosa dtaidistance numpy scipy

2. Try the basic TTS synthesis:
   python -c "from src.tts_aligner import MarthaTTS; tts = MarthaTTS(); print(tts.synthesize('Aasaqqussuaq'))"

3. Implement DTW alignment for your audio files

4. Explore the corpus for candidate sentences
    """)


if __name__ == "__main__":
    main()
