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

y = cat _arg1 $| sed 's/T\\(..\\):..:../,\\1/' $| cut -d ',' -f "1,2,4" $| sort -u $| cut -d ',' -f "3" $| sort $| uniq -c $| sort -k "1" -n $| awk '{print $2,$1}'
_print_res(y)