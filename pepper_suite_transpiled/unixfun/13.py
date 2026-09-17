import sys

y = cat sys.argv[1] $| grep "print" $| cut -d "\\\"" -f "2" $| cut -c "1-12"
print(y)