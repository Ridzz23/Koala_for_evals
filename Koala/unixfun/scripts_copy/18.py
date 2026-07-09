import sys
x = sys.argv[1]

y = cat x $| tr "' '" "'\\n'" $| grep "1969" $| wc "-l"
print(y)
