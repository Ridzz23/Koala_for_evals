import sys
x = sys.argv[1]

y = cat x $| tr -c "[a-z][A-Z]" "'\\n'" $| sort $| awk "length >= 16"
print(y)
