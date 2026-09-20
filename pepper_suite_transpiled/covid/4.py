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

y = cat _arg1 $| sed 's/T\\(..\\):..:../,\\1/' $| cut -d ',' -f "1,2" $| sort -u $| cut -d ',' -f "1" $| sort $| uniq -c $| awk '{print $2,$1}'
_print_res(y)