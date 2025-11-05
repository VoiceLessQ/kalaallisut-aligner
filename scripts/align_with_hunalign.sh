#!/bin/bash
# Production aligner using hunalign

DICT="data/processed/hunalign_dict.txt"
DANISH=$1
KAL=$2
OUTPUT=$3

~/hunalign/src/hunalign/hunalign -text "$DICT" "$DANISH" "$KAL" > "$OUTPUT"

echo "Aligned $(wc -l < "$OUTPUT") sentence pairs"
