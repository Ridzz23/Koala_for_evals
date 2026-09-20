import sys
import os
import warnings
warnings.filterwarnings('ignore', category=SyntaxWarning)
_arg1 = sys.argv[1] if len(sys.argv) > 1 else ''
def _print_res(val):
    if val is None or val == "":
        return
    if isinstance(val, (list, tuple)):
        sys.stdout.write("\n".join(str(x) for x in val) + "\n")
    elif isinstance(val, (int, float)):
        sys.stdout.write(f"{val}\n")
    else:
        sys.stdout.write(str(val))

IN = os.environ.get("IN", f"{os.environ.get('SUITE_DIR', '')}/inputs/pg")
OUT = _arg1 or f"{os.environ.get('SUITE_DIR', '')}/outputs/3_1/"
ENTRIES = os.environ.get("ENTRIES", "1000")
y = mkdir -p OUT
_print_res(y)
_iter_input = ls f"{IN}" $| head -n f"{ENTRIES}" $| xargs -I "arg1" "basename" "arg1"
for input in (_iter_input.split() if _iter_input else []):
    y = cat f"{IN}/{input}" $| tr -c 'A-Za-z' '[\\n*]' $| grep -v '^\\s*$' $| sort $| uniq -c $| sort -nr $> f"{OUT}/{input}.out"
y = echo 'done'
if isinstance(y, str) and not y.endswith('\n'): y += '\n'
_print_res(y)