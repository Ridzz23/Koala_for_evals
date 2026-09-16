#!/bin/bash

set -e
set -o pipefail

CORPUS_PATH="$1"
OUTPUT_PATH="$2"

if [ -z "$CORPUS_PATH" ] || [ -z "$OUTPUT_PATH" ]; then
    echo "Usage: $0 <corpus-path> <output-path>"
    exit 1
fi

if [ ! -d "$CORPUS_PATH" ]; then
    echo "Error: Corpus directory '$CORPUS_PATH' does not exist." >&2
    exit 1
fi

# Resolve paths to absolute paths before changing working directory
CORPUS_PATH="$(cd "$CORPUS_PATH" && pwd)"
mkdir -p "$OUTPUT_PATH"
OUTPUT_PATH="$(cd "$OUTPUT_PATH" && pwd)"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment if present
if [ -f "$SCRIPT_DIR/../venv_v2/bin/activate" ]; then
    source "$SCRIPT_DIR/../venv_v2/bin/activate"
elif [ -f "$SCRIPT_DIR/venv_v2/bin/activate" ]; then
    source "$SCRIPT_DIR/venv_v2/bin/activate"
elif [ -f "$SCRIPT_DIR/../venv/bin/activate" ]; then
    source "$SCRIPT_DIR/../venv/bin/activate"
elif [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
fi

checked_command() {
    local description="$1"
    shift

    echo "Generating $description" >&2

    if ! "$@"; then
        echo "Error generating $description, static analysis failed" >&2
        exit 1
    fi
}

echo "Analyzing corpus: $CORPUS_PATH"

mkdir -p target plots

checked_command "target/nodes_in_scripts_v2.csv" \
    python3 count_nodes_in_scripts_v2.py "$CORPUS_PATH" \
    | sort > target/nodes_in_scripts_v2.csv

checked_command "target/lines_of_code_v2.csv" \
    python3 count_lines_of_code_v2.py "$CORPUS_PATH" \
    | sort > target/lines_of_code_v2.csv

echo "Generating target/shellmetrics_v2.sh"

if [ ! -x target/shellmetrics_v2.sh ]; then
    if [ -x target/shellmetrics.sh ]; then
        cp target/shellmetrics.sh target/shellmetrics_v2.sh
    else
        SHELLMETRICS_URL="https://raw.githubusercontent.com/shellspec/shellmetrics/b3bfff2af6880443112cdbf2ea449440b30ab9b0/shellmetrics"
        if command -v curl >/dev/null 2>&1; then
            curl -sSfL -o target/shellmetrics_v2.sh "$SHELLMETRICS_URL" || {
                echo "Error downloading target/shellmetrics_v2.sh via curl" >&2
                exit 1
            }
        elif command -v wget >/dev/null 2>&1; then
            wget --quiet -O target/shellmetrics_v2.sh "$SHELLMETRICS_URL" || {
                echo "Error downloading target/shellmetrics_v2.sh via wget" >&2
                exit 1
            }
        else
            echo "Error: neither curl nor wget found to download shellmetrics" >&2
            exit 1
        fi
        chmod a+x target/shellmetrics_v2.sh
    fi
fi

# Ensure target/shellmetrics.sh is also available
if [ ! -x target/shellmetrics.sh ]; then
    cp target/shellmetrics_v2.sh target/shellmetrics.sh
fi

checked_command "target/cyclomatic_v2.csv" \
    python3 get_cyclomatic_v2.py "$CORPUS_PATH" \
    | sort > target/cyclomatic_v2.csv

checked_command "plots/corpus-syntax-analysis_v2.pdf" \
    python3 viz/syntax_v2.py "$CORPUS_PATH" plots

SRC_PDF="plots/corpus-syntax-analysis_v2.pdf"
if [ -d "$OUTPUT_PATH" ]; then
    DEST_PDF="$OUTPUT_PATH/corpus-syntax-analysis_v2.pdf"
else
    DEST_PDF="$OUTPUT_PATH"
fi

if [ -e "$DEST_PDF" ] && python3 -c 'import sys, os; sys.exit(0 if os.path.samefile(sys.argv[1], sys.argv[2]) else 1)' "$SRC_PDF" "$DEST_PDF" 2>/dev/null; then
    FINAL_PDF="$DEST_PDF"
else
    cp "$SRC_PDF" "$DEST_PDF"
    FINAL_PDF="$DEST_PDF"
fi


echo '---------------------------------------------------------------------------------------------------------------------------------------'
echo "Static analysis complete, all targets generated successfully."
echo "Syntax analysis heatmap is located at $FINAL_PDF"
echo '---------------------------------------------------------------------------------------------------------------------------------------'