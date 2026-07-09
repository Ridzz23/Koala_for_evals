import sys
x = sys.argv[1]

y = cat x $| awk "{print \\$2, \\$0}" $| sort "-nr" $| cut -d "' '" -f "2"
print(y)
