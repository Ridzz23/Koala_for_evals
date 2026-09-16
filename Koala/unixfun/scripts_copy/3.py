import sys
x = sys.argv[1]

y = cat x $| head -n "2" $| cut -d "' '" -f "2"
print(y)
