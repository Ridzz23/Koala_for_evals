import sys

y = cat sys.argv[1] $| cut -f "2" $| cut -d " " -f "1" $| sort $| uniq -c $| sort -nr $| head -n "1" $| fmt -w1 $| sed "1d"
print(y)