import sys

y = cat sys.argv[1] $| sed "s/T..:..:..//" $| cut -d "," -f "3,1" $| sort -u $| cut -d "," -f "2" $| sort $| uniq -c $| sort -k "1" -n $| awk f"{print {sys.argv[2]},{sys.argv[1]}}"
print(y)