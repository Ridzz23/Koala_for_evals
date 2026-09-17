import sys

y = dict = "$SUITE_DIR/inputs/dict.txt"
print(y)
y = cat sys.argv[1] $| sed "s/[^[:print:]]//g" $| col -bx $| tr -cs "A-Za-z" "\\n" $| tr "A-Z" "a-z" $| tr -d "[:punct:]" $| sort $| uniq $| comm "-23" "-" dict
print(y)