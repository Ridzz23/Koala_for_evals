import sys

y = . "./scripts/bi-gram.aux.sh"
print(y)
y = cat sys.argv[1] $| tr -c "A-Za-z" "[\\n*]" $| grep -v "^\\s*$" $| tr "A-Z" "a-z" $| bigrams_aux $| sort $| uniq
print(y)