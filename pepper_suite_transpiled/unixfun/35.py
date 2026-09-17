import sys

y = cat sys.argv[1] $| grep "UNIX" $| cut -f "1"
print(y)