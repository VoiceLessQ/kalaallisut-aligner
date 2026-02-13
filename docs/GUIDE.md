# User Guide

## Aligning documents

Prepare your input files: one sentence per line, UTF-8. Ideally both files have roughly the same number of sentences (hunalign handles mismatches, but it works best when they're close).

```bash
./scripts/align_production.sh danish.txt kal.txt > output.txt
```

Each line of output is: `danish \t kalaallisut \t score`

Filter for quality:

```bash
awk -F'\t' '$3 > 0.5' output.txt > good.txt
```

Convert to training format:

```bash
awk -F'\t' '{print $1 " @ " $2}' good.txt > pairs.txt
```

## Glossing

Interactive:

```bash
cd glosser
python3 glosser_v2_fixed.py
# type text, Ctrl+D when done
```

Batch:

```bash
for f in input/*.txt; do
    python3 glosser_v2_fixed.py "$f" -f html -o "output/$(basename "${f%.txt}").html"
done
```

## Troubleshooting

**hunalign not found** -- build it from source:

```bash
cd ~
git clone https://github.com/danielvarga/hunalign.git
cd hunalign/src/hunalign
make
```

**Morphology not working** -- rebuild lang-kal:

```bash
cd ~/lang-kal
make clean && make
```

**Dictionary missing** -- regenerate:

```bash
python3 scripts/extract_cognates.py
```
