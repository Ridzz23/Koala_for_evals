import sys

y = cat sys.argv[1] $| grep "(" $| cut -d "(" -f "2" $| cut -d ")" -f "1" $| head -n "1"
print(y)