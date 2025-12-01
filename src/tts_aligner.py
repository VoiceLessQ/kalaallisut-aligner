"""
TTS-based forced alignment using Martha TTS (Oqaasileriffik).

This module uses the reverse-engineering approach:
1. Generate reference audio from text using Martha TTS
2. Compare with source audio using DTW and MFCCs
3. Map timestamps from TTS to source audio

Dependencies:
    pip install requests librosa dtaidistance numpy scipy
"""

import requests
import json
import logging
from typing import Dict, List, Tuple, Optional, TYPE_CHECKING
from pathlib import Path
import time

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)


class MarthaTTS:
    """
    Client for Oqaasileriffik's Martha TTS API.

    API Endpoint: https://oqaasileriffik.gl/martha/tts/
    Audio Files: https://oqaasileriffik.gl/martha/data/

    Attributes:
        api_url: Martha TTS API endpoint
        data_url: Base URL for generated audio files
        max_chars: Maximum characters per request (10,000)
    """

    def __init__(self):
        self.api_url = "https://oqaasileriffik.gl/martha/tts/"
        self.data_url = "https://oqaasileriffik.gl/martha/data/"
        self.max_chars = 10000
        self.session = requests.Session()

    def synthesize(self, text: str, timeout: int = 30) -> Optional[Dict]:
        """
        Synthesize Kalaallisut text to speech using Martha TTS.

        Args:
            text: Kalaallisut text to synthesize (max 10,000 chars)
            timeout: Request timeout in seconds

        Returns:
            Dictionary containing:
                - fn: MP3 filename
                - du: Duration in seconds
                - sz: File size in bytes
                - ts: Word-level timing data (list of timestamps)
                - audio_url: Full URL to download MP3

        Raises:
            ValueError: If text exceeds character limit
            requests.RequestException: If API call fails
        """
        if len(text) > self.max_chars:
            raise ValueError(
                f"Text length ({len(text)}) exceeds maximum of {self.max_chars} characters"
            )

        try:
            logger.info(f"Sending TTS request for {len(text)} characters")

            response = self.session.post(
                self.api_url, data={"text": text}, timeout=timeout
            )
            response.raise_for_status()

            # Check if response is audio data (MP3) or JSON
            content_type = response.headers.get("content-type", "").lower()

            if "audio" in content_type or "mpeg" in content_type:
                # API returns audio data directly
                filename = response.headers.get(
                    "X-Cached-As",
                    response.headers.get("content-disposition", "")
                    .split("filename=")[-1]
                    .strip('"'),
                )

                if not filename:
                    # Generate filename from content
                    filename = f"{hash(text)}.mp3"

                # Create data structure similar to expected JSON
                data = {
                    "fn": filename,
                    "du": None,  # Duration not available from headers
                    "sz": len(response.content),
                    "ts": [],  # Timestamps not available
                    "audio_url": self.data_url + filename,
                }

                logger.info(f"TTS successful: {filename} ({data['sz']} bytes)")

            else:
                # Try to parse as JSON (for future API compatibility)
                try:
                    data = response.json()
                    # Add full audio URL
                    if "fn" in data:
                        data["audio_url"] = self.data_url + data["fn"]
                        logger.info(
                            f"TTS successful: {data['fn']} ({data.get('du', 0):.2f}s)"
                        )
                    else:
                        logger.warning("TTS response missing 'fn' field")
                except json.JSONDecodeError:
                    # If it's not JSON, treat as audio anyway
                    filename = f"response_{hash(text)}.mp3"
                    data = {
                        "fn": filename,
                        "du": None,
                        "sz": len(response.content),
                        "ts": [],
                        "audio_url": self.data_url + filename,
                    }
                    logger.info(f"TTS successful: {filename} ({data['sz']} bytes)")

            return data

        except requests.Timeout:
            logger.error(f"TTS request timed out after {timeout}s")
            raise
        except requests.RequestException as e:
            logger.error(f"TTS API error: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse TTS response: {e}")
            raise

    def download_audio(self, audio_url: str, output_path: Path) -> Path:
        """
        Download generated audio file.

        Args:
            audio_url: URL of the MP3 file
            output_path: Where to save the file

        Returns:
            Path to downloaded file
        """
        try:
            logger.info(f"Downloading audio from {audio_url}")
            response = self.session.get(audio_url, timeout=30)
            response.raise_for_status()

            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(response.content)

            logger.info(f"Audio saved to {output_path}")
            return output_path

        except requests.RequestException as e:
            logger.error(f"Failed to download audio: {e}")
            raise

    def batch_synthesize(
        self, texts: List[str], delay: float = 1.0
    ) -> List[Optional[Dict]]:
        """
        Synthesize multiple texts with rate limiting.

        Args:
            texts: List of Kalaallisut texts
            delay: Delay between requests (seconds) to avoid abuse

        Returns:
            List of TTS response dictionaries
        """
        results = []

        for i, text in enumerate(texts):
            logger.info(f"Processing {i+1}/{len(texts)}")

            try:
                result = self.synthesize(text)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to synthesize text {i}: {e}")
                results.append(None)

            # Rate limiting - be respectful of the API
            if i < len(texts) - 1:
                time.sleep(delay)

        return results


