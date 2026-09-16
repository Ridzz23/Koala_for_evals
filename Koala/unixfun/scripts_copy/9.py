import sys
x = sys.argv[1]

y = cat x $| tr "' '" "'\\n'" $| grep "'x'" $| grep "'\\.'" $| cut -d "'.'" -f "2" $| grep -v "'[KQRBN]'" $| wc "-l"
print(y)
