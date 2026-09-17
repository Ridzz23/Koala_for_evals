import sys
import bashlex
import re
import os

_NAME_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
_PURE_FLAG_RE = re.compile(r'^-{1,2}[A-Za-z_][A-Za-z0-9_]*$')
_POS_ARG_RE = re.compile(r'\$(\d+)')

class BashToDSLTranspiler:
    def __init__(self):
        self.requires_glob = False
        self.requires_sys = False
        self.requires_os = False
        self.defined_python_vars = set()
        self.original_script = ""

    def get_raw_word(self, node):
        if hasattr(node, "pos") and getattr(self, "original_script", None):
            start, end = node.pos
            return self.original_script[start:end]
        return getattr(node, "word", "")

    def transpile(self, bash_script: str) -> str:
        self.original_script = bash_script
        self.requires_glob = False
        self.requires_sys = False
        self.requires_os = False
        self.defined_python_vars = set()

        try:
            ast_trees = bashlex.parse(bash_script)
        except Exception as e:
            return f"# Parsing Error: {e}"

        translated_lines = []
        for tree in ast_trees:
            res = self.visit(tree)
            if not res:
                continue

            # Standard Python assignments should not be wrapped in y = ... / print(y)
            if tree.kind == 'assignment' or res.startswith('$') and '=' in res:
                translated_lines.append(res)
            elif tree.kind in ('command', 'pipeline'):
                translated_lines.append(f"y = {res}")
                translated_lines.append("print(y)")
            else:
                translated_lines.append(res)

        header = []
        if self.requires_sys:
            header.append("import sys")
        if self.requires_glob:
            header.append("import glob")
        if self.requires_os:
            header.append("import os")

        if header:
            header.append("")

        return "\n".join(header + translated_lines)

    def visit(self, node) -> str:
        if node is None:
            return ""
        method_name = f"visit_{node.kind}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node) -> str:
        return f"# [Unsupported Bash Node: {node.kind}]"

    def visit_pipeline(self, node) -> str:
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

        # 1. Base command identifier
        if is_command_name:
            return word_value

        # 2. Positional bash arguments ($1, $2, $3...) -> sys.argv[N]
        if _POS_ARG_RE.search(word_value):
            self.requires_sys = True
            # Standalone $N or "$N"
            exact_match = re.match(r'^"?\$(\d+)"?$', word_value)
            if exact_match:
                return f"sys.argv[{exact_match.group(1)}]"
            # Inlined inside text -> use f-string
            substituted = _POS_ARG_RE.sub(r'{sys.argv[\1]}', word_value.strip('"\''))
            return f'f"{substituted}"'

        # 3. Known local Python variables passed with bash prefix (e.g. $filename -> filename)
        if word_value.startswith('$'):
            bare_var = word_value.lstrip('$')
            if bare_var in self.defined_python_vars:
                return bare_var
            # If not a defined Python var, treat as native PEPPER env var ($PATH, $HOME)
            if _NAME_RE.match(bare_var):
                return word_value

        # 4. Standard flags matching PEPPER grammar (-l, --color)
        if _PURE_FLAG_RE.match(word_value):
            return word_value

        # 5. Composite flags (-n=5, -I{}) -> quote as string
        if word_value.startswith('-'):
            safe = word_value.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{safe}"'

        # 6. Preserved string quotes (handles embedded Python vars if present)
        if (raw_value.startswith("'") and raw_value.endswith("'")) or \
           (raw_value.startswith('"') and raw_value.endswith('"')):
            content = raw_value[1:-1]
            
            # Check if inner content refers to an inlined Python var like -routing-mrt-file=$mrt_file
            has_var = False
            for v in self.defined_python_vars:
                if f"${v}" in content:
                    content = content.replace(f"${v}", f"{{{v}}}")
                    has_var = True
            
            safe = content.replace('\\', '\\\\').replace('"', '\\"')
            return f'f"{safe}"' if has_var else f'"{safe}"'

        # 7. Unquoted Python variable references
        if word_value in self.defined_python_vars:
            return word_value

        # 8. All other tokens (numbers, strings) must be quoted strings
        safe_value = word_value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{safe_value}"'

    def visit_redirect(self, node) -> str:
        raw_output = self.visit(node.output)
        if not raw_output:
            return ""

        # If redirecting to a local Python variable (e.g. annotated or $annotated)
        clean_name = raw_output.strip('"\'').lstrip('$')
        if clean_name in self.defined_python_vars:
            target_file = f'f"{{{clean_name}}}"'
        elif not ((raw_output.startswith('"') and raw_output.endswith('"')) or
                  (raw_output.startswith("'") and raw_output.endswith("'")) or
                  raw_output.startswith('f"')):
            target_file = f'"{raw_output}"'
        else:
            target_file = raw_output

        redir_op = getattr(node, 'type', '>')
        if '>>' in redir_op:
            return f'$>> {target_file}'
        elif '<' in redir_op:
            return f'$< {target_file}'
        return f'$> {target_file}'

    def visit_assignment(self, node) -> str:
        raw_assignment = str(getattr(node, 'word', ''))
        if '=' not in raw_assignment:
            return raw_assignment

        var_name, var_value = raw_assignment.split('=', 1)

        # Track defined variable name so subsequent commands reference it as a Python var
        self.defined_python_vars.add(var_name)

        # Handle $(basename ...) patterns
        if '$(basename' in var_value:
            self.requires_os = True
            self.requires_sys = True
            match = re.search(r'\$\(basename\s+\$?([A-Za-z0-9_]+)\)', var_value)
            if match:
                target_var = match.group(1)
                clean_val = var_value.replace('"', '').replace("'", "")
                clean_val = _POS_ARG_RE.sub(r'{sys.argv[\1]}', clean_val)
                clean_val = re.sub(r'\$\(basename\s+\$?[A-Za-z0-9_]+\)', f'{{os.path.basename({target_var})}}', clean_val)
                return f"{var_name} = f'{clean_val}'"

        # Check for positional arguments: var=$1, var="$5"
        if _POS_ARG_RE.search(var_value):
            self.requires_sys = True
            exact = re.match(r'^"?\$(\d+)"?$', var_value)
            if exact:
                return f"{var_name} = sys.argv[{exact.group(1)}]"
            sub_val = _POS_ARG_RE.sub(r'{sys.argv[\1]}', var_value.strip('"\''))
            return f"{var_name} = f'{sub_val}'"

        # Env variable assignment syntax: $NAME = <expr>
        if var_name.startswith('$'):
            env_name = var_name.lstrip('$')
            return f"${env_name} = \"{var_value.strip('\"')}\""

        return f"{var_name} = \"{var_value.strip('\"')}\""