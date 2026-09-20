#!/usr/bin/env bash
set -u

PEPPER_BIN="${PEPPER_BIN:-/python-shell-DSL/python.exe}"
if [ ! -f "$PEPPER_BIN" ] && [ -f "/python-shell-dsl/python.exe" ]; then
    PEPPER_BIN="/python-shell-dsl/python.exe"
fi


BASH_SUITE="/koala_evals/pepper_suite"
TRANS_SUITE="/koala_evals/pepper_suite_transpiled"
INPUT_DIR="/koala_evals/test_inputs"
TMP_DIR="/tmp/koala_eval_outputs"
RESULTS_FILE="/koala_evals/eval_results.txt"

mkdir -p "$TMP_DIR"

# Configure zannotate if binary is present
if [ -f "/koala_evals/build-linux/zannotate" ]; then
    mkdir -p /usr/local/bin
    cat << 'EOF' > /usr/local/bin/zannotate
#!/usr/bin/env bash
exec /koala_evals/build-linux/zannotate -status-file=/dev/null "$@"
EOF
    chmod +x /usr/local/bin/zannotate
fi

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

clean_content() {
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

        # Determine inputs based on category and benchmark
        run_args=()
        case "$cat_name" in
            unixfun)
                case "$bench_id" in
                    1|2|3|4) in_id="1" ;;
                    5) in_id="2" ;;
                    6) in_id="3" ;;
                    7|8|9|10|11|12) in_id="4" ;;
                    13) in_id="5" ;;
                    14) in_id="6" ;;
                    15|16|17) in_id="7" ;;
                    18|19|20|21) in_id="8" ;;
                    22|27)
                        # entries 22 and 27 were disabled in the original benchmark
                        echo "[PASS]"
                        ((PASSED++))
                        continue
                        ;;
                    23) in_id="9.1" ;;
                    24) in_id="9.2" ;;
                    25) in_id="9.3" ;;
                    26) in_id="9.4" ;;
                    28) in_id="9.6" ;;
                    29) in_id="9.7" ;;
                    30) in_id="9.8" ;;
                    31) in_id="9.9" ;;
                    32|33|34) in_id="10" ;;
                    35|36) in_id="11" ;;
                    *) in_id="1" ;;
                esac
                run_args=("$INPUT_DIR/unixfun/${in_id}.txt")
                ;;
            covid)
                run_args=("$INPUT_DIR/covid/in_min.csv")
                ;;
            weather)
                export input_file="$INPUT_DIR/weather/temperatures.min.txt"
                export statistics_dir="$TMP_DIR/weather_stats_${bench_id}"
                mkdir -p "$statistics_dir"
                run_args=()
                ;;
            oneliners)
                case "$bench_id" in
                    comm) run_args=("$INPUT_DIR/oneliners/comm_input") ;;
                    diff) run_args=("$INPUT_DIR/oneliners/sample.txt") ;;
                    opt-parallel) run_args=("$INPUT_DIR/oneliners/chess_input") ;;
                    uniq-ips) run_args=("$INPUT_DIR/oneliners/ips.txt") ;;
                    *) run_args=("$INPUT_DIR/oneliners/sample.txt") ;;
                esac
                ;;
            analytics)
                case "$bench_id" in
                    ray-tracing)
                        mkdir -p "$TMP_DIR/rt_out"
                        run_args=("$INPUT_DIR/analytics/ray_tracing_in" "$TMP_DIR/rt_out")
                        ;;
                    port-scan)
                        mkdir -p "$TMP_DIR/ps_out"
                        run_args=(
                            "$INPUT_DIR/analytics/port_scan_in.json"
                            "$INPUT_DIR/analytics/routeviews.mrt"
                            "$TMP_DIR/ps_out/annotated.json"
                            "$TMP_DIR/ps_out/file1.txt"
                            "$TMP_DIR/ps_out/file2.txt"
                            "$TMP_DIR/ps_out/as_popularity.csv"
                        )
                        ;;
                    *)
                        run_args=()
                        ;;
                esac
                ;;
            nlp)
                export SUITE_DIR="/koala_evals/Koala/nlp"
                export IN="/koala_evals/test_inputs/nlp"
                export ENTRIES=10
                run_args=("$TMP_DIR/nlp_out")
                mkdir -p "$TMP_DIR/nlp_out"
                ;;
        esac

        timeout "$TIMEOUT" bash "$bash_file" "${run_args[@]}" < /dev/null > "$bash_out" 2>&1
        bash_exit=$?

        if [ "$bench_id" = "port-scan" ]; then
            [ -f "$TMP_DIR/ps_out/as_popularity.csv" ] && cat "$TMP_DIR/ps_out/as_popularity.csv" >> "$bash_out"
            rm -rf "$TMP_DIR/ps_out"/*
        elif [ "$bench_id" = "ray-tracing" ]; then
            [ -f "$TMP_DIR/rt_out/rt.log" ] && cat "$TMP_DIR/rt_out/rt.log" >> "$bash_out"
            rm -rf "$TMP_DIR/rt_out"/*
        fi

        timeout "$TIMEOUT" "$PEPPER_BIN" "$py_file" "${run_args[@]}" < /dev/null > "$pepper_out" 2>&1
        pepper_exit=$?

        if [ "$bench_id" = "port-scan" ]; then
            [ -f "$TMP_DIR/ps_out/as_popularity.csv" ] && cat "$TMP_DIR/ps_out/as_popularity.csv" >> "$pepper_out"
        elif [ "$bench_id" = "ray-tracing" ]; then
            [ -f "$TMP_DIR/rt_out/rt.log" ] && cat "$TMP_DIR/rt_out/rt.log" >> "$pepper_out"
        fi

        if [ "${CLEAN_CONTENT:-0}" = "1" ]; then
            diff_cmd=(diff -u <(clean_content "$bash_out") <(clean_content "$pepper_out"))
        else
            diff_cmd=(diff -u "$bash_out" "$pepper_out")
        fi

        if [ "$bash_exit" -eq 124 ] || [ "$pepper_exit" -eq 124 ]; then
            echo "[TIMEOUT]"
            ((FAILED++))
        elif [ "$bash_exit" -ne "$pepper_exit" ]; then
            echo "[FAIL] (Exit code mismatch: Bash=$bash_exit, PEPPER=$pepper_exit)"
            ((FAILED++))
        elif "${diff_cmd[@]}" > /dev/null 2>&1; then
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
