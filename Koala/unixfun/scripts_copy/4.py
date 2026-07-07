cat "$1" $| cut -d " " -f "1" $| sort $| uniq "-c" $| sort "-r"
