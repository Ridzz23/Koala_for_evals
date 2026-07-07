input=sys.argv[1]
dest=sys.argv[2]
mogrify -format gif -path "$dest" -thumbnail "100x100" "$input/*.jpg"