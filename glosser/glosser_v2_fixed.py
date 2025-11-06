#!/usr/bin/env python3
import sys, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from preprocessor import tokenize_text, analyze_word


class KalaallisutGlosser:
    def __init__(self, dict_file="kalaallisut_english_dict.json"):
        dict_path = Path(__file__).parent / dict_file
        with open(dict_path, "r", encoding="utf-8") as f:
            self.kal_eng = json.load(f)
        with open(Path(__file__).parent / "morpheme_glosses.json", "r") as f:
            self.glosses = json.load(f)
        print(f"Loaded {len(self.kal_eng)} dictionary entries", file=sys.stderr)

    def gloss_morpheme(self, morpheme):
        if morpheme in self.glosses["tags"]:
            return self.glosses["tags"][morpheme]
        if morpheme in self.glosses["roots"]:
            return self.glosses["roots"][morpheme]
        if morpheme in self.kal_eng:
            return self.kal_eng[morpheme]
        return morpheme

    def translate_root(self, root):
        if root in self.kal_eng:
            return self.kal_eng[root]
        for suffix in ["voq", "poq", "soq", "toq", "neq"]:
            if root.endswith(suffix):
                base = root[: -len(suffix)]
                if base in self.kal_eng:
                    return self.kal_eng[base]
        return None

    def format_analysis(self, word, analysis):
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

    def gloss_text(self, text):
        tokens = tokenize_text(text)
        glossed = []
        for token in tokens:
            if token.strip() in ".,;:!?":
                glossed.append({"surface": token, "type": "punctuation"})
                continue

            analyses = analyze_word(token)
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

    def output_text(self, glossed_items):
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


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?")
    parser.add_argument("-f", "--format", choices=["text", "html"], default="text")
    parser.add_argument("-o", "--output")
    args = parser.parse_args()

    text = open(args.input, encoding="utf-8").read() if args.input else sys.stdin.read()

    glosser = KalaallisutGlosser()
    glossed = glosser.gloss_text(text)
    output = glosser.output_text(glossed)

    if args.output:
        open(args.output, "w", encoding="utf-8").write(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
