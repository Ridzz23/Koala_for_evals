import sys

y = cat sys.argv[1] $| tr "A-Z" "a-z" $| grep "\\(.\\).*\\1\\(.\\).*\\2\\(.\\).*\\3\\(.\\).*\\4"
print(y)