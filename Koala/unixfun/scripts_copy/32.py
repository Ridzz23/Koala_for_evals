import sys
x = sys.argv[1]

y = cat x $| sed "1d" $| grep "'Bell'" $| cut -f "2" $| wc "-l"
print(y)
