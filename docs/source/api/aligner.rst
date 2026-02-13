Aligner Module
==============

.. automodule:: aligner
   :members:
   :undoc-members:
   :show-inheritance:

SentenceAligner Class
---------------------

.. autoclass:: aligner.SentenceAligner
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__
   .. automethod:: split_sentences
   .. automethod:: calculate_similarity
   .. automethod:: align_greedy
   .. automethod:: align_documents
   .. automethod:: save_alignments

Overview
--------

The aligner module implements the core sentence alignment algorithm for Danish-Kalaallisut parallel texts.

Algorithm:

1. **Sentence Splitting**: Date-aware splitting with month name detection
2. **Similarity Scoring**: Based on word count, character count, and position
3. **Greedy Alignment**: Matches each Danish sentence to best Kalaallisut sentence

Weights (configurable):

* Word score: 0.4
* Character score: 0.3
* Position score: 0.3

Example
-------

.. code-block:: python

   from aligner import SentenceAligner

   aligner = SentenceAligner()

   danish_text = "Hej. Hvordan har du det?"
   kal_text = "Aluu. Qanoq ippit?"

   alignments = aligner.align_documents(danish_text, kal_text)

   for align in alignments:
       print(f"Confidence: {align['confidence']:.2f}")
       print(f"DA: {align['danish']}")
       print(f"KL: {align['kalaallisut']}")
