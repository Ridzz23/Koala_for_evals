import sys

y = cat sys.argv[1] $| head -n "2" $| cut -d " " -f "2"
print(y)