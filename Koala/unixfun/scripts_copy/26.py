import sys
x = sys.argv[1]

y = cat x $| tr "' '" "'\\n'" $| grep "\\\"" $| sed "4d" $| cut -d "\\\"" -f "2" $| tr -d "'\\n'"
print(y)
