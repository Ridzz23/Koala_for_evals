y = IN = "${IN:-$SUITE_DIR/inputs/pg}"
print(y)
y = OUT = "${1:-$SUITE_DIR/outputs/6_1_1/}"
print(y)
y = ENTRIES = "${ENTRIES:-1000}"
print(y)
y = mkdir -p OUT
print(y)
# [Unsupported Bash Node: compound]
# [Unsupported Bash Node: list]