import sys
x = sys.argv[1]

y = cat x $| tr "' '" "'\\n'" $| grep "'\\.'" $| cut -d "'.'" -f "2" $| cut -c "1-1" $| tr "'[a-z]'" "'P'" $| sort "-r" $| uniq $| head -n "3" $| tail -n "1"
print(y)
