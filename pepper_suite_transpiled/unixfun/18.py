import sys

y = cat sys.argv[1] $| tr " " "\\n" $| grep "1969" $| wc -l
print(y)