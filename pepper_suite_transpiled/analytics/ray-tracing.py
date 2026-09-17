import sys

y = in_dir = sys.argv[1]
print(y)
y = out_dir = sys.argv[2]
print(y)
y = cat f"{in_dir}/1.INFO" $| grep "\\[RAY\\]" $| head -n1 $| cut -c "7-" $> f"{out_dir}/rays.csv"
print(y)
y = cat "$in_dir/*.INFO" $| grep "\\[RAY\\]" $| grep -v "pathID" $| cut -c "7-" $>> f"{out_dir}/rays.csv"
print(y)
y = cat f"{out_dir}/rays.csv" $| sed -n "/^590432,/p" $> f"{out_dir}/rt.log"
print(y)