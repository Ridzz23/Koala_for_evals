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

y = sed 's/T\\(..\\):..:../,\\1/' _arg1 $| awk "-F," '!seen[$1 $2 $4] { seen[$1 $2 $4] = 1; hours[$1 $4]++; bus[$4] = 1; day[$1] = 1; } END { PROCINFO["sorted_in"] = "@ind_str_asc"; for (d in day) printf("\\t%s", d); printf("\\n"); for (b in bus) { printf("%s", b); for (d in day) printf("\\t%s", hours[d b]); printf("\\n"); } }'
_print_res(y)