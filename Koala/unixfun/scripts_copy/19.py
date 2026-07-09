import sys
x = sys.argv[1]

y = cat x $| grep "'Bell'" $| awk "'length <= 45'" $| cut -d "','" -f "2" $| awk "{\\$1=\\$1};1"
print(y)
