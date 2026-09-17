import sys

y = cat sys.argv[1] $| sed "1d" $| grep "Bell" $| cut -f "2" $| wc -l
print(y)