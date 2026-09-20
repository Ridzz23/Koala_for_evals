import sys
import os
import warnings
warnings.filterwarnings('ignore', category=SyntaxWarning)
def _print_res(val):
    if val is None or val == "":
        return
    if isinstance(val, (list, tuple)):
        sys.stdout.write("\n".join(str(x) for x in val) + "\n")
    elif isinstance(val, (int, float)):
        sys.stdout.write(f"{val}\n")
    else:
        sys.stdout.write(str(val))

input_file = os.environ.get("input_file", "")
if not input_file: sys.stdout.write("script was not provided with $input_file\n")
statistics_dir = os.environ.get("statistics_dir", "")
if not statistics_dir: sys.stdout.write("script was not provided with $statistics_dir\n")
y = cat f"{input_file}" $| cut -c "89-92" $| grep -v "999" $| sort -rn $| head -n1 $> f"{statistics_dir}/max.txt"
y = cat f"{input_file}" $| cut -c "89-92" $| grep -v "999" $| sort -n $| head -n1 $> f"{statistics_dir}/min.txt"
y = cat f"{input_file}" $| cut -c "89-92" $| grep -v "999" $| awk '{ total += $1; count++ } END { print total/count }' $> f"{statistics_dir}/average.txt"