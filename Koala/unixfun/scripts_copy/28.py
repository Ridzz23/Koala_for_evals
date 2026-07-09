import sys
x = sys.argv[1]

y = cat x $| tr "' '" "'\\n'" $| grep "'[A-Z]'" $| sed "1d" $| sed "3d" $| sed "3d" $| tr "'[a-z]'" "'\\n'" $| grep "'[A-Z]'" $| sed "3d" $| tr -c "'[A-Z]'" "'\\n'" $| tr -d "'\\n'"
print(y)
