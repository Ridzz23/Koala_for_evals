import sys

y = cat sys.argv[1] $| cut -c "1-1" $| tr -d "\\n"
print(y)