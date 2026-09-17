import sys

y = cat sys.argv[1] $| tr " " "\\n" $| grep "x" $| grep "\\." $| wc -l
print(y)