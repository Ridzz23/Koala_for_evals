import sys

y = cat sys.argv[1] $| tr -c "A-Za-z" "[\\n*]" $| grep -v "^\\s*$" $| tr "A-Z" "a-z" $| sort $| uniq -c $| sort -rn
print(y)