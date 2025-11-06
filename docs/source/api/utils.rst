Utils Module
============

.. automodule:: utils
   :members:
   :undoc-members:
   :show-inheritance:

Functions
---------

.. autofunction:: utils.load_aligned_pairs

.. autofunction:: utils.split_train_test

.. autofunction:: utils.save_pairs

Overview
--------

Utility functions for loading, splitting, and saving aligned sentence pairs.

Features:

* Load pairs from @ -delimited format
* Train/test splitting with reproducibility
* Save pairs back to file

Example
-------

.. code-block:: python

   from utils import load_aligned_pairs, split_train_test, save_pairs

   # Load pairs
   pairs = load_aligned_pairs("data/aligned/corpus_6798_pairs.txt")

   # Split into train/test
   train, test = split_train_test(pairs, test_ratio=0.2, seed=42)

   # Save splits
   save_pairs(train, "train.txt")
   save_pairs(test, "test.txt")
