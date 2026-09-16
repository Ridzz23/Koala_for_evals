import sys
x = sys.argv[1]

y = cat x $| tr "' '" "'\\n'" $| grep "'[A-Z]'" $| tr "'[a-z]'" "'\\n'" $| grep "'[A-Z]'" $| tr -d "'\\n'" $| cut -c "1-4"
print(y)
