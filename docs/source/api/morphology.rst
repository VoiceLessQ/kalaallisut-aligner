Morphology Module
=================

.. automodule:: morphology
   :members:
   :undoc-members:
   :show-inheritance:

Functions
---------

.. autofunction:: morphology.tokenize_text

.. autofunction:: morphology.analyze_word

Overview
--------

The morphology module provides centralized HFST-based morphological analysis for Kalaallisut text.

Key features:

* Tokenization using lang-kal tokenizer
* Morphological analysis with word-level granularity
* Configurable paths via config module
* Error handling for missing tools

Example
-------

.. code-block:: python

   from morphology import tokenize_text, analyze_word

   # Tokenize text
   tokens = tokenize_text("Takussaanga")

   # Analyze word
   analyses = analyze_word("Takussaanga")
   for analysis in analyses:
       print(f"{analysis['surface']}: {analysis['analysis']}")
