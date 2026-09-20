import sys
import warnings
warnings.filterwarnings('ignore', category=SyntaxWarning)
_arg1 = sys.argv[1] if len(sys.argv) > 1 else ''
_arg2 = sys.argv[2] if len(sys.argv) > 2 else ''

in_dir = _arg1
out_dir = _arg2
y = cat f"{in_dir}/1.INFO" $| grep "\\[RAY\\]" $| head -n1 $| cut -c "7-" $> f"{out_dir}/rays.csv"
y = cat f"{in_dir}/*.INFO" $| grep "\\[RAY\\]" $| grep -v "pathID" $| cut -c "7-" $>> f"{out_dir}/rays.csv"
y = cat f"{out_dir}/rays.csv" $| sed -n '/^590432,/p' $> f"{out_dir}/rt.log"