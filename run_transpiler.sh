#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
# TO RUN: ./run_transpiler unixfun
set -e

# 1. Check if a folder argument was provided
if [ -z "$1" ]; then
    echo "Usage: $0 <path_to_folder>" >&2
    exit 1
fi

SOURCE_DIR="$1"

# 2. Verify the provided path is a valid directory
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: '$SOURCE_DIR' is not a directory." >&2
    exit 1
fi

# 3. Determine the output folder name (e.g., /path/to/scripts -> /path/to/scripts_copy)
# Strip any trailing slashes from the source directory path first
CLEANED_DIR="${SOURCE_DIR%/}"
TARGET_DIR="${CLEANED_DIR}_copy"

# Create the output folder if it doesn't exist
mkdir -p "$TARGET_DIR"

echo "Processing scripts from: $CLEANED_DIR"
echo "Saving transpiled output to: $TARGET_DIR"
echo "----------------------------------------"

# 4. Loop through every .sh file in the source directory
# Using a glob safeguard in case no .sh files are found
shopt -s nullglob
SH_FILES=("$CLEANED_DIR"/*.sh)

if [ ${#SH_FILES[@]} -eq 0 ]; then
    echo "No .sh files found in '$CLEANED_DIR'."
    exit 0
fi

for file in "${SH_FILES[@]}"; do
    # Extract just the filename (e.g., /path/to/scripts/test.sh -> test.sh)
    filename=$(basename "$file")

    py_filename="${filename%.sh}.py"

    echo "Transpiling: $filename -> $py_filename ..."
    
    # Run the python transpiler and redirect its stdout into the target directory
    python3 transpiler.py "$file" > "$TARGET_DIR/$py_filename"
done

echo "----------------------------------------"
echo "Done! All files processed successfully."