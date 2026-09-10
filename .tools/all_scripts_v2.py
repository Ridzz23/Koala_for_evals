#!/usr/bin/env python3

from pathlib import Path


def get_all_scripts(corpus_path):
    corpus_path = Path(corpus_path).resolve()

    scripts_by_category = {}

    for category in sorted(corpus_path.iterdir()):
        if not category.is_dir() or category.name.startswith("."):
            continue

        scripts_by_category[category.name] = sorted([
            file
            for file in category.rglob("*")
            if file.is_file() and not file.name.startswith(".")
        ])

    return scripts_by_category


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "../Koala/pre-analysis-corpus"
    scripts = get_all_scripts(path)
    for cat, files in scripts.items():
        print(f"{cat}: {len(files)} scripts")