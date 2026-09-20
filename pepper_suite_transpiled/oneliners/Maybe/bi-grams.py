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

y = . "./scripts/bi-gram.aux.sh"
_print_res(y)
y = cat _arg1 $| tr -c 'A-Za-z' '[\\n*]' $| grep -v '^\\s*$' $| tr "A-Z" "a-z" $| bigrams_aux $| sort $| uniq
_print_res(y)