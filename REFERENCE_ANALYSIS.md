# Reference Projects Analysis & Project To-Do List

**Date:** November 5, 2025
**Branch:** claude/analyze-language-references-011CUqTpEYZfnLhkJHJAPAFF

---

## 1. Reference Projects Analysis

### 1.1 lang-kal (https://github.com/giellalt/lang-kal)

**Type:** Finite State Transducer (FST) Morphological Analyzer
**License:** GPL-3.0 (alternative licensing available by negotiation)
**Maturity:** Production-grade (10,133+ commits, active maintenance)

#### Key Features:
- Comprehensive morphological analysis for Kalaallisut
- Spell-checking and proofing tools
- Constraint Grammar rules for grammatical analysis
- Multi-platform support (Windows, macOS, mobile)
- FST-based architecture for efficient processing

#### Integration Status in Our Project:
✅ **Currently Used:**
- Integrated via `hfst-tokenize` and `hfst-lookup` tools
- Referenced in `src/preprocessor.py` for morphological analysis
- Installation instructions in README.md

⚠️ **Issues:**
- Hardcoded path: `~/lang-kal/` (not flexible)
- No version checking or compatibility verification
- Missing error handling if lang-kal not installed

#### Recommendations:
1. Add environment variable support for lang-kal location
2. Implement version checking during setup
3. Add fallback behavior if lang-kal unavailable
4. Consider packaging as Docker container for easier deployment

---

### 1.2 hunalign (https://github.com/danielvarga/hunalign)

**Type:** Bilingual Sentence Alignment Tool
**License:** LGPL-3.0 or later
**Maturity:** Stable (widely used in corpus linguistics)

#### Key Features:
- Dictionary-based + Gale-Church sentence-length alignment
- Automatic dictionary construction mode
- Two-pass realignment for quality improvement
- UTF-8 support
- Confidence scoring for alignments
- Batch processing capabilities

#### Known Limitations:
- Cannot handle crossing alignments (A B → B' A')
- Best performance on corpora < 10,000 sentences (use partialAlign for larger)
- Requires pre-tokenization and sentence segmentation

#### Integration Status in Our Project:
✅ **Currently Used:**
- Primary alignment engine via `scripts/align_production.sh`
- Uses cognate dictionary from `data/processed/hunalign_dict_full.txt`
- 1,526 Danish-Kalaallisut cognate pairs

⚠️ **Issues:**
- Hardcoded path: `~/hunalign/src/hunalign/hunalign`
- No realignment option currently used (could improve quality)
- Limited threshold optimization

#### Recommendations:
1. Add `--realign` flag to improve alignment quality
2. Experiment with different threshold values (currently 50)
3. Implement batch processing for multiple file pairs
4. Add environment variable for hunalign location
5. Consider using partialAlign for large corpora

---

### 1.3 Oqaasileriffik (Greenland Language Secretariat)

**Type:** Governmental Language Authority
**License:** Various (dictionaries: CC-BY-SA 4.0)
**Website:** https://oqaasileriffik.gl/

#### Available Resources:

**1. Dictionary Resources:**
- **ordbog.gl**: Main dictionary website
- **Katersat**: Word database (Greenlandic/Danish/English)
- **2018 Chicago Dictionary**: Greenlandic-English (16,819+ entries)
  - Format: OpenDocument Spreadsheet
  - License: CC-BY-SA 4.0
  - GitHub: https://github.com/Oqaasileriffik/dicts

**2. Language Technology:**
- **Martha TTS**: Text-to-Speech API
  - Endpoint: https://oqaasileriffik.gl/martha/tts/
  - Example: `?t=oqaatsit&n=json`
  - Limit: 10,000 Unicode characters
