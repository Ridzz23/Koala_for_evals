y = mkfifo "s1" "s2"
print(y)
# [Unsupported Bash Node: list]
# [Unsupported Bash Node: list]
y = diff -B "s1" "s2"
print(y)
y = rm "s1" "s2"
print(y)