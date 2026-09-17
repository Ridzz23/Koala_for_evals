import sys

y = cat sys.argv[1] $| cut -d " " -f "2" $| cut -c "1-1" $| tr -d "\\n" $| tr "[A-Z]" "[a-z]"
print(y)