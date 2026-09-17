#!/usr/bin/env bash
set -u

PEPPER_BIN="/build-linux/python"
BASH_SUITE="/koala_evals/pepper_suite"
TRANS_SUITE="/koala_evals/pepper_suite_transpiled"
TMP_DIR="/tmp/koala_eval_outputs"
RESULTS_FILE="/koala_evals/eval_results.txt"

mkdir -p "$TMP_DIR"

# Tee entire output to RESULTS_FILE while preserving terminal output
exec > >(tee "$RESULTS_FILE") 2>&1

PASSED=0
FAILED=0
ERRORS=0
TIMEOUT=15s

echo "=== Running Koala Equivalence Suite ==="
echo "Timestamp: $(date)"
echo "PEPPER Binary: $PEPPER_BIN"
echo "Results Log: $RESULTS_FILE"
echo ""

for cat_dir in "$BASH_SUITE"/*; do
    [ -d "$cat_dir" ] || continue
    cat_name=$(basename "$cat_dir")
    [ "$cat_name" = "maybe" ] && continue

    echo "--- Category: $cat_name ---"

    for bash_file in "$cat_dir"/*.sh; do
        [ -f "$bash_file" ] || continue
        bench_id=$(basename "$bash_file" .sh)
        py_file="$TRANS_SUITE/$cat_name/$bench_id.py"

        if [ ! -f "$py_file" ]; then
            echo "  [MISSING] $cat_name/$bench_id.py"
            ((ERRORS++))
            continue
        fi

        printf "  Testing %-30s ... " "$bench_id"

        bash_out="$TMP_DIR/${cat_name}_${bench_id}_bash.out"
        pepper_out="$TMP_DIR/${cat_name}_${bench_id}_pepper.out"

        timeout "$TIMEOUT" bash "$bash_file" < /dev/null > "$bash_out" 2>&1
        bash_exit=$?

        timeout "$TIMEOUT" "$PEPPER_BIN" "$py_file" < /dev/null > "$pepper_out" 2>&1
        pepper_exit=$?

        if [ "$bash_exit" -eq 124 ] || [ "$pepper_exit" -eq 124 ]; then
            echo "[TIMEOUT]"
            ((FAILED++))
        elif [ "$bash_exit" -ne "$pepper_exit" ]; then
            echo "[FAIL] (Exit code mismatch: Bash=$bash_exit, PEPPER=$pepper_exit)"
            ((FAILED++))
        elif diff -u "$bash_out" "$pepper_out" > /dev/null 2>&1; then
            echo "[PASS]"
            ((PASSED++))
        else
            echo "[FAIL] (Output mismatch)"
            ((FAILED++))
        fi
    done
done

echo ""
echo "=== Results ==="
echo "Passed: $PASSED | Failed: $FAILED | Errors: $ERRORS"
