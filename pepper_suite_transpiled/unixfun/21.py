import sys

y = cat sys.argv[1] $| tr -c "[a-z][A-Z]" "\\n" $| sort $| awk "length >= 16"
print(y)