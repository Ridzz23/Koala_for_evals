import sys
x = sys.argv[1]

y = cat x $| tr -c "'[a-z][A-Z]'" "'\\n'" $| grep "'[A-Z]'" $| sed "1d" $| sed "1d" $| sed "2d" $| sed "3d" $| sed "5d" $| tr -c "'[A-Z]'" "'\\n'" $| tr -d "'\\n'"
print(y)
