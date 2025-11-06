"""Tests for utility functions."""
import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import load_aligned_pairs, split_train_test, save_pairs


class TestLoadAlignedPairs:
    """Tests for load_aligned_pairs function."""

    def test_load_valid_pairs(self, temp_pairs_file):
        """Test loading valid aligned pairs from file."""
        pairs = load_aligned_pairs(temp_pairs_file)
        assert len(pairs) == 3
        assert pairs[0]["danish"] == "Hej verden"
        assert pairs[0]["kalaallisut"] == "Aluu silarsuaq"

    def test_load_nonexistent_file(self):
        """Test error when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_aligned_pairs("nonexistent_file.txt")

    def test_load_empty_file(self, tmp_path):
        """Test error when file is empty."""
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("")
        with pytest.raises(ValueError, match="No valid pairs found"):
            load_aligned_pairs(str(empty_file))

    def test_load_malformed_lines(self, tmp_path):
        """Test handling of malformed lines."""
        malformed_file = tmp_path / "malformed.txt"
        malformed_file.write_text("Danish @ Kalaallisut\nMalformed line\n@ No danish\n")
        pairs = load_aligned_pairs(str(malformed_file))
        assert len(pairs) == 1  # Only first line is valid

    def test_load_invalid_encoding(self, tmp_path):
        """Test error with invalid encoding."""
        invalid_file = tmp_path / "invalid.txt"
        invalid_file.write_bytes(b"\xff\xfe\xfd")
        with pytest.raises(ValueError, match="Invalid encoding"):
            load_aligned_pairs(str(invalid_file))


class TestSplitTrainTest:
    """Tests for split_train_test function."""

    def test_split_basic(self, sample_aligned_pairs):
        """Test basic train/test splitting."""
        train, test = split_train_test(sample_aligned_pairs, test_ratio=0.33, seed=42)
        assert len(train) + len(test) == len(sample_aligned_pairs)
        assert len(train) == 2
        assert len(test) == 1

    def test_split_reproducibility(self, sample_aligned_pairs):
        """Test that splitting is reproducible with same seed."""
        train1, test1 = split_train_test(sample_aligned_pairs, test_ratio=0.2, seed=42)
        train2, test2 = split_train_test(sample_aligned_pairs, test_ratio=0.2, seed=42)
        assert train1 == train2
        assert test1 == test2

    def test_split_empty_list(self):
        """Test error when splitting empty list."""
        with pytest.raises(ValueError, match="Cannot split empty pairs list"):
            split_train_test([])

    def test_split_invalid_ratio(self, sample_aligned_pairs):
        """Test error with invalid test ratio."""
        with pytest.raises(ValueError, match="test_ratio must be between 0 and 1"):
            split_train_test(sample_aligned_pairs, test_ratio=1.5)

        with pytest.raises(ValueError, match="test_ratio must be between 0 and 1"):
            split_train_test(sample_aligned_pairs, test_ratio=0.0)

    def test_split_single_pair(self):
        """Test error when trying to split single pair."""
        with pytest.raises(ValueError, match="Need at least 2 pairs"):
            split_train_test([{"danish": "test", "kalaallisut": "test"}])

    def test_split_ensures_both_sets(self):
        """Test that both train and test sets have at least one item."""
        pairs = [{"danish": f"da{i}", "kalaallisut": f"kal{i}"} for i in range(100)]
        train, test = split_train_test(pairs, test_ratio=0.01, seed=42)
        assert len(train) >= 1
        assert len(test) >= 1


class TestSavePairs:
    """Tests for save_pairs function."""

    def test_save_valid_pairs(self, tmp_path, sample_aligned_pairs):
        """Test saving valid pairs to file."""
        output_file = tmp_path / "output.txt"
        save_pairs(sample_aligned_pairs, str(output_file))

        assert output_file.exists()
        with open(output_file, encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) == 3
        assert "Hej verden @ Aluu silarsuaq" in lines[0]

    def test_save_creates_directory(self, tmp_path, sample_aligned_pairs):
        """Test that save_pairs creates parent directory if needed."""
        output_file = tmp_path / "subdir" / "output.txt"
        save_pairs(sample_aligned_pairs, str(output_file))
        assert output_file.exists()

    def test_save_empty_pairs(self, tmp_path):
        """Test error when saving empty pairs list."""
        with pytest.raises(ValueError, match="Cannot save empty pairs list"):
            save_pairs([], str(tmp_path / "output.txt"))

    def test_save_invalid_pair_format(self, tmp_path):
        """Test error with invalid pair format."""
        invalid_pairs = [{"danish": "test"}]  # Missing 'kalaallisut' key
        with pytest.raises(ValueError, match="Invalid pair format"):
            save_pairs(invalid_pairs, str(tmp_path / "output.txt"))
