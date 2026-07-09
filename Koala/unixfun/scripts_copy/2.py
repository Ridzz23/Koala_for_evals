import sys
x = sys.argv[1]

y = cat x $| cut -d "' '" -f "2" $| sort
print(y)
