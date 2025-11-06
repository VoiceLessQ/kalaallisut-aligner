#!/bin/bash
# Production aligner with full dictionary + realign

set -euo pipefail  # Fail on errors, undefined vars, pipe failures

# Input validation
if [ $# -ne 2 ]; then
    echo "Usage: $0 <danish_file> <kalaallisut_file>" >&2
    echo "" >&2
    echo "Example:" >&2
    echo "  $0 examples/example_danish.txt examples/example_kalaallisut.txt" >&2
    exit 1
fi

DANISH_FILE="$1"
KAL_FILE="$2"

# Validate Danish file
if [ ! -f "$DANISH_FILE" ]; then
    echo "ERROR: Danish file not found: $DANISH_FILE" >&2
    exit 1
fi

if [ ! -r "$DANISH_FILE" ]; then
    echo "ERROR: Danish file not readable: $DANISH_FILE" >&2
    exit 1
fi

# Validate Kalaallisut file
if [ ! -f "$KAL_FILE" ]; then
    echo "ERROR: Kalaallisut file not found: $KAL_FILE" >&2
    exit 1
fi

if [ ! -r "$KAL_FILE" ]; then
    echo "ERROR: Kalaallisut file not readable: $KAL_FILE" >&2
    exit 1
fi

# Validate files are text files (not binaries)
if ! file "$DANISH_FILE" | grep -q text; then
    echo "ERROR: Danish file is not a text file: $DANISH_FILE" >&2
    exit 1
fi

if ! file "$KAL_FILE" | grep -q text; then
    echo "ERROR: Kalaallisut file is not a text file: $KAL_FILE" >&2
    exit 1
fi

# Support environment variable with fallback to default location
HUNALIGN_PATH="${HUNALIGN_PATH:-$HOME/hunalign/src/hunalign/hunalign}"

# Validate hunalign exists and is executable
if [ ! -f "$HUNALIGN_PATH" ]; then
    echo "ERROR: hunalign not found at $HUNALIGN_PATH" >&2
    echo "Install hunalign or set HUNALIGN_PATH environment variable" >&2
    echo "See: https://github.com/danielvarga/hunalign" >&2
    exit 1
fi

if [ ! -x "$HUNALIGN_PATH" ]; then
    echo "ERROR: hunalign not executable: $HUNALIGN_PATH" >&2
    exit 1
fi

# Validate dictionary exists
DICT="data/processed/hunalign_dict_full.txt"
if [ ! -f "$DICT" ]; then
    echo "ERROR: Dictionary not found: $DICT" >&2
    echo "Run data preparation scripts first" >&2
    exit 1
fi

# Run hunalign with validated inputs
"$HUNALIGN_PATH" -text -realign "$DICT" "$DANISH_FILE" "$KAL_FILE"
