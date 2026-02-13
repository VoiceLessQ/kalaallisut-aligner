Preprocessor Module
===================

.. automodule:: preprocessor
   :members:
   :undoc-members:
   :show-inheritance:

Functions
---------

.. autofunction:: preprocessor.process_sentence

Overview
--------

The preprocessor module handles text preprocessing and sentence-level analysis.

Features:

* Tokenizes and analyzes sentences
* Skips punctuation and empty tokens
* Graceful error handling for analysis failures
* Returns structured token data

Example
-------

.. code-block:: python

   from preprocessor import process_sentence

   sentence = "Takussaanga Kalaallit Nunaat."
   result = process_sentence(sentence)

   for token_data in result:
       print(f"Token: {token_data['token']}")
       print(f"Analyses: {len(token_data['analyses'])}")
       print(f"Morphemes: {token_data['morpheme_count']}")
