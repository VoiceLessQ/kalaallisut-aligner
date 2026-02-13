# Data Version Information

**Last Updated:** November 5, 2025

## Dictionaries

### Kalaallisut-English Dictionary
- **File:** `glosser/kalaallisut_english_dict.json`
- **Entries:** 16,819
- **Source:** Oqaasileriffik (Greenland Language Secretariat)
- **Original:** 2018 Chicago Greenlandic-English Dictionary
- **License:** CC-BY-SA 4.0
- **Repository:** https://github.com/Oqaasileriffik/dicts
- **Format:** JSON
- **Last Verified:** November 2025

### Morpheme Glosses
- **File:** `glosser/morpheme_glosses.json`
- **Source:** Custom compilation from GiellaLT lang-kal tags
- **Purpose:** Tag and morpheme translations
- **Last Updated:** November 2025

## Cognates

### Danish-Kalaallisut Cognate Dictionary
- **File:** `data/processed/cognates.json`
- **Entries:** 1,526 total
  - Word cognates: 785
  - Date/number cognates: 587
  - Other: 154
- **Source:** Automatically extracted from aligned corpus
- **Extraction Method:** Exact match + similarity-based detection
- **Last Generated:** November 2025

### hunalign Dictionary Format
- **File:** `data/processed/hunalign_dict_full.txt`
- **Format:** hunalign-compatible (word pairs, one per line)
- **Entries:** 1,526 (same as cognates.json)
- **Purpose:** Used by hunalign for alignment hints
- **Last Generated:** November 2025

## Aligned Corpus

### Main Training Corpus
- **File:** `data/aligned/corpus_6798_pairs.txt`
- **Actual Pairs:** 6,813 aligned sentence pairs
- **Format:** `Danish sentence @ Kalaallisut sentence`
- **Source:** Danish-Kalaallisut government documents
- **Quality:** 100% valid alignments (all contain @ separator)
- **Split:**
  - Training: ~80% (5,450 pairs)
  - Test: ~20% (1,363 pairs)
- **Encoding:** UTF-8
- **Last Verified:** November 2025

### Test Output
- **File:** `data/aligned/test_output.txt`
- **Purpose:** Sample alignment for quality testing
- **Size:** 100 sentence pairs
- **Last Generated:** November 2025

## Statistics

### Alignment Statistics
- **File:** `data/processed/alignment_stats.json`
- **Metrics:**
  - Word ratio (Danish/Kalaallisut): 1.3644
  - Character ratio (Danish/Kalaallisut): 0.7301
- **Purpose:** Used for alignment algorithm tuning
- **Source:** Computed from training corpus
- **Last Updated:** November 2025

## Update Procedures

### Updating Dictionary from Oqaasileriffik
```bash
# 1. Clone latest dictionary repository
git clone https://github.com/Oqaasileriffik/dicts
cd dicts/2018\ Chicago

# 2. Convert ODS to JSON (requires custom script)
python3 ../../scripts/convert_ods_to_json.py kalaallisut_english.ods

# 3. Update version information in this file
# Update entry count and date
```

### Regenerating Cognate Dictionary
```bash
# Extract cognates from aligned corpus
python3 scripts/extract_cognates.py

# This will update:
# - data/processed/cognates.json
# - data/processed/hunalign_dict_full.txt
```

### Recomputing Statistics
```bash
# Analyze corpus and update statistics
python3 scripts/compute_alignment_stats.py

# This will update:
# - data/processed/alignment_stats.json
```

## Data Provenance

| File | Original Source | License | Attribution Required |
|------|----------------|---------|---------------------|
| kalaallisut_english_dict.json | Oqaasileriffik/dicts | CC-BY-SA 4.0 | Yes |
| cognates.json | Derived from corpus | Same as corpus | No (auto-generated) |
| corpus_6798_pairs.txt | Government documents | Public domain | No |
| alignment_stats.json | Computed | N/A | No |

## Version History

- **v1.0 (November 2025)**: Initial data assembly
  - 16,819 dictionary entries
  - 6,813 aligned pairs
  - 1,526 cognate pairs

---

**Note:** Always verify data versions before research use. Contact maintainer for questions about data provenance or licensing.
