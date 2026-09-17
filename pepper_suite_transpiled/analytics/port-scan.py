import sys

y = filename = sys.argv[1]
print(y)
y = mrt_file = sys.argv[2]
print(y)
y = annotated = sys.argv[3]
print(y)
y = file1 = sys.argv[4]
print(y)
y = file2 = sys.argv[5]
print(y)
y = as_popularity = sys.argv[6]
print(y)
y = cat filename $| zannotate -routing "-routing-mrt-file=$mrt_file" "-input-file-type=json" $> f"{annotated}"
print(y)
y = cat annotated $| jq ".ip" $| tr -d "\"" $> f"{file1}"
print(y)
y = cat annotated $| jq -c ".zannotate.routing.asn" $> f"{file2}"
print(y)
y = pr "-mts," file1 file2 $| awk "-F," f"{ a[{sys.argv[2]}]++; } END { for (n in a) print n "," a[n] } " $| sort -k2 -n "-t," -r $> f"{as_popularity}"
print(y)