"""
Audio-to-Text Transcription using TTS Reverse Engineering.

This module transcribes Kalaallisut audio by:
1. Generating candidate texts from corpus/dictionary
2. Synthesizing each candidate using Martha TTS
3. Comparing audio similarity (DTW + MFCC)
4. Returning best matching text(s)

Usage:
    python src/audio_transcriber.py --audio my_audio.wav --top 5
"""

import argparse
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import time
import json

try:
    import librosa
    import numpy as np

    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    logging.warning("librosa not installed - audio processing unavailable")

try:
    from dtaidistance import dtw

    DTW_AVAILABLE = True
except ImportError:
    DTW_AVAILABLE = False
    logging.warning("dtaidistance not installed - DTW alignment unavailable")

from tts_aligner import MarthaTTS
from utils import load_aligned_pairs

logger = logging.getLogger(__name__)


class AudioTranscriber:
    """
    Transcribe Kalaallisut audio using TTS-based similarity matching.

    This "reverse engineers" transcription by:
    - Generating candidate texts
    - Using Martha TTS to synthesize audio for each
    - Finding which candidate sounds most similar to your audio

    No ASR model required!
    """

    def __init__(
        self, corpus_path: Optional[Path] = None, cache_dir: Optional[Path] = None
    ):
        """
        Initialize transcriber.

        Args:
            corpus_path: Path to aligned corpus for candidates
            cache_dir: Where to cache TTS audio files
        """
        self.tts = MarthaTTS()
        self.corpus_path = corpus_path or Path("data/aligned/corpus_6798_pairs.txt")
        self.cache_dir = cache_dir or Path("data/tts_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Load candidates
        self.candidates = self._load_candidates()
        logger.info(f"Loaded {len(self.candidates)} candidate sentences")

    def _load_candidates(self) -> List[str]:
        """
        Load candidate sentences from corpus.

        Returns:
            List of Kalaallisut sentences
        """
        if not self.corpus_path.exists():
            logger.warning(f"Corpus not found: {self.corpus_path}")
            return []

        try:
            pairs = load_aligned_pairs(str(self.corpus_path))
            # Extract Kalaallisut sentences (second element of each pair)
            candidates = [kal.strip() for da, kal in pairs if kal.strip()]

            logger.info(f"Loaded {len(candidates)} candidates from corpus")
            return candidates

        except Exception as e:
            logger.error(f"Failed to load corpus: {e}")
            return []

    def extract_mfcc(
        self, audio_path: Path, n_mfcc: int = 13, sr: int = 16000
    ) -> np.ndarray:
        """
        Extract MFCC features from audio.

        Args:
            audio_path: Path to audio file
            n_mfcc: Number of MFCC coefficients (default 13)
            sr: Sample rate (default 16kHz for speech)

        Returns:
            MFCC feature matrix (n_mfcc x time_frames)
        """
        if not AUDIO_AVAILABLE:
            raise ImportError("librosa required: pip install librosa")

        try:
            # Load audio
            y, _ = librosa.load(audio_path, sr=sr)

            # Extract MFCCs
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)

            # Normalize
            mfcc = (mfcc - np.mean(mfcc)) / (np.std(mfcc) + 1e-10)

            logger.debug(f"Extracted MFCC: {mfcc.shape} from {audio_path}")
            return mfcc

        except Exception as e:
            logger.error(f"MFCC extraction failed: {e}")
            raise

    def compute_similarity(
        self, source_mfcc: np.ndarray, candidate_mfcc: np.ndarray
    ) -> float:
        """
        Compute DTW similarity between two audio features.

        Args:
            source_mfcc: Source audio MFCCs
            candidate_mfcc: Candidate audio MFCCs

        Returns:
            DTW distance (lower = more similar)
        """
        if not DTW_AVAILABLE:
            raise ImportError("dtaidistance required: pip install dtaidistance")

        try:
            # Transpose for DTW (frames x features)
            distance = dtw.distance(source_mfcc.T, candidate_mfcc.T)
            return distance

        except Exception as e:
            logger.error(f"DTW computation failed: {e}")
            raise

    def filter_candidates_by_duration(
        self, audio_duration: float, candidates: List[str], tolerance: float = 0.3
    ) -> List[str]:
        """
        Filter candidates by estimated duration.

        Args:
            audio_duration: Source audio duration (seconds)
            candidates: List of candidate texts
            tolerance: Duration tolerance (0.3 = ±30%)

        Returns:
            Filtered candidates
        """
        # Rough estimate: ~3 characters per second for Kalaallisut
        chars_per_second = 3

        min_chars = int(audio_duration * chars_per_second * (1 - tolerance))
        max_chars = int(audio_duration * chars_per_second * (1 + tolerance))

        filtered = [c for c in candidates if min_chars <= len(c) <= max_chars]

        logger.info(
            f"Filtered {len(candidates)} → {len(filtered)} candidates "
            f"({min_chars}-{max_chars} chars for {audio_duration:.1f}s audio)"
        )

        return filtered

    def transcribe(
        self,
        audio_path: Path,
        top_k: int = 5,
        max_candidates: int = 100,
        delay_between_requests: float = 1.5,
    ) -> List[Tuple[str, float]]:
        """
        Transcribe audio by finding best matching text from candidates.

        Args:
            audio_path: Path to source audio file
            top_k: Return top K matches
            max_candidates: Maximum candidates to test
            delay_between_requests: Delay between TTS calls (seconds)

        Returns:
            List of (text, similarity_score) tuples, sorted by score
        """
        logger.info(f"Transcribing: {audio_path}")

        # Extract source audio features
        logger.info("Extracting source audio features...")
        source_mfcc = self.extract_mfcc(audio_path)

        # Get audio duration for filtering
        y, sr = librosa.load(audio_path, sr=16000)
        audio_duration = len(y) / sr
        logger.info(f"Source audio duration: {audio_duration:.2f}s")

        # Filter candidates by duration
        candidates = self.filter_candidates_by_duration(
            audio_duration, self.candidates, tolerance=0.3
        )

        # Limit candidates
        if len(candidates) > max_candidates:
            logger.info(f"Limiting to {max_candidates} candidates")
            # Sample evenly from corpus
            step = len(candidates) // max_candidates
            candidates = candidates[::step][:max_candidates]

        # Score each candidate
        scores = []

        for i, candidate_text in enumerate(candidates):
            logger.info(f"[{i+1}/{len(candidates)}] Testing: {candidate_text[:50]}...")

            try:
                # Generate TTS audio
                tts_result = self.tts.synthesize(candidate_text)

                if not tts_result or "audio_url" not in tts_result:
                    logger.warning(f"TTS failed for: {candidate_text[:30]}")
                    continue

                # Download audio
                cache_filename = self.cache_dir / f"candidate_{i:04d}.mp3"
                self.tts.download_audio(tts_result["audio_url"], cache_filename)

                # Extract features
                candidate_mfcc = self.extract_mfcc(cache_filename)

                # Compute similarity
                distance = self.compute_similarity(source_mfcc, candidate_mfcc)

                scores.append((candidate_text, distance))
                logger.info(f"  → Distance: {distance:.2f}")

                # Clean up cache to save space
                if cache_filename.exists():
                    cache_filename.unlink()

            except Exception as e:
                logger.error(f"Failed to process candidate: {e}")
                continue

            # Rate limiting
            if i < len(candidates) - 1:
                time.sleep(delay_between_requests)

        # Sort by distance (ascending - lower is better)
        scores.sort(key=lambda x: x[1])

        # Return top K
        top_results = scores[:top_k]

        logger.info(f"\nTop {len(top_results)} matches:")
        for i, (text, score) in enumerate(top_results, 1):
            logger.info(f"  {i}. [{score:.2f}] {text}")

        return top_results

    def transcribe_batch(
        self, audio_files: List[Path], output_json: Optional[Path] = None, **kwargs
    ) -> Dict[str, List[Tuple[str, float]]]:
        """
        Transcribe multiple audio files.

        Args:
            audio_files: List of audio file paths
            output_json: Save results to JSON file
            **kwargs: Additional args for transcribe()

        Returns:
            Dictionary mapping audio filename → top matches
        """
        results = {}

        for audio_file in audio_files:
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing: {audio_file}")
            logger.info("=" * 60)

            try:
                matches = self.transcribe(audio_file, **kwargs)
                results[str(audio_file)] = matches

            except Exception as e:
                logger.error(f"Failed to transcribe {audio_file}: {e}")
                results[str(audio_file)] = []

        # Save results
        if output_json:
            output_json.parent.mkdir(parents=True, exist_ok=True)
            with open(output_json, "w", encoding="utf-8") as f:
                # Convert to serializable format
                output = {
                    path: [(text, float(score)) for text, score in matches]
                    for path, matches in results.items()
                }
                json.dump(output, f, ensure_ascii=False, indent=2)

            logger.info(f"\nResults saved to: {output_json}")

        return results


