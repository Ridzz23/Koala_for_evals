import sys

y = cat sys.argv[1] $| sort $| uniq
print(y)