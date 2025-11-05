#!/bin/bash
# Production aligner with full dictionary + realign

DICT="data/processed/hunalign_dict_full.txt"
~/hunalign/src/hunalign/hunalign -text -realign "$DICT" "$1" "$2"
