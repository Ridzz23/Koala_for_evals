import sys
x = sys.argv[1]

y = cat x $| cut -d "' '" -f "4" $| tr -d "','"
print(y)
