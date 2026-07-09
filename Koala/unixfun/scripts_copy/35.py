import sys
x = sys.argv[1]

y = cat x $| grep "'UNIX'" $| cut -f "1"
print(y)
