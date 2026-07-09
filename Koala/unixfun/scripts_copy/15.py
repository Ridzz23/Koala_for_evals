import sys
x = sys.argv[1]

y = cat x $| cut -f "1" $| grep "'AT&T'" $| wc "-l"
print(y)
