import sys

y = cat sys.argv[1] $| tr " " "\\n" $| grep "x" $| grep "\\." $| cut -d "." -f "2" $| cut -c "1-1" $| tr "[a-z]" "P" $| sort $| uniq -c $| sort -nr
print(y)