import sys

y = cat sys.argv[1] $| tr "A-Z" "a-z" $| sort $| sort -r
print(y)