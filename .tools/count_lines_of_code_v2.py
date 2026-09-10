#!/usr/bin/env python3

import sys
import json
from pathlib import Path
from subprocess import Popen, PIPE

from all_scripts_v2 import get_all_scripts
from project_root import get_project_root

if len(sys.argv) < 2:
    print("Usage: count_lines_of_code_v2.py <corpus_path>", file=sys.stderr)
    sys.exit(1)

root = get_project_root().resolve()
corpus_path = Path(sys.argv[1]).resolve()

scripts_by_cat = get_all_scripts(corpus_path)

processes = []
for category, scripts in scripts_by_cat.items():
    for script in scripts:
        proc = Popen(['cloc', '--json', str(script)], stdout=PIPE, stderr=PIPE)
        try:
            rel_script = script.resolve().relative_to(root)
        except ValueError:
            rel_script = script
        processes.append((rel_script, category, proc))

for rel_script, category, proc in processes:
    stdout, _ = proc.communicate()
    try:
        cloc_data = json.loads(stdout.decode())
        code_lines = cloc_data.get('SUM', {}).get('code', 0)
    except Exception:
        code_lines = 0
    print(rel_script, category, code_lines, sep=',')
