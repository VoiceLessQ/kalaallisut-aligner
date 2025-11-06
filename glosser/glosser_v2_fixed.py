#!/usr/bin/env python3
import sys, json
from pathlib import Path
from typing import List, Dict, Optional, Any

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from preprocessor import tokenize_text, analyze_word


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

        print(f"Loaded {len(self.kal_eng)} dictionary entries", file=sys.stderr)

    def gloss_morpheme(self, morpheme: str) -> str:
        if morpheme in self.glosses["tags"]:
            return self.glosses["tags"][morpheme]
        if morpheme in self.glosses["roots"]:
            return self.glosses["roots"][morpheme]
        if morpheme in self.kal_eng:
            return self.kal_eng[morpheme]
        return morpheme

    def translate_root(self, root: str) -> Optional[str]:
        if root in self.kal_eng:
            return self.kal_eng[root]
        for suffix in ["voq", "poq", "soq", "toq", "neq"]:
            if root.endswith(suffix):
                base = root[: -len(suffix)]
                if base in self.kal_eng:
                    return self.kal_eng[base]
        return None

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
                print(f"Warning: Failed to analyze '{token}': {e}", file=sys.stderr)
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
                print(f"Error: Input file not found: {args.input}", file=sys.stderr)
                return 1
            with open(args.input, encoding="utf-8") as f:
                text = f.read()
        else:
            text = sys.stdin.read()
    except IOError as e:
        print(f"Error reading input: {e}", file=sys.stderr)
        return 1
    except UnicodeDecodeError as e:
        print(f"Error: Invalid encoding in input file: {e}", file=sys.stderr)
        return 1

    if not text.strip():
        print("Error: Input text is empty", file=sys.stderr)
        return 1

    # Initialize glosser and process
    try:
        glosser = KalaallisutGlosser()
    except (FileNotFoundError, ValueError) as e:
        print(f"Error initializing glosser: {e}", file=sys.stderr)
        return 1

    try:
        glossed = glosser.gloss_text(text)
    except (ValueError, RuntimeError) as e:
        print(f"Error glossing text: {e}", file=sys.stderr)
        return 1

    output = glosser.output_text(glossed)

    # Write output
    try:
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Output written to: {args.output}", file=sys.stderr)
        else:
            print(output)
    except IOError as e:
        print(f"Error writing output: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
