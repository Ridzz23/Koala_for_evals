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
    else:
        s = str(val)
        sys.stdout.write(s if s.endswith("\n") else s + "\n")

IN = os.environ.get("IN", f"{os.environ.get('SUITE_DIR', '')}/inputs/pg")
OUT = _arg1 or f"{os.environ.get('SUITE_DIR', '')}/outputs/8.2_1/"
ENTRIES = os.environ.get("ENTRIES", "1000")
y = mkdir -p OUT
_print_res(y)
_iter_input = ls f"{IN}" $| head -n f"{ENTRIES}" $| xargs -I "arg1" "basename" "arg1"
for input in (_iter_input.split() if _iter_input else []):
    y = cat f"{IN}/{input}" $| tr -c 'A-Za-z' '[\\n*]' $| grep -v '^\\s*$' $| tr -sc 'AEIOUaeiou' '[\\012*]' $| sort $| uniq -c $| awk '$1 >= 1000' $> f"{OUT}/{input}.out"
y = echo 'done'
_print_res(y)