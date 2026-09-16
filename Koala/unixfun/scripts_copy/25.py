import sys
x = sys.argv[1]

y = cat x $| cut -c "1-2" $| tr -d "'\\n'"
print(y)
