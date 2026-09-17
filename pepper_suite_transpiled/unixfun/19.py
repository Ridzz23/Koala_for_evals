import sys

y = cat sys.argv[1] $| grep "Bell" $| awk "length <= 45" $| cut -d "," -f "2" $| awk f"{{sys.argv[1]}={sys.argv[1]}};1"
print(y)