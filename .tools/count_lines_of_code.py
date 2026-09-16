#!/usr/bin/env python3

import sys
from pathlib import Path
from typing import Optional
import json
from subprocess import Popen, PIPE

from project_root import get_project_root

root = get_project_root().resolve()

if len(sys.argv) > 1:
    from all_scripts_v2 import get_all_scripts
    corpus_path = Path(sys.argv[1]).resolve()
    scripts_dict = get_all_scripts(corpus_path)
    has_category = True
else:
    from all_scripts import get_all_scripts
    scripts_dict = get_all_scripts()
    has_category = False

processes = []
for benchmark_name, scripts in scripts_dict.items():
    for script in scripts:
        process = Popen(['cloc', '--json', str(script)], stdout=PIPE, stderr=PIPE)
        try:
            rel_script = script.resolve().relative_to(root)
        except ValueError:
            rel_script = script
        processes.append((rel_script, benchmark_name, process))

for rel_script, benchmark_name, process in processes:
    stdout, _stderr = process.communicate()
    try:
        cloc = json.loads(stdout.decode())
        cloc = cloc.get('SUM', {}).get('code', 0)
    except Exception:
        cloc = 0
    if has_category:
        print(rel_script, benchmark_name, cloc, sep=',')
    else:
        print(rel_script, cloc, sep=',')

