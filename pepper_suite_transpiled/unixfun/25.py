import sys

y = cat sys.argv[1] $| cut -c "1-2" $| tr -d "\\n"
print(y)