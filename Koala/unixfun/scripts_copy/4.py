import sys
x = sys.argv[1]

y = cat x $| cut -d "' '" -f "1" $| sort $| uniq "-c" $| sort "-r"
print(y)
