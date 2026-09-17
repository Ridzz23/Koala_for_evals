import sys

y = cat sys.argv[1] $| tr " " "\\n" $| grep "x" $| grep "\\." $| cut -d "." -f "2" $| grep "[KQRBN]" $| cut -c "1-1" $| sort $| uniq -c $| sort -nr
print(y)