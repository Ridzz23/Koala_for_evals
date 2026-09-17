import sys

y = cat sys.argv[1] $| sed "s/T\\(..\\):..:../,\\1/" $| cut -d "," -f "1,2,4" $| sort -u $| cut -d "," -f "3" $| sort $| uniq -c $| sort -k "1" -n $| awk f"{print {sys.argv[2]},{sys.argv[1]}}"
print(y)