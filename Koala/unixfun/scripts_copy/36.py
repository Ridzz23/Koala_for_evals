import sys
x = sys.argv[1]

y = cat x $| cut -f "2" $| cut -d "' '" -f "1" $| sort $| uniq "-c" $| sort "-nr" $| head -n "1" $| fmt "-w1" $| sed "1d"
print(y)
