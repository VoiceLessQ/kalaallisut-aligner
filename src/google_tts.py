"""
Google Translate TTS wrapper for Kalaallisut.

Provides a simple interface to Google Translate's text-to-speech API
as an alternative to Martha TTS for audio transcription.

Note: This is an unofficial API and may be rate-limited or blocked.
Use responsibly.
"""

import requests
import logging
from typing import Optional, Dict
from pathlib import Path
import urllib.parse
import hashlib
import time

logger = logging.getLogger(__name__)


class GoogleKalaallisutTTS:
    """
    Google Translate TTS client for Kalaallisut.

    Uses Google Translate's unofficial TTS API to generate
    Kalaallisut speech from text.

    Warning: This is an unofficial API. For production use,
    consider self-hosting Martha TTS or using official APIs.
    """

    def __init__(self):
        """Initialize Google TTS client."""
        self.base_url = "https://translate.google.com/translate_tts"
        self.language = "kl"  # Kalaallisut language code
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://translate.google.com/",
            }
        )

    def synthesize(self, text: str, timeout: int = 30) -> Optional[Dict]:
        """
        Synthesize Kalaallisut text to speech using Google TTS.

        Args:
            text: Kalaallisut text to synthesize
            timeout: Request timeout in seconds

        Returns:
            Dictionary containing:
                - audio_data: Raw MP3 audio bytes
                - text: Original text
                - hash: MD5 hash of text (for caching)
                - size: Audio size in bytes

        Raises:
            requests.RequestException: If API call fails
        """
        try:
            logger.info(f"Sending Google TTS request for {len(text)} characters")

            # Google TTS parameters
            params = {
                "ie": "UTF-8",
                "q": text,
                "tl": self.language,
                "client": "tw-ob",  # Client identifier
            }

            response = self.session.get(
                self.base_url, params=params, timeout=timeout, allow_redirects=True
            )
            response.raise_for_status()

            # Check if we got audio or an error page
            content_type = response.headers.get("Content-Type", "")

            if "audio" not in content_type and "mpeg" not in content_type:
                # Got HTML error page instead of audio
                logger.error(f"Google TTS returned non-audio response: {content_type}")
                logger.error(f"Response preview: {response.text[:200]}")
                raise ValueError("Google TTS returned non-audio response")

            audio_data = response.content

            if len(audio_data) < 1000:
                # Audio file too small, probably an error
                logger.warning(
                    f"Google TTS returned suspiciously small audio: {len(audio_data)} bytes"
                )

            # Create response dict similar to Martha TTS format
            result = {
                "audio_data": audio_data,
                "text": text,
                "hash": hashlib.md5(text.encode()).hexdigest(),
                "size": len(audio_data),
            }

            logger.info(f"Google TTS successful: {len(audio_data)} bytes")
            return result

        except requests.Timeout:
            logger.error(f"Google TTS request timed out after {timeout}s")
            raise
        except requests.RequestException as e:
            logger.error(f"Google TTS API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Google TTS failed: {e}")
            raise

    def synthesize_to_file(
        self, text: str, output_path: Path, timeout: int = 30
    ) -> Path:
        """
        Synthesize text and save directly to file.

        Args:
            text: Kalaallisut text to synthesize
            output_path: Where to save the MP3 file
            timeout: Request timeout in seconds

        Returns:
            Path to saved audio file
        """
        result = self.synthesize(text, timeout=timeout)

        # Save audio data to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(result["audio_data"])

        logger.info(f"Audio saved to {output_path}")
        return output_path

    def batch_synthesize(
        self, texts: list[str], delay: float = 2.0
    ) -> list[Optional[Dict]]:
        """
        Synthesize multiple texts with rate limiting.

        Args:
            texts: List of Kalaallisut texts
            delay: Delay between requests (seconds) to avoid rate limiting

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

            # Rate limiting - be respectful
            if i < len(texts) - 1:
                time.sleep(delay)

        return results


# Example usage
def main():
    """Example usage of Google TTS for Kalaallisut."""
    import logging

    logging.basicConfig(level=logging.INFO)

    tts = GoogleKalaallisutTTS()

    # Example 1: Simple synthesis
    print("\n=== Example 1: Basic TTS ===")
    text = "Aasaqqussuaq"

    try:
        result = tts.synthesize(text)
        print(f"Text: {result['text']}")
        print(f"Size: {result['size']} bytes")
        print(f"Hash: {result['hash']}")

        # Save to file
        output_path = Path("/tmp/test_google_tts.mp3")
        output_path.write_bytes(result["audio_data"])
        print(f"Saved to: {output_path}")

    except Exception as e:
        print(f"Error: {e}")

    # Example 2: Direct to file
    print("\n=== Example 2: Direct to File ===")
    texts = ["Kalaallit Nunaat", "Imaqa", "Takussaanga"]

    for i, text in enumerate(texts):
        try:
            output = Path(f"/tmp/kalaallisut_{i}.mp3")
            tts.synthesize_to_file(text, output)
            print(f"✓ {text} → {output}")
        except Exception as e:
            print(f"✗ {text}: {e}")

        # Rate limiting
        time.sleep(2)


if __name__ == "__main__":
    main()
