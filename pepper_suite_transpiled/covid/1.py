import sys

y = cat sys.argv[1] $| sed "s/T..:..:..//" $| cut -d "," -f "1,3" $| sort -u $| cut -d "," -f "1" $| sort $| uniq -c $| awk f"{print {sys.argv[2]},{sys.argv[1]}}"
print(y)