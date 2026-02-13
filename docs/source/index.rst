Kalaallisut-Danish Sentence Aligner Documentation
=================================================

Complete NLP toolkit for Kalaallisut language processing and Danish-Kalaallisut parallel corpus alignment.

.. image:: https://github.com/VoiceLessQ/kalaallisut-aligner/actions/workflows/test.yml/badge.svg
   :target: https://github.com/VoiceLessQ/kalaallisut-aligner/actions/workflows/test.yml
   :alt: Test Status

Features
--------

* **Morphological Analyzer** - Full Kalaallisut morphology using lang-kal/GiellaLT
* **Sentence Aligner** - hunalign-based alignment with cognate dictionary (34.7% high-confidence)
* **Glosser** - Morpheme-by-morpheme analysis with 16,819 dictionary entries
* **Cognate Extractor** - 1,526 Danish-Kalaallisut shared terms

Dataset
-------

* **6,812 aligned sentence pairs** (5,450 train / 1,362 test)
* Extracted from parallel Danish-Kalaallisut government documents
* Smart date-aware sentence splitting
* Avg word ratio: 1.36 (Danish/Kalaallisut)

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   # Install dependencies
   sudo apt install build-essential git make hunalign
   pip3 install -r requirements.txt

   # Install lang-kal (morphological analyzer)
   cd ~
   git clone https://github.com/giellalt/lang-kal.git
   cd lang-kal
   ./autogen.sh
   ./configure --disable-syntax --enable-tokenisers --enable-analysers
   make

Usage Examples
~~~~~~~~~~~~~~

**Align Documents:**

.. code-block:: bash

   ./scripts/align_production.sh danish.txt kalaallisut.txt > output.txt

**Gloss Kalaallisut Text:**

.. code-block:: python

   from glosser_v2_fixed import KalaallisutGlosser

   glosser = KalaallisutGlosser()
   result = glosser.gloss_text("Takussaanga")
   print(glosser.output_text(result))

**Python API:**

.. code-block:: python

   from aligner import SentenceAligner

   aligner = SentenceAligner()
   alignments = aligner.align_documents(danish_text, kal_text)
   aligner.save_alignments(alignments, "output.txt")

Configuration
-------------

Create a ``config.json`` file in the project root:

.. code-block:: json

   {
     "lang_kal_path": "~/lang-kal",
     "hunalign_path": "~/hunalign/src/hunalign/hunalign",
     "alignment": {
       "word_score_weight": 0.4,
       "char_score_weight": 0.3,
       "position_score_weight": 0.3
     }
   }

See :doc:`configuration` for all options.

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   configuration
   examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/morphology
   api/preprocessor
   api/aligner
   api/utils
   api/glosser
   api/config

.. toctree::
   :maxdepth: 1
   :caption: Development

   contributing
   testing
   changelog

Performance
-----------

**Alignment Quality** (100 sentence test):

* Average confidence: 0.481
* High confidence (>0.5): 34.7%
* Very high (>1.0): 13.9%

**Glosser Coverage**:

* 16,819 dictionary entries
* Morphological analysis using lang-kal FST
* HTML/text/JSON output formats

Code Quality
------------

* ✅ Type hints (100% coverage)
* ✅ Comprehensive testing (41 unit tests, CI/CD)
* ✅ Error handling & validation
* ✅ Performance optimized (O(n) algorithms, caching)
* ✅ Centralized configuration
* ✅ Modular design

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
