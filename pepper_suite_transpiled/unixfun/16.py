import sys

y = cat sys.argv[1] $| cut -f "2" $| sort -n $| uniq -c $| sort -nr $| head -n "1" $| tr -s " " "\\n" $| tail -n "1"
print(y)