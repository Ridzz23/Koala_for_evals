import sys

y = cat sys.argv[1] $| cut -d " " -f "1" $| sort $| uniq -c $| sort -r
print(y)