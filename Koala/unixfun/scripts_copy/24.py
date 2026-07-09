import sys
x = sys.argv[1]

y = cat x $| cut -c "1-1" $| tr -d "'\\n'"
print(y)
