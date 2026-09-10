#!/usr/bin/env python3

import sys
from pathlib import Path
from collections import Counter

from all_scripts_v2 import get_all_scripts
from syntax_analysis import parse_shell_script, count_nodes
from project_root import get_project_root


if len(sys.argv) < 2:
    print("Usage: count_nodes_in_scripts_v2.py <corpus_path>", file=sys.stderr)
    sys.exit(1)

root = get_project_root().resolve()
corpus_path = Path(sys.argv[1]).resolve()

for category, scripts in get_all_scripts(corpus_path).items():
    for script in scripts:
        asts = parse_shell_script(script)

        count = Counter()
        count_nodes(asts, count)

        count_str = ';'.join(
            f'{node}:{number}'
            for node, number in count.items()
        )

        try:
            rel_script = script.resolve().relative_to(root)
        except ValueError:
            rel_script = script

        print(
            rel_script,
            category,
            count_str,
            sep=','
        )