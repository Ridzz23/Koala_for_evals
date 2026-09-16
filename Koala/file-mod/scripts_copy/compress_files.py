import glob
import sys
import os

mkdir -p "$2"
for item in glob.glob(f'sys.argv[1]/*'):
    output_name = f'{sys.argv[2]}/{os.path.basename(item)}.zip'
    cat "$item" $| gzip "--no-name" -c $> "$output_name"