def main():
    """Command-line interface for audio transcription."""
    parser = argparse.ArgumentParser(
        description="Transcribe Kalaallisut audio using TTS similarity matching"
    )
    parser.add_argument(
        "audio", type=Path, help="Audio file to transcribe (.wav, .mp3, etc.)"
    )
    parser.add_argument(
        "--corpus",
        type=Path,
        default=Path("data/aligned/corpus_6798_pairs.txt"),
        help="Path to aligned corpus for candidates",
    )
    parser.add_argument(
        "--top", type=int, default=5, help="Return top K matches (default: 5)"
    )
    parser.add_argument(
        "--max-candidates",
        type=int,
        default=100,
        help="Maximum candidates to test (default: 100)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.5,
        help="Delay between TTS requests in seconds (default: 1.5)",
    )
    parser.add_argument("--output", type=Path, help="Save results to JSON file")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Check dependencies
    if not AUDIO_AVAILABLE:
        logger.error("librosa not installed. Install with: pip install librosa")
        return 1

    if not DTW_AVAILABLE:
        logger.error(
            "dtaidistance not installed. Install with: pip install dtaidistance"
        )
        return 1

    # Check audio file exists
    if not args.audio.exists():
        logger.error(f"Audio file not found: {args.audio}")
        return 1

    # Initialize transcriber
    try:
        transcriber = AudioTranscriber(corpus_path=args.corpus)
    except Exception as e:
        logger.error(f"Failed to initialize transcriber: {e}")
        return 1

    # Transcribe
    try:
        results = transcriber.transcribe(
            audio_path=args.audio,
            top_k=args.top,
            max_candidates=args.max_candidates,
            delay_between_requests=args.delay,
        )

        # Print results
        print(f"\n{'='*60}")
        print(f"TRANSCRIPTION RESULTS: {args.audio}")
        print("=" * 60)

        for i, (text, score) in enumerate(results, 1):
            print(f"\n{i}. [Distance: {score:.2f}]")
            print(f"   {text}")

        # Save if requested
        if args.output:
            output_data = {
                "audio_file": str(args.audio),
                "matches": [
                    {"rank": i, "text": text, "distance": float(score)}
                    for i, (text, score) in enumerate(results, 1)
                ],
            }

            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)

            print(f"\nResults saved to: {args.output}")

        return 0

    except KeyboardInterrupt:
        logger.info("\nTranscription interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        logger.exception("Full traceback:")
        return 1


if __name__ == "__main__":
    exit(main())
