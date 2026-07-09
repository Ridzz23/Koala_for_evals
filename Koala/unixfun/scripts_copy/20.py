import sys
x = sys.argv[1]

y = cat x $| grep "'('" $| cut -d "'('" -f "2" $| cut -d "')'" -f "1" $| head -n "1"
print(y)
