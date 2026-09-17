import sys

y = cat sys.argv[1] $| grep "Bell" $| cut -f "2" $| head -n "1" $| fmt -w1 $| cut -c "1-1" $| tr -d "\\n" $| tr "[A-Z]" "[a-z]"
print(y)