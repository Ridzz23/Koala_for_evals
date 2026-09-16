import sys
x = sys.argv[1]

y = cat x $| grep "'print'" $| cut -d '"\\\""' -f "2" $| cut -c "1-12"
print(y)
