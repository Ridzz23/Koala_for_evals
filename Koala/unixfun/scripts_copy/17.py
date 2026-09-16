import sys
x = sys.argv[1]

y = cat x $| cut -f "4" $| sort "-n" $| cut -c "3-3" $| uniq $| sed "s/$/0s/"
print(y)
