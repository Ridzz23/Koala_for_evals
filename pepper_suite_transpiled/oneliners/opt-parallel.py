import sys

y = find sys.argv[1] -type "f" -name "*.pgn" -print0 $| xargs "-0" -n4 -P4 "mawk" f"/Result/ { split({sys.argv[0]}, a, "-"); res = substr(a[1], length(a[1]), 1); if (res == 1) white++; if (res == 0) black++; if (res == 2) draw++ } END { print white+black+draw, white, black, draw }" $| mawk f"{games += {sys.argv[1]}; white += {sys.argv[2]}; black += {sys.argv[3]}; draw += {sys.argv[4]}; } END { print games, white, black, draw }"
print(y)