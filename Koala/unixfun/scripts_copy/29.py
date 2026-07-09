import sys
x = sys.argv[1]

y = cat x $| sed "2d" $| sed "2d" $| tr -c "'[A-Z]'" "'\\n'" $| tr -d "'\\n'"
print(y)
