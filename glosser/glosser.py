#!/usr/bin/env python3
"""
Full-text Kalaallisut glosser/annotator.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from preprocessor import tokenize_text, analyze_word


class KalaallisutGlosser:
    def __init__(self, glosses_file="morpheme_glosses.json"):
        """Initialize with morpheme dictionary."""
        glosses_path = Path(__file__).parent / glosses_file
        with open(glosses_path, "r", encoding="utf-8") as f:
            self.glosses = json.load(f)

    def gloss_morpheme(self, morpheme):
        """Get gloss for a single morpheme."""
        # Check if it's a root
        if morpheme in self.glosses["roots"]:
            return self.glosses["roots"][morpheme]

        # Check if it's a tag
        if morpheme in self.glosses["tags"]:
            return self.glosses["tags"][morpheme]

        # Unknown
        return morpheme

    def format_analysis(self, word, analysis):
        """Format a single analysis into glossed output."""
        parts = analysis["analysis"].split("+")

        root = parts[0]
        morphemes = parts[1:]

        # Build morpheme line
        morpheme_line = root
        if morphemes:
            morpheme_line += "-" + "-".join(morphemes)

        # Build gloss line
        gloss_parts = [self.gloss_morpheme(root)]
        gloss_parts.extend([self.gloss_morpheme(m) for m in morphemes])
        gloss_line = "-".join(gloss_parts)

        return {
            "surface": word,
            "morphemes": morpheme_line,
            "glosses": gloss_line,
            "raw_analysis": analysis["analysis"],
        }

    def gloss_text(self, text):
        """Gloss full text."""
        tokens = tokenize_text(text)

        glossed = []
        for token in tokens:
            # Skip punctuation-only tokens
            if token.strip() in ".,;:!?":
                glossed.append({"surface": token, "type": "punctuation"})
                continue

            analyses = analyze_word(token)

            if not analyses:
                glossed.append({"surface": token, "type": "unknown"})
            else:
                # Use first analysis (best)
                formatted = self.format_analysis(token, analyses[0])
                formatted["type"] = "word"
                formatted["all_analyses"] = len(analyses)
                glossed.append(formatted)

        return glossed

    def output_text(self, glossed_items):
        """Output in text format."""
        output = []
        output.append("═" * 60)

        for item in glossed_items:
            if item["type"] == "punctuation":
                output.append(f"\n{item['surface']}\n")
                output.append("─" * 60)
            elif item["type"] == "unknown":
                output.append(f"\n{item['surface']}")
                output.append("❌ UNKNOWN WORD")
                output.append("─" * 60)
            else:
                output.append(f"\n{item['surface']}")
                output.append(item["morphemes"])
                output.append(item["glosses"])
                if item["all_analyses"] > 1:
                    output.append(f"({item['all_analyses']} possible analyses)")
                output.append("─" * 60)

        return "\n".join(output)

    def output_json(self, glossed_items):
        """Output in JSON format."""
        return json.dumps(glossed_items, indent=2, ensure_ascii=False)

    def output_html(self, glossed_items):
        """Output in HTML format."""
        html = ['<html><head><meta charset="utf-8"><style>']
        html.append(
            """
            body { font-family: Arial, sans-serif; margin: 20px; }
            .word { margin: 15px 0; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
            .surface { font-size: 18px; font-weight: bold; color: #2c3e50; }
            .morphemes { color: #3498db; margin: 5px 0; }
            .glosses { color: #27ae60; margin: 5px 0; font-style: italic; }
            .unknown { background-color: #ffebee; }
            .punctuation { color: #999; }
        """
        )
        html.append("</style></head><body>")
        html.append("<h1>Kalaallisut Glossed Text</h1>")

        for item in glossed_items:
            if item["type"] == "punctuation":
                html.append(f'<span class="punctuation">{item["surface"]}</span>')
            elif item["type"] == "unknown":
                html.append(
                    f'<div class="word unknown"><div class="surface">{item["surface"]}</div><div>❌ Unknown</div></div>'
                )
            else:
                html.append(f'<div class="word">')
                html.append(f'<div class="surface">{item["surface"]}</div>')
                html.append(f'<div class="morphemes">{item["morphemes"]}</div>')
                html.append(f'<div class="glosses">{item["glosses"]}</div>')
                if item["all_analyses"] > 1:
                    html.append(
                        f'<div style="font-size:12px;color:#999;">({item["all_analyses"]} analyses)</div>'
                    )
                html.append("</div>")

        html.append("</body></html>")
        return "\n".join(html)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Gloss Kalaallisut text")
    parser.add_argument("input", nargs="?", help="Input file (or use stdin)")
    parser.add_argument(
        "-f",
        "--format",
        choices=["text", "json", "html"],
        default="text",
        help="Output format",
    )
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")

    args = parser.parse_args()

    # Read input
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        print("Enter Kalaallisut text (Ctrl+D when done):")
        text = sys.stdin.read()

    # Gloss
    print("Analyzing...", file=sys.stderr)
    glosser = KalaallisutGlosser()
    glossed = glosser.gloss_text(text)

    # Format output
    if args.format == "text":
        output = glosser.output_text(glossed)
    elif args.format == "json":
        output = glosser.output_json(glossed)
    else:  # html
        output = glosser.output_html(glossed)

    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Saved to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
