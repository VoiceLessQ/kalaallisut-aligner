#!/usr/bin/env python3
"""
Central configuration for the Kalaallisut-Danish Aligner project.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Project configuration singleton."""

    _instance: Optional["Config"] = None
    _config: Dict[str, Any] = {}

    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self) -> None:
        """Load configuration from file or environment."""
        config_file = Path(__file__).parent.parent / "config.json"

        if config_file.exists():
            with open(config_file, encoding="utf-8") as f:
                self._config = json.load(f)
        else:
            # Default configuration
            self._config = self._get_default_config()

        # Override with environment variables
        self._apply_env_overrides()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "lang_kal_path": str(Path.home() / "lang-kal"),
            "hunalign_path": str(Path.home() / "hunalign/src/hunalign/hunalign"),
            "data_paths": {
                "raw": "data/raw",
                "processed": "data/processed",
                "aligned": "data/aligned",
                "test": "data/test",
            },
            "alignment": {
                "confidence_threshold": 0.5,
                "word_score_weight": 0.3,
                "char_score_weight": 0.2,
                "position_score_weight": 0.2,
                "lexical_score_weight": 0.3,
                "min_sentence_length": 5,
            },
            "cognates": {
                "min_word_length": 3,
                "max_edit_distance": 2,
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        }

    def _apply_env_overrides(self) -> None:
        """Override config with environment variables."""
        if "LANG_KAL_PATH" in os.environ:
            self._config["lang_kal_path"] = os.environ["LANG_KAL_PATH"]
        if "HUNALIGN_PATH" in os.environ:
            self._config["hunalign_path"] = os.environ["HUNALIGN_PATH"]

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation.

        Args:
            key: Configuration key (e.g., "alignment.word_score_weight")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    @property
    def lang_kal_root(self) -> Path:
        """Get lang-kal root directory."""
        return Path(self.get("lang_kal_path"))

    @property
    def tokenizer_path(self) -> Path:
        """Get tokenizer path."""
        return self.lang_kal_root / "tools/tokenisers/tokeniser-disamb-gt-desc.pmhfst"

    @property
    def analyzer_path(self) -> Path:
        """Get analyzer path."""
        return self.lang_kal_root / "src/fst/analyser-gt-desc.hfst"

    @property
    def hunalign_path(self) -> Path:
        """Get hunalign binary path."""
        return Path(self.get("hunalign_path"))

    @property
    def word_score_weight(self) -> float:
        """Get word score weight for alignment."""
        return float(self.get("alignment.word_score_weight", 0.4))

    @property
    def char_score_weight(self) -> float:
        """Get character score weight for alignment."""
        return float(self.get("alignment.char_score_weight", 0.3))

    @property
    def position_score_weight(self) -> float:
        """Get position score weight for alignment."""
        return float(self.get("alignment.position_score_weight", 0.3))

    @property
    def lexical_score_weight(self) -> float:
        """Get lexical/cognate score weight for alignment."""
        return float(self.get("alignment.lexical_score_weight", 0.3))

    @property
    def min_sentence_length(self) -> int:
        """Get minimum sentence length for splitting."""
        return int(self.get("alignment.min_sentence_length", 5))

    @property
    def confidence_threshold(self) -> float:
        """Get confidence threshold for alignments."""
        return float(self.get("alignment.confidence_threshold", 0.5))

    @property
    def min_cognate_length(self) -> int:
        """Get minimum word length for cognate extraction."""
        return int(self.get("cognates.min_word_length", 3))

    @property
    def max_edit_distance(self) -> int:
        """Get maximum edit distance for cognate matching."""
        return int(self.get("cognates.max_edit_distance", 2))


# Global config instance
config = Config()
