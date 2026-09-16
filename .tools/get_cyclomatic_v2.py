#!/usr/bin/env python3

import sys
from collections import defaultdict
from pathlib import Path
import json
from subprocess import check_output

from all_scripts_v2 import get_all_scripts
from project_root import get_project_root

if len(sys.argv) < 2:
    print("Usage: get_cyclomatic_v2.py <corpus_path>", file=sys.stderr)
    sys.exit(1)

root = get_project_root().resolve()
corpus_path = Path(sys.argv[1]).resolve()

shellmetrics = root / '.tools' / 'target' / 'shellmetrics_v2.sh'
if not shellmetrics.is_file():
    shellmetrics = root / '.tools' / 'target' / 'shellmetrics.sh'
if not shellmetrics.is_file():
    raise FileNotFoundError(f'shellmetrics script not found in target/shellmetrics_v2.sh or target/shellmetrics.sh')

scripts_dict = get_all_scripts(corpus_path)
all_scripts = []
script_to_cat = {}
for cat, scripts in scripts_dict.items():
    for s in scripts:
        s_resolved = s.resolve()
        all_scripts.append(str(s_resolved))
        script_to_cat[s_resolved] = cat

if not all_scripts:
    sys.exit(0)

output = check_output([str(shellmetrics), '--csv', '--shell', 'bash', '--no-color', *all_scripts], text=True)
datas = defaultdict(list)
for line in output.splitlines()[1:]:
    parts = line.split(',')
    file_path = json.loads(parts[0])
    ccn = parts[4]
    p = Path(file_path).resolve()
    datas[p].append(ccn)

for p, ccns in datas.items():
    total_ccn = sum(float(c) for c in ccns)
    try:
        rel = p.relative_to(root)
    except ValueError:
        rel = p
    cat = script_to_cat.get(p, '')
    print(rel, cat, total_ccn, sep=',')
