import os
import subprocess
import sys

$IN="inputs/bio-full"
$IN_NAME="inputs/bio-full/input.txt"
$OUT="outputs"


for arg in sys.argv[1:]:
    match arg:
        case "--small":
            $IN_NAME="inputs/bio-small/input_small.txt" 
            $IN="inputs/bio-small"
        case "--min":
            $IN_NAME="inputs/bio-min/input_min.txt"
            $IN="inputs/bio-min"

size="full"
subset=False
selected_scripts=[]

args = sys.argv[1:]
i = 0

while i < len(args):
    current_arg = args[i]
    match current_arg:
        case "--small":
            size = "full"
            subset = True
            i += 1
            
        case "--min":
            size = "min"
            i += 1
            
        case "-s" | "--scripts":
            i += 1
            # Nested loop to grab all values until the next flag (starts with -)
            while i < len(args) and not args[i].startswith("-"):
                selected_scripts.append(args[i])
                i += 1
        
        case _:
            # The catch-all (*)
            i += 1

    
$SIZE=full

x = echo $KOALA_SHELL
if x=="":
    $KOALA_SHELL="bash"
else:
    $KOALA_SHELL=x
#if koala shell has a value already then dont need to reset 

$BENCHMARK_CATEGORY="bio"

def should_run(script_name, selected_scripts):
    if not selected_scripts:
        return True
    return script_name in selected_scripts

if should_run("bio", selected_scripts):
    script_file="./scripts/bio.sh"
    tmp1 = realpath $script_file
    $BENCHMARK_SCRIPT=tmp1

    tmp2 = realpath $IN 
    $BENCHMARK_INPUT_FILE=tmp2

     $KOALA_SHELL "$script_file" "$IN" "$IN_NAME" "$OUT" #--- TODO : how to convert this ?
    
if size=="min":
    exit(0)

teraseq_script_names = ["data", "run_dRNASeq", "run_5TERA"]

if subset:
    teraseq_script_names = ["data", "run_dRNASeq"]

tmp3 = realpath "inputs/full"
$BENCHMARK_INPUT_FILE=tmp3

for script in script_list:
    if should_run(script, selected_scripts):
        script_file = f"./scripts/{script}.sh"
        tmp4 = realpath $script_file
        $BENCHMARK_SCRIPT=tmp4

        echo script

        $KOALA_SHELL "$script_file" #-- Again this needs to run a process how to support TODO

         echo "$?" #-- TODO : dont have support for this :(









