# Kalaallisut-Danish Sentence Aligner

[![Test](https://github.com/VoiceLessQ/kalaallisut-aligner/actions/workflows/test.yml/badge.svg)](https://github.com/VoiceLessQ/kalaallisut-aligner/actions/workflows/test.yml)

Aligns Danish and Kalaallisut (West Greenlandic) parallel text. Also does morphological analysis and glossing.

Still early -- alignment confidence averages around 48%, with about a third of pairs scoring above 0.5. Good enough to be useful, lots of room to improve.

Includes a sentence aligner (hunalign + cognate dictionary), a morphological analyzer (lang-kal/GiellaLT HFST), a glosser with ~17k dictionary entries from Oqaasileriffik, and a cognate extractor (~1,500 Danish-Kalaallisut pairs). Training data is ~8k aligned sentence pairs from government docs and news.

## Setup

```bash
sudo apt install build-essential git make hunalign
pip3 install -r requirements.txt

# lang-kal (morphological analyzer)
cd ~
git clone https://github.com/giellalt/lang-kal.git
cd lang-kal
./autogen.sh
./configure --disable-syntax --enable-tokenisers --enable-analysers
make
```

Then:

```bash
git clone https://github.com/VoiceLessQ/kalaallisut-aligner.git
cd kalaallisut-aligner
chmod +x scripts/*.sh
```

If lang-kal or hunalign aren't in the default locations, set `LANG_KAL_PATH` / `HUNALIGN_PATH` env vars, or use a `config.json` (copy `config.json.example`).

## Usage

Align two documents:

```bash
./scripts/align_production.sh danish.txt kalaallisut.txt > aligned.txt

# keep only decent pairs
awk -F'\t' '$3 > 0.5' aligned.txt > good.txt
```

Or from Python:

```python
from src.aligner import SentenceAligner

aligner = SentenceAligner('data/processed/alignment_stats.json')
for a in aligner.align_documents(danish_text, kal_text):
    print(f"{a['confidence']:.2f}  {a['danish']}  ---  {a['kalaallisut']}")
```

Gloss Kalaallisut text:

```bash
cd glosser
python3 glosser_v2_fixed.py              # interactive
python3 glosser_v2_fixed.py input.txt -f html -o output.html
```

Add more training data (expects `DA:/KL:/CONF:` format):

```bash
python3 scripts/append_parallel_corpus.py
python3 scripts/calculate_stats_fast.py
```

## Layout

```
src/            aligner, preprocessor, morphology, config, utils
glosser/        glosser + dictionaries
scripts/        CLI tools, shell scripts
data/           training data, cognates, alignment stats
tests/          45 pytest tests
examples/       example scripts
docs/           TTS alignment docs, user guide
```

## Tests

```bash
pytest tests/ -v
```

HFST integration tests are marked and skipped if the tools aren't installed.

## Dependencies and licenses

- [lang-kal](https://github.com/giellalt/lang-kal) -- GPL-3.0
- [hunalign](https://github.com/danielvarga/hunalign) -- LGPL-3.0
- [Oqaasileriffik dictionary](https://oqaasileriffik.gl/) -- CC-BY-SA 4.0

Code in this repo is MIT.

## Thanks

Oqaasileriffik for the dictionary, GiellaLT/Divvun for lang-kal, Daniel Varga for hunalign.
