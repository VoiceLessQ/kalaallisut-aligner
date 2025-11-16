#!/bin/bash
# Production aligner using hunalign

# Support environment variable with fallback to default location
HUNALIGN_PATH="${HUNALIGN_PATH:-$HOME/hunalign/src/hunalign/hunalign}"

# Check if hunalign exists
if [ ! -f "$HUNALIGN_PATH" ]; then
    echo "ERROR: hunalign not found at $HUNALIGN_PATH" >&2
    echo "Install hunalign or set HUNALIGN_PATH environment variable" >&2
    echo "See: https://github.com/danielvarga/hunalign" >&2
    exit 1
fi

DICT="data/processed/hunalign_dict.txt"
DANISH=$1
KAL=$2
OUTPUT=$3

"$HUNALIGN_PATH" -text "$DICT" "$DANISH" "$KAL" > "$OUTPUT"

echo "Aligned $(wc -l < "$OUTPUT") sentence pairs"
