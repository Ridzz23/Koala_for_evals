import sys
x = sys.argv[1]

y = cat x $| cut -f "2" $| sort "-n" $| uniq "-c" $| sort "-nr" $| head -n "1" $| tr -s "' '" "'\\n'" $| tail -n "1"
print(y)
