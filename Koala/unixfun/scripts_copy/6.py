import sys
x = sys.argv[1]

y = cat x $| cut -d "' '" -f "2" $| cut -c "1-1" $| tr -d "'\\n'" $| tr "'[A-Z]'" "'[a-z]'"
print(y)
