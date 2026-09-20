import sys
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

y = cat _arg1 $| tr -c '[a-z][A-Z]' '\\n' $| grep '[A-Z]' $| sed "1d" $| sed "1d" $| sed "2d" $| sed "3d" $| sed "5d" $| tr -c '[A-Z]' '\\n' $| tr -d '\\n'
_print_res(y)