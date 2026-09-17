import sys

y = cat sys.argv[1] $| cut -f "1" $| grep "AT&T" $| wc -l
print(y)