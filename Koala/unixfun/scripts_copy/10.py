import sys
x = sys.argv[1]

y = cat x $| tr "' '" "'\\n'" $| grep "'x'" $| grep "'\\.'" $| cut -d "'.'" -f "2" $| grep "'[KQRBN]'" $| cut -c "1-1" $| sort $| uniq "-c" $| sort "-nr"
print(y)
