import sys
x = sys.argv[1]

y = cat x $| tr "' '" "'\\n'" $| grep "'x'" $| grep "'\\.'" $| wc "-l"
print(y)
