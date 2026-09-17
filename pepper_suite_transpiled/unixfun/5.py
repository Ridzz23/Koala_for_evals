import sys

y = cat sys.argv[1] $| cut -d " " -f "4" $| tr -d ","
print(y)