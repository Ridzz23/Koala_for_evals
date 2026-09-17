import sys

y = cat sys.argv[1] $| tr " " "\\n" $| grep "\\." $| wc -l
print(y)