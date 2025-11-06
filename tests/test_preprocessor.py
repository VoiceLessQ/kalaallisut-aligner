"""Tests for preprocessor module."""
import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from preprocessor import tokenize_text, analyze_word, process_sentence


class TestTokenizeText:
    """Tests for tokenize_text function."""

    def test_tokenize_empty_text(self):
        """Test error with empty text."""
        with pytest.raises(ValueError, match="Input text cannot be empty"):
            tokenize_text("")

    def test_tokenize_whitespace_only(self):
        """Test error with whitespace-only text."""
        with pytest.raises(ValueError, match="Input text cannot be empty"):
            tokenize_text("   \n\t  ")


class TestAnalyzeWord:
    """Tests for analyze_word function."""

    def test_analyze_empty_word(self):
        """Test error with empty word."""
        with pytest.raises(ValueError, match="Word cannot be empty"):
            analyze_word("")

    def test_analyze_whitespace_only(self):
        """Test error with whitespace-only word."""
        with pytest.raises(ValueError, match="Word cannot be empty"):
            analyze_word("   ")


class TestProcessSentence:
    """Tests for process_sentence function."""

    def test_process_empty_sentence(self):
        """Test error with empty sentence."""
        with pytest.raises(ValueError, match="Sentence cannot be empty"):
            process_sentence("")

    def test_process_whitespace_only(self):
        """Test error with whitespace-only sentence."""
        with pytest.raises(ValueError, match="Sentence cannot be empty"):
            process_sentence("   \n\t  ")


# Note: Full integration tests that actually call HFST tools are skipped
# unless the tools are available. Add markers for integration tests:

@pytest.mark.integration
@pytest.mark.skipif(
    not Path.home().joinpath("lang-kal/src/fst/analyser-gt-desc.hfst").exists(),
    reason="HFST tools not installed"
)
class TestIntegrationWithHFST:
    """Integration tests that require HFST tools to be installed."""

    def test_tokenize_kalaallisut_text(self):
        """Test tokenization of real Kalaallisut text."""
        result = tokenize_text("Takussaanga.")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_analyze_kalaallisut_word(self):
        """Test analysis of real Kalaallisut word."""
        result = analyze_word("takussaanga")
        assert isinstance(result, list)
        # May be empty for unknown words, but should not raise

    def test_process_kalaallisut_sentence(self):
        """Test processing of real Kalaallisut sentence."""
        result = process_sentence("Takussaanga.")
        assert isinstance(result, list)
        assert len(result) >= 0
