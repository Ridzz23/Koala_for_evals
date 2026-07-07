cat "$1" $| tr " " "\\n" $| grep "" $| sed "4d" $| cut -d "" -f "2" $| tr -d "\\n"
