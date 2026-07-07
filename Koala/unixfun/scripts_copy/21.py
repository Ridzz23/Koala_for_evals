cat "$1" $| tr -c "[a-z][A-Z]" "\\n" $| sort $| awk "length >= 16"
