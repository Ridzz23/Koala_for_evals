import sys

# Case 1: Python logic for argument parsing
force = False
for arg in sys.argv[1:]:
    if arg == "-f":
        force = True

# Case 2: Environment variable assignment using your $NAME = expression syntax
# These will be persistent in the shell state
$TOP = git rev-parse --show-toplevel
$eval_dir = f"{$TOP}/bio"
$outputs_dir = f"{$eval_dir}/outputs"
$input_dir = f"{$eval_dir}/inputs"

# Case 3: Native shell command execution
# 'rm' is not defined in Python, so it triggers _PyAST_ShellCmd
rm -rf $outputs_dir

# Case 4: Mixing Python control flow with shell execution
if force:
    rm -rf $input_dir