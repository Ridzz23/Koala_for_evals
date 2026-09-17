import os
import sys
from pathlib import Path

# Import the BashToDSLTranspiler directly from your transpile.py
try:
    from transpiler import BashToDSLTranspiler
except ImportError:
    print("Error: Could not import BashToDSLTranspiler. Ensure transpile.py is in the current directory or PYTHONPATH.", file=sys.stderr)
    sys.exit(1)

def batch_transpile(src_dir: str, dest_dir: str):
    src_path = Path(src_dir).resolve()
    dest_path = Path(dest_dir).resolve()

    if not src_path.exists():
        print(f"Error: Source directory '{src_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    transpiler = BashToDSLTranspiler()
    converted_count = 0
    skipped_count = 0
    error_count = 0

    print(f"Source: {src_path}")
    print(f"Destination: {dest_path}\n")

    for root, dirs, files in os.walk(src_path):
        # In-place modification of dirs prevents os.walk from descending into 'maybe' folders
        if 'maybe' in dirs:
            dirs.remove('maybe')
            print(f"Skipping folder: {os.path.join(root, 'maybe')}")

        for file in files:
            if not file.endswith('.sh'):
                continue

            input_file = Path(root) / file
            # Compute relative path to preserve folder hierarchy
            rel_path = input_file.relative_to(src_path)
            # Change extension from .sh to .py
            output_file = dest_path / rel_path.with_suffix('.py')

            # Ensure the target subdirectory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)

            try:
                with open(input_file, 'r', encoding='utf-8') as f:
                    bash_content = f.read()

                dsl_output = transpiler.transpile(bash_content)

                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(dsl_output)

                converted_count += 1
                print(f"[OK] {rel_path} -> {output_file.relative_to(dest_path)}")
            except Exception as e:
                error_count += 1
                print(f"[ERROR] Failed {rel_path}: {e}", file=sys.stderr)

    print("\n--- Summary ---")
    print(f"Converted: {converted_count}")
    print(f"Errors:    {error_count}")
    print(f"Output saved to: {dest_path}")

if __name__ == "__main__":
    # Default directories, can be overridden via CLI args:
    # python batch_transpile.py [input_dir] [output_dir]
    default_src = "pepper_suite"
    default_dest = "pepper_suite_transpiled"

    src = sys.argv[1] if len(sys.argv) > 1 else default_src
    dest = sys.argv[2] if len(sys.argv) > 2 else default_dest

    batch_transpile(src, dest)