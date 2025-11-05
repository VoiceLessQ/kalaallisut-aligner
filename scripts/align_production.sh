#!/bin/bash
# Production aligner with full dictionary + realign

# Support environment variable with fallback to default location
HUNALIGN_PATH="${HUNALIGN_PATH:-$HOME/hunalign/src/hunalign/hunalign}"

# Check if hunalign exists
if [ ! -f "$HUNALIGN_PATH" ]; then
    echo "ERROR: hunalign not found at $HUNALIGN_PATH" >&2
    echo "Install hunalign or set HUNALIGN_PATH environment variable" >&2
    echo "See: https://github.com/danielvarga/hunalign" >&2
    exit 1
fi

DICT="data/processed/hunalign_dict_full.txt"
"$HUNALIGN_PATH" -text -realign "$DICT" "$1" "$2"
