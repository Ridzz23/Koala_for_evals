import sys
x = sys.argv[1]

y = cat x $| tr "' '" "'\\n'" $| grep "'\\.'" $| wc "-l"
print(y)