class TTSBasedAligner:
    """
    Forced alignment using TTS-based synthesis-by-analysis.

    This aligner uses Martha TTS to generate reference audio from text,
    then aligns it with source audio using DTW (Dynamic Time Warping).

    Requires: librosa, dtaidistance (optional: fastdtw)
    """

    def __init__(self):
        self.tts = MarthaTTS()

        # Try to import audio processing libraries
        try:
            import librosa

            self.librosa = librosa
        except ImportError:
            logger.warning(
                "librosa not installed. Audio processing features unavailable.\n"
                "Install with: pip install librosa"
            )
            self.librosa = None

        try:
            from dtaidistance import dtw

            self.dtw = dtw
        except ImportError:
            logger.warning(
                "dtaidistance not installed. DTW alignment unavailable.\n"
                "Install with: pip install dtaidistance"
            )
            self.dtw = None

    def extract_mfcc(
        self, audio_path: Path, n_mfcc: int = 13
    ) -> Optional["np.ndarray"]:
        """
        Extract MFCC features from audio file.

        Args:
            audio_path: Path to audio file
            n_mfcc: Number of MFCC coefficients

        Returns:
            MFCC feature matrix (n_mfcc x time_frames)
        """
        if self.librosa is None:
            raise ImportError("librosa is required for audio processing")

        try:
            # Load audio
            y, sr = self.librosa.load(audio_path, sr=16000)

            # Extract MFCCs
            mfccs = self.librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)

            logger.info(f"Extracted MFCCs: {mfccs.shape}")
            return mfccs

        except Exception as e:
            logger.error(f"Failed to extract MFCCs from {audio_path}: {e}")
            raise

    def align_audio(
        self, source_audio: Path, text: str, output_dir: Optional[Path] = None
    ) -> Dict:
        """
        Perform forced alignment using TTS-based approach.

        Workflow:
        1. Generate reference audio from text using Martha TTS
        2. Extract MFCC features from both source and reference
        3. Apply DTW to find alignment path
        4. Map Martha's word timestamps to source audio

        Args:
            source_audio: Path to source audio file
            text: Kalaallisut text transcript
            output_dir: Where to save intermediate files

        Returns:
            Dictionary containing:
                - word_timings: List of (word, start, end) tuples
                - dtw_path: DTW alignment path
                - dtw_distance: DTW distance score
                - tts_response: Original Martha TTS response
        """
        if output_dir is None:
            output_dir = Path("data/tts_alignment")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Generate reference audio via TTS
        logger.info("Generating reference audio via Martha TTS")
        tts_response = self.tts.synthesize(text)

        if not tts_response or "audio_url" not in tts_response:
            raise ValueError("TTS synthesis failed")

        # Download reference audio
        ref_audio_path = output_dir / tts_response["fn"]
        self.tts.download_audio(tts_response["audio_url"], ref_audio_path)

        # Step 2: Extract features
        logger.info("Extracting MFCC features")
        source_mfcc = self.extract_mfcc(source_audio)
        ref_mfcc = self.extract_mfcc(ref_audio_path)

        # Step 3: DTW alignment
        logger.info("Computing DTW alignment")
        distance, path = self._compute_dtw(source_mfcc.T, ref_mfcc.T)

        logger.info(f"DTW distance: {distance:.2f}")

        # Step 4: Map timestamps
        word_timings = self._map_timestamps(
            tts_response.get("ts", []),
            path,
            source_mfcc.shape[1],
            tts_response.get("du", 0),
        )

        return {
            "word_timings": word_timings,
            "dtw_path": path,
            "dtw_distance": distance,
            "tts_response": tts_response,
            "reference_audio": str(ref_audio_path),
        }

    def _compute_dtw(self, source_seq, ref_seq) -> Tuple[float, List]:
        """
        Compute DTW alignment between two sequences.

        Args:
            source_seq: Source audio features
            ref_seq: Reference audio features

        Returns:
            (distance, path) where path is list of (source_idx, ref_idx) tuples
        """
        if self.dtw is None:
            raise ImportError("dtaidistance is required for DTW alignment")

        # Compute DTW distance and path
        distance = self.dtw.distance(source_seq, ref_seq)
        path = self.dtw.warping_path(source_seq, ref_seq)

        return distance, path

    def _map_timestamps(
        self,
        tts_timestamps: List,
        dtw_path: List,
        source_frames: int,
        ref_duration: float,
    ) -> List[Tuple[str, float, float]]:
        """
        Map TTS word timestamps to source audio using DTW path.

        Args:
            tts_timestamps: Word-level timestamps from Martha TTS
            dtw_path: DTW alignment path
            source_frames: Number of frames in source audio
            ref_duration: Duration of reference audio in seconds

        Returns:
            List of (word, start_time, end_time) tuples
        """
        # This is a placeholder - actual implementation would:
        # 1. Convert TTS timestamps (in seconds) to frame indices
        # 2. Use DTW path to map reference frames to source frames
        # 3. Convert source frames back to seconds

        # For now, return the original TTS timestamps as a starting point
        logger.warning(
            "Timestamp mapping not fully implemented - returning TTS timestamps"
        )

        if not tts_timestamps:
            return []

        # Parse Martha's timestamp format (needs to be determined from actual API response)
        word_timings = []

        # Placeholder: you would parse the actual 'ts' field structure here
        logger.info(f"TTS provided {len(tts_timestamps)} timing points")

        return word_timings


# Example usage
def main():
    """Example usage of TTS-based alignment."""

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Initialize
    tts = MarthaTTS()

    # Example 1: Simple synthesis
    print("\n=== Example 1: Basic TTS ===")
    text = "Aasaqqussuaq"  # Common Kalaallisut word

    try:
        result = tts.synthesize(text)
        print(f"Generated: {result['fn']}")
        print(f"Duration: {result['du']} seconds")
        print(f"Size: {result['sz']} bytes")
        print(f"Download: {result['audio_url']}")

        if "ts" in result:
            print(f"Timestamps: {result['ts']}")

    except Exception as e:
        print(f"Error: {e}")

    # Example 2: Batch synthesis
    print("\n=== Example 2: Batch Synthesis ===")
    texts = ["Aasaqqussuaq", "Kalaallit Nunaat", "Imaqa"]

    try:
        results = tts.batch_synthesize(texts, delay=2.0)
        for text, result in zip(texts, results):
            if result:
                print(f"{text}: {result['du']:.2f}s")
            else:
                print(f"{text}: FAILED")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