- **kukkuniiaat**: Spell checker
- **Nutserut**: Greenlandic-Danish Machine Translation (https://nutserut.gl/en)

**3. GitHub Resources:**
- 17+ repositories with open-source language tools
- https://github.com/Oqaasileriffik

#### Integration Status in Our Project:
✅ **Currently Used:**
- Dictionary data in `glosser/kalaallisut_english_dict.json` (16,819 entries)
- Used for glossing and translation

⚠️ **Missing Opportunities:**
- Not using Martha TTS for pronunciation generation
- Not leveraging Katersat database
- Not using Nutserut MT system
- Dictionary may be outdated (need version tracking)

#### Recommendations:
1. Add Martha TTS integration for pronunciation in glosser
2. Implement dictionary update mechanism from Oqaasileriffik/dicts
3. Add version/date stamp to dictionary files
4. Consider integrating Nutserut MT for translation suggestions
5. Explore Katersat API if available

---

### 1.4 GiellaLT (Giella Infrastructure)

**Type:** Language Technology Infrastructure
**License:** Dual CC-BY-SA / GPL
**Website:** https://giellalt.github.io/
**GitHub:** https://github.com/giellalt

#### Key Features:
- Rule-based language technology for minority/indigenous languages
- Infrastructure for keyboards, proofing tools, speech technology
- Shared resources and standardized build systems
- Support for 100+ languages
- FST-based morphological analyzers
- Neahttadigisánit dictionary platform

#### Components:
- **Language Models**: FST transducers for morphology
- **Keyboards**: Virtual and physical keyboard layouts
- **Proofing Tools**: Spell-checkers, grammar checkers
- **Dictionaries**: Web-based dictionary platform
- **Build Infrastructure**: Autotools-based compilation

#### Integration Status in Our Project:
✅ **Currently Used:**
- lang-kal is part of GiellaLT infrastructure
- Using GiellaLT build system for lang-kal compilation

⚠️ **Missing Opportunities:**
- Not using GiellaLT shared resources
- Not leveraging standardized testing infrastructure
- Could benefit from GiellaLT keyboard layouts
- Missing citation to GiellaLT infrastructure paper (LREC 2022)

#### Recommendations:
1. Add proper citation to GiellaLT infrastructure
2. Explore shared resources for improved morphology
3. Consider using GiellaLT testing framework
4. Document GiellaLT dependency more clearly
5. Align with GiellaLT best practices

---

## 2. Current Project Assessment

### 2.1 Strengths
✅ Proper integration of lang-kal for morphology
✅ Effective use of hunalign with cognate dictionary
✅ Good dictionary coverage from Oqaasileriffik
✅ Clean architecture and documentation
✅ Production-ready alignment pipeline

### 2.2 Gaps Identified

**Licensing & Attribution:**
- ⚠️ Missing proper citations to reference papers
- ⚠️ License compatibility not fully documented
- ⚠️ Attribution to Oqaasileriffik incomplete

**Data & Resources:**
- ⚠️ Dictionary version not tracked
- ⚠️ Corpus count discrepancy (6,798 vs 6,813)
- ⚠️ Missing raw data in `data/raw/`
- ⚠️ No mechanism for dictionary updates

**Technical Integration:**
- ⚠️ Hardcoded paths for dependencies
- ⚠️ No version checking for external tools
- ⚠️ Limited error handling for missing dependencies
- ⚠️ No Docker/containerization support

**Features Not Utilized:**
- ❌ Martha TTS for pronunciation
- ❌ Nutserut MT integration
- ❌ hunalign realignment option
- ❌ GiellaLT shared resources
- ❌ Batch processing automation

---

## 3. Project To-Do List

### 3.1 CRITICAL (Fix Now)

**Documentation & Licensing:**
- [ ] Update corpus count in README (6,798 → 6,813)
- [ ] Add proper citations section to README
  - [ ] GiellaLT infrastructure paper (LREC 2022)
  - [ ] hunalign paper citation
  - [ ] Oqaasileriffik dictionary attribution with version
- [ ] Document license compatibility (GPL-3.0, LGPL-3.0, MIT, CC-BY-SA 4.0)
- [ ] Add CONTRIBUTORS.md acknowledging all sources
- [ ] Update LICENSE file to clarify derivative work constraints

**Code Quality:**
- [ ] Remove or deprecate `glosser/glosser.py` (keep only v2_fixed)
- [ ] Add version numbers to all Python modules
- [ ] Fix hardcoded paths in scripts
  - [ ] Add `LANG_KAL_PATH` environment variable
  - [ ] Add `HUNALIGN_PATH` environment variable
- [ ] Add dependency version checking to setup.sh

**Data Management:**
- [ ] Add version/date metadata to dictionary files
- [ ] Create `data/raw/README.md` explaining expected structure
- [ ] Add data provenance tracking (where each file came from)

---

### 3.2 HIGH PRIORITY (Next Sprint)

**Improved Integration:**
- [ ] Implement hunalign realignment option
  - [ ] Add `--realign` flag to align_production.sh
  - [ ] Test quality improvement on sample data
  - [ ] Document performance impact
- [ ] Add error handling for missing dependencies
  - [ ] Graceful fallback if lang-kal not found
  - [ ] Clear error messages with installation instructions
- [ ] Create requirements.txt for Python dependencies
  - [ ] pandas
  - [ ] odfpy
  - [ ] Add version constraints

**Feature Enhancements:**
- [ ] Integrate Martha TTS API for pronunciation
  - [ ] Add TTS option to glosser
  - [ ] Generate audio files for glossed text
  - [ ] Add pronunciation examples to HTML output
- [ ] Implement dictionary update mechanism
  - [ ] Script to fetch latest from Oqaasileriffik/dicts
  - [ ] Automatic conversion from ODS to JSON
  - [ ] Version comparison and update notifications
- [ ] Add batch processing scripts
  - [ ] Process multiple file pairs automatically
  - [ ] Progress reporting
  - [ ] Error handling and logging

**Testing:**
- [ ] Create test suite for core functions
  - [ ] Unit tests for preprocessor.py
  - [ ] Unit tests for aligner.py
  - [ ] Integration tests for alignment pipeline
- [ ] Add sample test data in `data/test/`
- [ ] Create CI/CD pipeline for automated testing
- [ ] Add regression tests for alignment quality

---

### 3.3 MEDIUM PRIORITY (Future Enhancements)

**Deployment & Portability:**
- [ ] Create Docker container for easy deployment
  - [ ] Include lang-kal pre-built
  - [ ] Include hunalign pre-built
  - [ ] All dependencies bundled
- [ ] Add docker-compose.yml for multi-service setup
- [ ] Create installation packages
  - [ ] .deb package for Debian/Ubuntu
  - [ ] Homebrew formula for macOS
- [ ] Add web interface
  - [ ] Flask/FastAPI backend
  - [ ] Simple HTML frontend
  - [ ] RESTful API for alignment/glossing

**Advanced Features:**
- [ ] Integrate Nutserut MT for translation suggestions
- [ ] Add neural alignment model option
  - [ ] Train BERT-based aligner on corpus
  - [ ] Compare with hunalign performance
- [ ] Implement quality estimation model
  - [ ] Predict alignment confidence without manual review
  - [ ] Filter low-quality alignments automatically
- [ ] Add support for other Greenlandic variants
  - [ ] East Greenlandic (Tunumiisut)
  - [ ] Polar Eskimo (Inuktun)

**Data Expansion:**
- [ ] Expand cognate dictionary
  - [ ] Use edit distance for near-cognates
  - [ ] Add morphological variants
  - [ ] Target 3,000+ entries
- [ ] Add more parallel corpora
  - [ ] Government documents
  - [ ] News articles
  - [ ] Educational materials
- [ ] Implement active learning
  - [ ] Identify uncertain alignments
  - [ ] Request manual review
  - [ ] Retrain with corrected data

---

### 3.4 LOW PRIORITY (Nice to Have)

**Documentation:**
- [ ] Create video tutorials
- [ ] Add Jupyter notebooks with examples
- [ ] Translate documentation to Danish
- [ ] Translate documentation to Kalaallisut
- [ ] Create academic paper describing the system

**Community & Collaboration:**
- [ ] Set up discussion forum or mailing list
- [ ] Create contribution guidelines
- [ ] Add issue templates to GitHub
- [ ] Establish code review process
- [ ] Set up monthly development meetings

**Research Integration:**
- [ ] Add export to common formats
  - [ ] TMX (Translation Memory eXchange)
  - [ ] XLIFF (XML Localization Interchange File Format)
  - [ ] Moses format for SMT
- [ ] Integrate with existing MT frameworks
  - [ ] OpenNMT
  - [ ] Marian NMT
  - [ ] Fairseq
- [ ] Add linguistic analysis tools
  - [ ] Word frequency analysis
  - [ ] Morphological complexity metrics
  - [ ] Translation divergence analysis

---

## 4. Resource Dependencies Summary

| Resource | License | Current Use | Integration Status | Next Steps |
|----------|---------|-------------|-------------------|------------|
| lang-kal | GPL-3.0 | Morphology | ✅ Active | Add version check, env var |
| hunalign | LGPL-3.0 | Alignment | ✅ Active | Add realignment, batch mode |
| Oqaasileriffik Dict | CC-BY-SA 4.0 | Glossing | ✅ Active | Add update mechanism, version tracking |
| Martha TTS | Unknown | None | ❌ Not used | Implement pronunciation feature |
| Nutserut MT | Unknown | None | ❌ Not used | Research integration possibility |
| GiellaLT Infrastructure | CC-BY-SA/GPL | Build system | ✅ Indirect | Add proper citation, explore shared resources |

---

## 5. Recommended Reading

**Academic Papers:**
1. GiellaLT Infrastructure Paper (LREC 2022) - for citation
2. hunalign original paper - for methodology understanding
3. Kalaallisut morphology papers - for linguistic background

**Documentation:**
- GiellaLT documentation: https://giellalt.github.io/
- lang-kal specific docs: https://github.com/giellalt/lang-kal
- hunalign manual: https://github.com/danielvarga/hunalign
- Oqaasileriffik resources: https://oqaasileriffik.gl/en/resources/

---

## 6. Priority Action Plan (Next 2 Weeks)

**Week 1:**
1. ✅ Complete reference analysis
2. Update documentation (corpus count, citations, license compatibility)
3. Remove deprecated glosser.py
4. Add environment variables for paths
5. Create requirements.txt
6. Add version checking to setup.sh

**Week 2:**
7. Implement hunalign realignment
8. Add error handling for missing dependencies
9. Create basic test suite
10. Implement dictionary update script
11. Add batch processing capability
12. Update README with new features

**Success Metrics:**
- All CRITICAL tasks completed
- At least 50% of HIGH PRIORITY tasks completed
- Test coverage > 60%
- Documentation up to date
- All license/attribution issues resolved

---

## 7. Long-term Vision

**Goal:** Make this the definitive open-source toolkit for Kalaallisut language technology

**Objectives:**
- Comprehensive coverage of Kalaallisut NLP tasks
- Easy-to-use for researchers and developers
- Well-documented and maintained
- Integrated with broader language technology ecosystem
- Active community of contributors
- Used in real-world applications (education, government, translation)

**Metrics for Success:**
- 100+ GitHub stars
- 10+ external contributors
- Used in at least 3 published research papers
- Adopted by Greenlandic institutions
- Integration with major MT platforms

---

**Analysis completed:** November 5, 2025
**Next review date:** November 19, 2025
**Maintained by:** VoiceLessQ
