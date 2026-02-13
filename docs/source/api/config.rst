Config Module
=============

.. automodule:: config
   :members:
   :undoc-members:
   :show-inheritance:

Config Class
------------

.. autoclass:: config.Config
   :members:
   :undoc-members:
   :show-inheritance:

   Properties:
      * ``lang_kal_root`` - Path to lang-kal installation
      * ``tokenizer_path`` - Path to HFST tokenizer
      * ``analyzer_path`` - Path to HFST analyzer
      * ``hunalign_path`` - Path to hunalign binary
      * ``word_score_weight`` - Alignment word score weight (default: 0.4)
      * ``char_score_weight`` - Alignment char score weight (default: 0.3)
      * ``position_score_weight`` - Alignment position score weight (default: 0.3)
      * ``min_sentence_length`` - Minimum sentence length (default: 5)
      * ``confidence_threshold`` - Alignment confidence threshold (default: 0.5)
      * ``min_cognate_length`` - Minimum word length for cognates (default: 3)
      * ``max_edit_distance`` - Maximum edit distance for cognates (default: 2)

Overview
--------

Centralized configuration management using singleton pattern.

Configuration sources (priority order):

1. Environment variables (``LANG_KAL_PATH``, ``HUNALIGN_PATH``)
2. ``config.json`` file in project root
3. Default values

Example
-------

.. code-block:: python

   from config import config

   # Access configuration
   print(f"Tokenizer: {config.tokenizer_path}")
   print(f"Word weight: {config.word_score_weight}")

   # Get custom values with dot notation
   value = config.get("alignment.word_score_weight", default=0.4)

Configuration File
------------------

Create ``config.json`` in project root:

.. code-block:: json

   {
     "lang_kal_path": "~/lang-kal",
     "hunalign_path": "~/hunalign/src/hunalign/hunalign",
     "alignment": {
       "word_score_weight": 0.4,
       "char_score_weight": 0.3,
       "position_score_weight": 0.3,
       "min_sentence_length": 5
     },
     "cognates": {
       "min_word_length": 3,
       "max_edit_distance": 2
     }
   }
