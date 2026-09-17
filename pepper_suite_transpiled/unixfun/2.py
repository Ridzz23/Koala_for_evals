import sys

y = cat sys.argv[1] $| cut -d " " -f "2" $| sort
print(y)