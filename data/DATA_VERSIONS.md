# Data Versions

Last updated: November 2025

## Dictionaries

**Kalaallisut-English** (`glosser/kalaallisut_english_dict.json`)
16,819 entries from the 2018 Chicago Greenlandic-English Dictionary via [Oqaasileriffik](https://github.com/Oqaasileriffik/dicts). CC-BY-SA 4.0.

**Morpheme glosses** (`glosser/morpheme_glosses.json`)
Tag translations compiled from GiellaLT lang-kal.

## Cognates

**Danish-Kalaallisut** (`data/processed/cognates.json`)
1,526 pairs (785 word cognates, 587 date/number cognates, 154 other). Auto-extracted from the aligned corpus.

Also in hunalign format: `data/processed/hunalign_dict_full.txt`

## Aligned corpus

**Training** (`data/processed/train.txt`) -- 8,178 pairs, format: `Danish @ Kalaallisut`
**Test** (`data/processed/test.txt`) -- 1,362 pairs
Source: government documents + news corpus.

**Statistics** (`data/processed/alignment_stats.json`)
Word ratio (DA/KL): 1.553, char ratio: 0.796

## Regenerating

```bash
python3 scripts/extract_cognates.py          # cognates + hunalign dict
python3 scripts/calculate_stats_fast.py      # alignment stats
```

## Provenance

| File | Source | License |
|------|--------|---------|
| kalaallisut_english_dict.json | Oqaasileriffik | CC-BY-SA 4.0 |
| cognates.json | auto-generated | -- |
| aligned corpus | government docs | public domain |
