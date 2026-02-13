"""Pytest configuration and shared fixtures."""
import pytest
from pathlib import Path
import json


@pytest.fixture
def sample_kal_text():
    """Sample Kalaallisut text for testing."""
    return "Takussaanga. Inuit Kalaallit Nunaat."


@pytest.fixture
def sample_danish_text():
    """Sample Danish text for testing."""
    return "Hej verden. Dette er en test."


@pytest.fixture
def sample_aligned_pairs():
    """Sample aligned pairs for testing."""
    return [
        {"danish": "Hej verden", "kalaallisut": "Aluu silarsuaq"},
        {"danish": "God dag", "kalaallisut": "Kutaa"},
        {"danish": "Hvordan går det?", "kalaallisut": "Qanoq ippit?"},
    ]


@pytest.fixture
def temp_cognates_file(tmp_path):
    """Create a temporary cognates file for testing."""
    cognates_file = tmp_path / "cognates.json"
    cognates = {
        "budget": "budget",
        "politik": "politikkikkut",
        "grønland": "kalaallit",
        "parlament": "inatsisartut",
    }
    cognates_file.write_text(json.dumps(cognates))
    return str(cognates_file)


@pytest.fixture
def temp_stats_file(tmp_path):
    """Create a temporary stats file for testing."""
    stats_file = tmp_path / "stats.json"
    stats = {"avg_word_ratio": 1.48, "avg_char_ratio": 0.75}
    stats_file.write_text(json.dumps(stats))
    return str(stats_file)


@pytest.fixture
def temp_pairs_file(tmp_path, sample_aligned_pairs):
    """Create a temporary aligned pairs file for testing."""
    pairs_file = tmp_path / "pairs.txt"
    with open(pairs_file, "w", encoding="utf-8") as f:
        for pair in sample_aligned_pairs:
            f.write(f"{pair['danish']} @ {pair['kalaallisut']}\n")
    return str(pairs_file)
