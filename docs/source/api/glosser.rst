Glosser Module
==============

.. automodule:: glosser_v2_fixed
   :members:
   :undoc-members:
   :show-inheritance:

KalaallisutGlosser Class
------------------------

.. autoclass:: glosser_v2_fixed.KalaallisutGlosser
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__
   .. automethod:: gloss_morpheme
   .. automethod:: translate_root
   .. automethod:: format_analysis
   .. automethod:: gloss_text
   .. automethod:: output_text

Overview
--------

The glosser provides morpheme-by-morpheme analysis of Kalaallisut text.

Features:

* 16,819 dictionary entries (Kalaallisut-English)
* Morphological analysis with gloss tags
* Dictionary caching for performance
* Multiple output formats (text/HTML/JSON)

Dictionaries:

* ``kalaallisut_english_dict.json`` - Word translations
* ``morpheme_glosses.json`` - Morpheme tags and roots

Example
-------

.. code-block:: python

   from glosser_v2_fixed import KalaallisutGlosser

   glosser = KalaallisutGlosser()

   text = "Takussaanga"
   glossed = glosser.gloss_text(text)

   # Text output
   output = glosser.output_text(glossed)
   print(output)

   # Access structured data
   for item in glossed:
       if item['type'] == 'word':
           print(f"Surface: {item['surface']}")
           print(f"Morphemes: {item['morphemes']}")
           print(f"Glosses: {item['glosses']}")
