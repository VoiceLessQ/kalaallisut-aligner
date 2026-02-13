#!/usr/bin/env python3
import sys
import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import List, Dict, Optional, Any

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from morphology import tokenize_text, analyze_word

# Set up logging
logger = logging.getLogger(__name__)


class KalaallisutGlosser:
    def __init__(self, dict_file: str = "kalaallisut_english_dict.json") -> None:
        """Initialize glosser with dictionary and morpheme gloss files.

        Args:
            dict_file: Name of dictionary JSON file

        Raises:
            FileNotFoundError: If dictionary files don't exist
            ValueError: If JSON files are invalid
        """
        dict_path = Path(__file__).parent / dict_file
        morpheme_path = Path(__file__).parent / "morpheme_glosses.json"

        if not dict_path.exists():
            raise FileNotFoundError(
                f"Dictionary not found: {dict_path}\n"
                f"Ensure {dict_file} exists in glosser/ directory"
            )

        if not morpheme_path.exists():
            raise FileNotFoundError(
                f"Morpheme glosses not found: {morpheme_path}\n"
                f"Ensure morpheme_glosses.json exists in glosser/ directory"
            )

        try:
            with open(dict_path, "r", encoding="utf-8") as f:
                self.kal_eng = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {dict_path}: {e}")

        try:
            with open(morpheme_path, "r") as f:
                self.glosses = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {morpheme_path}: {e}")

        # Validate structure
        if not isinstance(self.kal_eng, dict):
            raise ValueError(
                f"Dictionary must be a JSON object, got {type(self.kal_eng)}"
            )

        if "tags" not in self.glosses or "roots" not in self.glosses:
            raise ValueError("morpheme_glosses.json must have 'tags' and 'roots' keys")

        # Initialize caches for performance
        self._gloss_cache: Dict[str, str] = {}
        self._translate_cache: Dict[str, Optional[str]] = {}

        logger.info(f"Loaded {len(self.kal_eng)} dictionary entries")

    def gloss_morpheme(self, morpheme: str) -> str:
        # Check cache first
        if morpheme in self._gloss_cache:
            return self._gloss_cache[morpheme]

        # Lookup and cache result
        if morpheme in self.glosses["tags"]:
            result = self.glosses["tags"][morpheme]
        elif morpheme in self.glosses["roots"]:
            result = self.glosses["roots"][morpheme]
        elif morpheme in self.kal_eng:
            result = self.kal_eng[morpheme]
        else:
            result = morpheme

        self._gloss_cache[morpheme] = result
        return result

    def translate_root(self, root: str) -> Optional[str]:
        # Check cache first
        if root in self._translate_cache:
            return self._translate_cache[root]

        # Lookup and cache result
        result = None
        if root in self.kal_eng:
            result = self.kal_eng[root]
        else:
            for suffix in ["voq", "poq", "soq", "toq", "neq"]:
                if root.endswith(suffix):
                    base = root[: -len(suffix)]
                    if base in self.kal_eng:
                        result = self.kal_eng[base]
                        break

        self._translate_cache[root] = result
        return result

    def format_analysis(self, word: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        parts = analysis["analysis"].split("+")
        root, morphemes = parts[0], parts[1:]
        morpheme_line = root + ("-" + "-".join(morphemes) if morphemes else "")
        root_gloss = self.translate_root(root) or self.gloss_morpheme(root)
        gloss_parts = [root_gloss] + [self.gloss_morpheme(m) for m in morphemes]
        return {
            "surface": word,
            "morphemes": morpheme_line,
            "glosses": "-".join(gloss_parts),
            "translation": self.kal_eng.get(word),
            "raw_analysis": analysis["analysis"],
        }

    def gloss_text(self, text: str) -> List[Dict[str, Any]]:
        """Gloss Kalaallisut text with morphological analysis.

        Args:
            text: Input Kalaallisut text

        Returns:
            List of glossed token dictionaries

        Raises:
            ValueError: If text is empty
            RuntimeError: If tokenization or analysis fails
        """
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")

        try:
            tokens = tokenize_text(text)
        except (RuntimeError, ValueError) as e:
            raise RuntimeError(f"Tokenization failed: {e}")

        glossed = []
        for token in tokens:
            if token.strip() in ".,;:!?":
                glossed.append({"surface": token, "type": "punctuation"})
                continue

            try:
                analyses = analyze_word(token)
            except ValueError:
                # Empty token, skip
                continue
            except RuntimeError as e:
                # Analysis failed, treat as unknown
                logger.warning(f"Failed to analyze '{token}': {e}")
                analyses = []

            if not analyses:
                glossed.append(
                    {
                        "surface": token,
                        "type": "unknown" if token not in self.kal_eng else "word",
                        "translation": self.kal_eng.get(token),
                    }
                )
            else:
                # Find analysis with known root
                best = analyses[0]
                for a in analyses:
                    if a["analysis"].split("+")[0] in self.kal_eng:
                        best = a
                        break
                # Otherwise pick shortest
                if best == analyses[0] and len(analyses) > 1:
                    best = min(analyses, key=lambda a: len(a["analysis"].split("+")))

                formatted = self.format_analysis(token, best)
                formatted["type"] = "word"
                formatted["all_analyses"] = len(analyses)
                glossed.append(formatted)
        return glossed

    def output_text(self, glossed_items: List[Dict[str, Any]]) -> str:
        output = ["═" * 70]
        for item in glossed_items:
            if item["type"] == "punctuation":
                output.extend([f"\n{item['surface']}\n", "─" * 70])
            elif item["type"] == "unknown":
                output.extend([f"\n{item['surface']}", "❌ UNKNOWN", "─" * 70])
            else:
                output.append(f"\n{item['surface']}")
                if "morphemes" in item:
                    output.extend([item["morphemes"], item["glosses"]])
                if item.get("translation"):
                    output.append(f'💡 "{item["translation"]}"')
                if item.get("all_analyses", 0) > 1:
                    output.append(f"({item['all_analyses']} analyses)")
                output.append("─" * 70)
        return "\n".join(output)


def main() -> int:
    """Main entry point for glosser CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Gloss Kalaallisut text with morphological analysis",
        epilog="Example: python glosser_v2_fixed.py input.txt -o output.txt",
    )
    parser.add_argument("input", nargs="?", help="Input file (default: stdin)")
    parser.add_argument(
        "-f", "--format", choices=["text", "html"], default="text", help="Output format"
    )
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    args = parser.parse_args()

    # Read input
    try:
        if args.input:
            input_path = Path(args.input)
            if not input_path.exists():
                logger.error(f"Input file not found: {args.input}")
                return 1
            with open(args.input, encoding="utf-8") as f:
                text = f.read()
        else:
            text = sys.stdin.read()
    except IOError as e:
        logger.error(f"Error reading input: {e}")
        return 1
    except UnicodeDecodeError as e:
        logger.error(f"Invalid encoding in input file: {e}")
        return 1

    if not text.strip():
        logger.error("Input text is empty")
        return 1

    # Initialize glosser and process
    try:
        glosser = KalaallisutGlosser()
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Error initializing glosser: {e}")
        return 1

    try:
        glossed = glosser.gloss_text(text)
    except (ValueError, RuntimeError) as e:
        logger.error(f"Error glossing text: {e}")
        return 1

    output = glosser.output_text(glossed)

    # Write output
    try:
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            logger.info(f"Output written to: {args.output}")
        else:
            print(output)
    except IOError as e:
        logger.error(f"Error writing output: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
