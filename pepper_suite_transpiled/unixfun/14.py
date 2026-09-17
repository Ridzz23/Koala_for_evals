import sys

y = cat sys.argv[1] $| awk f"{print {sys.argv[2]}, {sys.argv[0]}}" $| sort -nr $| cut -d " " -f "2"
print(y)