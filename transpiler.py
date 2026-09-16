import sys
import bashlex
import re
import os

_NAME_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
_PURE_FLAG_RE = re.compile(r'^-{1,2}[A-Za-z_][A-Za-z0-9_]*$')

class BashToDSLTranspiler:
    def __init__(self):
        self.requires_glob = False
        self.requires_sys = False
        self.requires_os = False
        self.uses_arg1 = False
        self.uses_arg2 = False
        self.original_script = ""

    def get_raw_word(self, node):
        if hasattr(node, "pos") and getattr(self, "original_script", None):
            start, end = node.pos
            return self.original_script[start:end]
        return getattr(node, "word", "")

    def transpile(self, bash_script: str) -> str:
        """Parses a full Bash script and recursively translates it to PEPPER DSL."""
        self.original_script = bash_script
        self.requires_glob = False
        self.requires_sys = False
        self.requires_os = False
        self.uses_arg1 = False
        self.uses_arg2 = False

        try:
            ast_trees = bashlex.parse(bash_script)
        except Exception as e:
            return f"# Parsing Error: {e}"

        translated_lines = []
        for tree in ast_trees:
            res = self.visit(tree)
            if res:
                # Capture output in y and print(y) for execution in eval benchmarks
                translated_lines.append(f"y = {res}")
                translated_lines.append("print(y)")

        header = []
        if self.requires_sys or self.uses_arg1 or self.uses_arg2:
            header.append("import sys")
        if self.requires_glob:
            header.append("import glob")
        if self.requires_os:
            header.append("import os")

        # Map non-native positional args $1 and $2 to Python variables
        if self.uses_arg1:
            header.append("x = sys.argv[1]")
        if self.uses_arg2:
            header.append("y = sys.argv[2]")

        if header:
            header.append("")

        return "\n".join(header + translated_lines)

    def visit(self, node) -> str:
        """Recursive descent router based on the node kind."""
        if node is None:
            return ""
        method_name = f"visit_{node.kind}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node) -> str:
        return f"# [Unsupported Bash Node: {node.kind}]"

    def visit_pipeline(self, node) -> str:
        """Translates pipelines using PEPPER's $| operator."""
        commands = [part for part in getattr(node, 'parts', []) if part.kind != 'pipe']
        parts = [self.visit(part) for part in commands]
        return " $| ".join(parts)

    def visit_command(self, node) -> str:
        cmd_parts = []
        redirect_parts = []

        for idx, part in enumerate(getattr(node, 'parts', [])):
            if part.kind == 'redirect':
                redir_str = self.visit_redirect(part)
                if redir_str:
                    redirect_parts.append(redir_str)
            elif part.kind == 'word':
                is_cmd_name = (idx == 0)
                translated_part = self.visit_word(part, is_command_name=is_cmd_name)
                if translated_part:
                    cmd_parts.append(translated_part)
            else:
                translated_part = self.visit(part)
                if translated_part:
                    cmd_parts.append(translated_part)

        base_command = " ".join(cmd_parts)
        if redirect_parts:
            return f"{base_command} {' '.join(redirect_parts)}"
        return base_command

    def visit_word(self, node, is_command_name=False) -> str:
        word_value = getattr(node, 'word', '')
        raw_value = self.get_raw_word(node)

        # 1. Base command identifier (ls, grep, cat, etc.)
        if is_command_name:
            return word_value

        # 2. Positional bash arguments (mapped to Python variables x and y)
        if '$1' in word_value:
            self.uses_arg1 = True
            if word_value in ('$1', '"$1"'):
                return "x"
            word_value = word_value.replace('"$1"', '{x}').replace('$1', '{x}')
            return f'f"{word_value}"'

        if '$2' in word_value:
            self.uses_arg2 = True
            if word_value in ('$2', '"$2"'):
                return "y"
            word_value = word_value.replace('"$2"', '{y}').replace('$2', '{y}')
            return f'f"{word_value}"'

        # 3. Native PEPPER environment variables ($NAME, =$NAME)
        # Grammar: op="$" n=NAME or op="=" op2="$" n2=NAME
        if re.match(r'^\$[A-Za-z_][A-Za-z0-9_]*$', word_value):
            return word_value

        if re.match(r'^=\$[A-Za-z_][A-Za-z0-9_]*$', word_value):
            return word_value

        # 4. Standard flags matching single or double dash rules
        # Single dash: -[a-zA-Z_] | Double dash: --[a-zA-Z_]
        if _PURE_FLAG_RE.match(word_value):
            return word_value

        # 5. Composite flags (e.g. -n=5, -I{}, or numeric options like -1) -> quote as string
        if word_value.startswith('-'):
            safe = word_value.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{safe}"'

        # 6. Preserved single and double quoting
        if raw_value.startswith("'") and raw_value.endswith("'"):
            content = raw_value[1:-1]
            safe = content.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{safe}"'

        if raw_value.startswith('"') and raw_value.endswith('"'):
            content = raw_value[1:-1]
            safe = content.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{safe}"'

        # 7. Pure Python variable reference (unquoted bare name)
        if _NAME_RE.match(word_value):
            return word_value

        # 8. Numeric literals and general string arguments (must be quoted strings)
        safe_value = word_value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{safe_value}"'

    def visit_redirect(self, node) -> str:
        """Translates redirections strictly to $<, $>, and $>>."""
        target_file = self.visit(node.output)
        if not target_file:
            return ""

        # Enforce quotes around filenames per PEPPER grammar strings rule
        if not ((target_file.startswith('"') and target_file.endswith('"')) or
                (target_file.startswith("'") and target_file.endswith("'"))):
            target_file = f'"{target_file}"'

        redir_op = getattr(node, 'type', '>')
        if '>>' in redir_op:
            return f'$>> {target_file}'
        elif '>' in redir_op:
            return f'$> {target_file}'
        elif '<' in redir_op:
            return f'$< {target_file}'
        return f'$> {target_file}'

    def visit_function(self, node) -> str:
        func_name = node.name
        body_content = ""
        if hasattr(node, 'parts') and node.parts:
            body_content = self.visit(node.parts[0])

        indented_body = "\n".join(f"    {line}" for line in body_content.split("\n") if line.strip())
        if not indented_body.strip():
            indented_body = "    pass"
        return f"def {func_name}():\n{indented_body}"

    def visit_compound(self, node) -> str:
        children = getattr(node, 'list', []) if hasattr(node, 'list') else getattr(node, 'parts', [])
        parts = [self.visit(part) for part in children]
        return "\n".join(p for p in parts if p)

    def visit_for(self, node) -> str:
        words = [part for part in getattr(node, 'parts', []) if part.kind == 'word']
        loop_var = self.visit(words[0]) if words else "item"

        targets = words[1:] if len(words) > 1 else []
        raw_target = " ".join(self.visit(t) for t in targets)

        if "*" in raw_target:
            self.requires_glob = True
            self.requires_sys = True

            python_target = raw_target.replace('"$1"', '{sys.argv[1]}')\
                                      .replace('$1', '{sys.argv[1]}')\
                                      .replace('"$2"', '{sys.argv[2]}')\
                                      .replace('$2', '{sys.argv[2]}')
            python_target = python_target.replace('"', '').replace("'", "")
            loop_header = f"for {loop_var} in glob.glob(f'{python_target}'):"
        else:
            loop_header = f"for {loop_var} in {raw_target if raw_target else 'inputs'}:"

        body_node = getattr(node, 'body', None)
        if not body_node and hasattr(node, 'parts'):
            body_node = next((part for part in node.parts if part.kind in ('compound', 'list')), None)

        body_content = self.visit(body_node) if body_node else "pass"
        indented_body = "\n".join(f"    {line}" for line in body_content.split("\n") if line.strip())
        if not indented_body.strip():
            indented_body = "    pass"

        return f"{loop_header}\n{indented_body}"

    def visit_reservedword(self, node) -> str:
        return ""

    def visit_list(self, node) -> str:
        children = getattr(node, 'list', []) if hasattr(node, 'list') else getattr(node, 'parts', [])
        parts = [self.visit(part) for part in children]
        return "\n".join(p for p in parts if p)

    def visit_operator(self, node) -> str:
        return ""

    def visit_assignment(self, node) -> str:
        """Translates assignments, mapping export/shell assignments to PEPPER's $NAME = <expr>."""
        raw_assignment = str(getattr(node, 'word', ''))
        if '=' not in raw_assignment:
            return raw_assignment

        var_name, var_value = raw_assignment.split('=', 1)

        # Handle command substitutions like $(basename $item)
        if '$(basename' in var_value:
            self.requires_os = True
            self.requires_sys = True
            match = re.search(r'\$\(basename\s+\$?([A-Za-z0-9_]+)\)', var_value)
            if match:
                target_var = match.group(1)
                clean_val = var_value.replace('"', '').replace("'", "")
                clean_val = clean_val.replace('$1', '{sys.argv[1]}').replace('$2', '{sys.argv[2]}')
                clean_val = re.sub(r'\$\(basename\s+\$?[A-Za-z0-9_]+\)', f'{{os.path.basename({target_var})}}', clean_val)
                return f"{var_name} = f'{clean_val}'"

        # Env variable assignment syntax: $NAME = <expr>
        if var_name.startswith('$'):
            env_name = var_name.lstrip('$')
            return f"${env_name} = \"{var_value.strip('\"')}\""

        # Positional substitution in assignments
        clean_val = var_value.replace('"$1"', 'sys.argv[1]')\
                             .replace('$1', 'sys.argv[1]')\
                             .replace('"$2"', 'sys.argv[2]')\
                             .replace('$2', 'sys.argv[2]')
        return f"{var_name} = {clean_val}"


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {os.path.basename(sys.argv[0])} <path_to_bash_file>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            bash_content = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' could not be found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    transpiler = BashToDSLTranspiler()
    dsl_output = transpiler.transpile(bash_content)
    print(dsl_output)


if __name__ == "__main__":
    main()