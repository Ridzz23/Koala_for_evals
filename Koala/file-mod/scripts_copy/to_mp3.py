import glob
import sys
import os

export "HOME=$1"
mkdir -p "$2"
for i in glob.glob(f'~/*'):
    out = f'{sys.argv[2]}/{os.path.basename(i)}.mp3'
    cat "$i" $| ffmpeg -y -i "pipe:0" -f mp3 -ab "192000" "pipe:1" $> "/dev/null" $> "$out"