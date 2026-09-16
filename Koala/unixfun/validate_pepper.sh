#!/bin/bash

# Compare .out files in small-pepper and small-shell.
# Ignores leading/trailing whitespace on each line, and all leading/trailing blank lines.

PEPPER_DIR="outputs/small-pepper"
SHELL_DIR="outputs/small-shell"

status=0

# Helper function to clean the file content using awk
clean_content() {
    # 1. s/^[[:space:]]*//; s/[[:space:]]*$// trims leading/trailing whitespace per line.
    # 2. The awk script skips leading blank lines and buffers content to avoid printing trailing blank lines.
    sed 's/^[[:space:]]*//; s/[[:space:]]*$//' "$1" | awk '
        /./ {
            while (blank_lines > 0) {
                print ""
                blank_lines--
            }
            print
            started = 1
            next
        }
        started { blank_lines++ }
    '
}

for pepper_file in "$PEPPER_DIR"/*.out; do
    [ -e "$pepper_file" ] || continue

    filename=$(basename "$pepper_file")
    shell_file="$SHELL_DIR/$filename"

    if [ ! -f "$shell_file" ]; then
        echo "Missing: $shell_file"
        status=1
        continue
    fi

    # Compare the cleaned outputs using process substitution
    if diff -q <(clean_content "$pepper_file") <(clean_content "$shell_file") >/dev/null; then
        echo "PASS: $filename"
    else
        echo "❌FAIL: $filename"
        status=1
    fi
done

exit $status