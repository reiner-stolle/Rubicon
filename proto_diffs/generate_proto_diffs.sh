#!/usr/bin/env bash

set -euo pipefail

# Set the directory. Repo1 is the Rubicon Repo, Repo2 is the optimizer
REPO1_PROTO="$HOME/Rubicon/proto"
REPO2_PROTO="$HOME/ws25-optimizer-cpp/proto"
OUTPUT_DIR="$HOME/Rubicon/proto_diffs"

# Make the Output Directory, if it doesn't already exist
mkdir -p "$OUTPUT_DIR"

# Depth First Search of one, I couldn't find the files, this works though.
mapfile -t PROTO_FILES < <(find "$REPO1_PROTO" -maxdepth 1 -type f -name "*.proto")

# Enter vimdiff loop
echo "Found ${#PROTO_FILES[@]} proto files"

for file1 in "${PROTO_FILES[@]}"; do
    filename="$(basename "$file1")"
    name="${filename%.proto}"

    file2="$REPO2_PROTO/$filename"
    output="$OUTPUT_DIR/${name}_diff.html"

    if [[ ! -f "$file2" ]]; then
        echo "Skipping missing: $file2"
        continue
    fi

    echo "Generating diff:"
    echo "  $file1"
    echo "  $file2"
    echo "  -> $output"

    vimdiff "$file1" "$file2" \
        -c 'TOhtml' \
        -c "w! $output" \
        -c 'qa!'
done

echo "Finished generating diffs"
