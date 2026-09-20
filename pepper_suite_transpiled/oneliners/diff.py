import sys
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

y = touch "s1" "s2"
_print_res(y)
y = cat _arg1 $| tr "[:lower:]" "[:upper:]" $| sort $> "s1"
y = cat _arg1 $| tr "[:upper:]" "[:lower:]" $| sort $> "s2"
y = diff -B "s1" "s2"
_print_res(y)
y = rm "s1" "s2"
_print_res(y)