import sys

y = cat sys.argv[1] $| tr " " "\\n" $| grep "x" $| grep "\\." $| cut -d "." -f "2" $| grep -v "[KQRBN]" $| wc -l
print(y)