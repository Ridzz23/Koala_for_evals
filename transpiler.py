import sys
import bashlex
import re
import os

_NAME_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
_PURE_FLAG_RE = re.compile(r'^-{1,2}[A-Za-z_][A-Za-z0-9_]*$')
_POS_ARG_RE = re.compile(r'(?<!\\)\$(\d+)')
_PARAM_EXP_RE = re.compile(r'\$\{([^:}]+):-(.*?)\}')

class BashToDSLTranspiler:
    def __init__(self):
        self.requires_glob = False
        self.requires_sys = False
        self.requires_os = False
        self.defined_python_vars = set()
        self.positional_args = set()
        self.original_script = ""

    def get_raw_word(self, node):
        if hasattr(node, "pos") and getattr(self, "original_script", None):
            start, end = node.pos
            return self.original_script[start:end]
        return getattr(node, "word", "")

    def preprocess(self, script: str) -> tuple:
        pre_lines = []
        cleaned_script_lines = []
        for line in script.splitlines():
            # Check [[ -n "$var" ]] || echo "msg"
            m = re.match(r'^\s*\[\[\s*-n\s*"\$([A-Za-z0-9_]+)"\s*\]\]\s*\|\|\s*echo\s+"([^"]+)"', line)
            if m:
                var, msg = m.group(1), m.group(2).replace(r'\$', '$')
                self.requires_os = True
                self.requires_sys = True
                self.defined_python_vars.add(var)
                pre_lines.append(f'{var} = os.environ.get("{var}", "")')
                pre_lines.append(f'if not {var}: sys.stdout.write("{msg}\\n")')
                continue
            cleaned_script_lines.append(line)
        return "\n".join(cleaned_script_lines), pre_lines

    def transpile(self, bash_script: str) -> str:
        self.original_script = bash_script
        self.requires_glob = False
        self.requires_sys = False
        self.requires_os = False
        self.defined_python_vars = set()
        self.positional_args = set()

        cleaned_script, pre_lines = self.preprocess(bash_script)
        self.original_script = cleaned_script

        try:
            ast_trees = bashlex.parse(cleaned_script)
        except Exception as e:
            # If bashlex fails (e.g. comments or syntax), return comment
            return f"# Parsing Error: {e}"

        translated_lines = list(pre_lines)
        for tree in ast_trees:
            res = self.visit(tree)
            if not res:
                continue

            # Check if this tree is an assignment command
            is_assignment = False
            if tree.kind == 'command':
                parts = getattr(tree, 'parts', [])
                if parts and all(p.kind == 'assignment' for p in parts if p.kind != 'redirect'):
                    is_assignment = True

            first_tok = res.split()[0] if res.split() else ""
            if tree.kind in ('assignment', 'compound') or is_assignment or (res.startswith('$') and '=' in res) or '=' in res.split()[0:1] or res.startswith('for ') or res.startswith('if ') or res.startswith('_iter_'):
                translated_lines.append(res)
            elif tree.kind in ('command', 'pipeline'):
                if '$>' in res or '$>>' in res:
                    translated_lines.append(f"y = {res}")
                else:
                    translated_lines.append(f"y = {res}")
                    translated_lines.append("_print_res(y)")
                    self.requires_sys = True
            else:
                translated_lines.append(res)

        header = []
        if self.requires_sys or self.positional_args:
            header.append("import sys")
        if self.requires_glob:
            header.append("import glob")
        if self.requires_os:
            header.append("import os")
        header.append("import warnings")
        header.append("warnings.filterwarnings('ignore', category=SyntaxWarning)")

        # Emit positional argument lookups at the top
        for idx in sorted(self.positional_args):
            header.append(f"_arg{idx} = sys.argv[{idx}] if len(sys.argv) > {idx} else ''")
            self.defined_python_vars.add(f"_arg{idx}")

        if self.requires_sys:
            header.append("""def _print_res(val):
    if val is None or val == "":
        return
    if isinstance(val, (list, tuple)):
        sys.stdout.write("\\n".join(str(x) for x in val) + "\\n")
    elif isinstance(val, (int, float)):
        sys.stdout.write(f"{val}\\n")
    else:
        sys.stdout.write(str(val))""")


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

    def visit_list(self, node) -> str:
        parts = getattr(node, 'parts', [])
        lines = []
        for p in parts:
            if getattr(p, 'kind', '') in ('operator',):
                continue
            res = self.visit(p)
            if res:
                if '$>' in res or '$>>' in res:
                    lines.append(f"y = {res}")
                else:
                    lines.append(f"y = {res}")
                    if res.strip().startswith("echo ") and " -n " not in res:
                        lines.append("if isinstance(y, str) and not y.endswith('\\n'): y += '\\n'")
                    lines.append("_print_res(y)")
                    self.requires_sys = True

        return "\n".join(lines)

    def visit_compound(self, node) -> str:
        for item in getattr(node, 'list', []):
            if getattr(item, 'kind', '') == 'for':
                return self.visit_for(item)
        return f"# [Unsupported Bash Node: {node.kind}]"

    def visit_for(self, node) -> str:
        parts = getattr(node, 'parts', [])
        var_name = parts[1].word
        self.defined_python_vars.add(var_name)

        iter_node = parts[3]
        iter_code = ""
        if hasattr(iter_node, 'parts') and iter_node.parts:
            sub = iter_node.parts[0]
            if sub.kind == 'commandsubstitution':
                iter_code = self.visit(sub.command)
        if not iter_code:
            iter_code = self.visit(iter_node)

        do_idx = next(i for i, p in enumerate(parts) if getattr(p, 'word', '') == 'do')
        done_idx = next(i for i, p in enumerate(parts) if getattr(p, 'word', '') == 'done')
        body_nodes = [p for p in parts[do_idx + 1:done_idx] if getattr(p, 'kind', '') not in ('reservedword', 'pipe')]

        iter_var = f"_iter_{var_name}"
        lines = [
            f"{iter_var} = {iter_code}",
            f"for {var_name} in ({iter_var}.split() if {iter_var} else []):"
        ]
        for b_node in body_nodes:
            b_str = self.visit(b_node)
            if b_str:
                if '$>' in b_str or '$>>' in b_str:
                    lines.append(f"    y = {b_str}")
                else:
                    lines.append(f"    y = {b_str}")
                    if b_str.strip().startswith("echo ") and " -n " not in b_str:
                        lines.append("    if isinstance(y, str) and not y.endswith('\\n'): y += '\\n'")
                    lines.append("    _print_res(y)")
                    self.requires_sys = True

        return "\n".join(lines)

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

        if cmd_parts and cmd_parts[0] == 'mkfifo':
            cmd_parts[0] = 'touch'

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

        # 2. Preserved single quotes: In bash, single quotes are 100% literal and NEVER expand variables
        if raw_value.startswith("'") and raw_value.endswith("'"):
            content = raw_value[1:-1]
            content = content.replace('\r\n', '\n')
            if '\n' in content:
                # Multi-line single quoted string (e.g. awk script)
                processed_lines = []
                for l in content.split('\n'):
                    l_str = l.strip()
                    if not l_str:
                        continue
                    if not l_str.endswith((';', '{', '}', 'else', ',')) and not re.search(r'\b(for|if|while)\s*\(.*\)$', l_str):
                        processed_lines.append(l_str + ';')
                    else:
                        processed_lines.append(l_str)
                content = " ".join(processed_lines)
            safe = content.replace('\\', '\\\\').replace("'", "\\'")
            return f"'{safe}'"

        # 3. Standalone Positional bash arguments ($1, "$1", $2, "$2"...)
        pos_match = re.match(r'^"?\$(\d+)"?$', word_value)
        if pos_match:
            idx = int(pos_match.group(1))
            self.positional_args.add(idx)
            return f"_arg{idx}"

        # 4. Inlined positional arguments inside text/quotes (e.g. "$1/foo" or "$1/${input}.out")
        if _POS_ARG_RE.search(word_value) and not raw_value.startswith("'"):
            has_unescaped = False
            for m in _POS_ARG_RE.finditer(raw_value):
                start_pos = m.start()
                if start_pos == 0 or raw_value[start_pos - 1] != '\\':
                    has_unescaped = True
                    self.positional_args.add(int(m.group(1)))

            if has_unescaped:
                content = raw_value.strip('"\'')
                content = content.replace(r'\$', '__ESCAPED_DOLLAR__')
                content = _POS_ARG_RE.sub(r'{_arg\1}', content)
                content = content.replace('__ESCAPED_DOLLAR__', '$')
                for v in self.defined_python_vars:
                    if f"${v}" in content or f"${{{v}}}" in content:
                        content = content.replace(f"${{{v}}}", f"{{{v}}}")
                        content = content.replace(f"${v}", f"{{{v}}}")
                safe = content.replace('\\', '\\\\').replace('"', '\\"')
                return f'f"{safe}"'

        # 5. Known local Python variables passed with bash prefix (e.g. $filename -> filename)
        if word_value.startswith('$'):
            bare_var = word_value.lstrip('$')
            if bare_var in self.defined_python_vars:
                return bare_var
            # If not a defined Python var, treat as native PEPPER env var ($PATH, $HOME)
            if _NAME_RE.match(bare_var):
                return word_value

        # 6. Standard flags matching PEPPER grammar (-l, --color)
        if _PURE_FLAG_RE.match(word_value):
            return word_value

        # 7. Composite flags (-n=5, -I{}, -file=$mrt_file) -> quote as string or f-string
        if word_value.startswith('-'):
            has_var = False
            content = word_value
            for v in self.defined_python_vars:
                if f"${v}" in content or f"${{{v}}}" in content:
                    content = content.replace(f"${{{v}}}", f"{{{v}}}")
                    content = content.replace(f"${v}", f"{{{v}}}")
                    has_var = True
            safe = content.replace('\\', '\\\\').replace('"', '\\"')
            return f'f"{safe}"' if has_var else f'"{safe}"'

        # 8. Preserved double quotes (handles embedded Python vars if present)
        if raw_value.startswith('"') and raw_value.endswith('"'):
            content = raw_value[1:-1]
            content = content.replace('\r\n', '\n')
            if '\n' in content:
                lines = [l.strip() for l in content.split('\n') if l.strip()]
                content = " ".join(lines)
            has_var = False
            for v in self.defined_python_vars:
                if f"${v}" in content or f"${{{v}}}" in content:
                    content = content.replace(f"${{{v}}}", f"{{{v}}}")
                    content = content.replace(f"${v}", f"{{{v}}}")
                    has_var = True

            if has_var:
                safe = content.replace('\\', '\\\\').replace('"', '\\"')
                return f'f"{safe}"'
            else:
                # If there are no Python variables, check if it contains escaped bash vars or $
                # In bash, "{print \$2,\$1}" was double-quoted with \$ so bash wouldn't expand $2,$1.
                # In Python DSL, if we turn it into a single-quoted string, bash will never expand variables!
                if r'\$' in content or '$' in content:
                    clean = content.replace(r'\"', '"').replace(r'\$', '$')
                    safe = clean.replace('\\', '\\\\').replace("'", "\\'")
                    return f"'{safe}'"
                else:
                    safe = content.replace('\\', '\\\\').replace('"', '\\"')
                    return f'"{safe}"'

        # 9. Unquoted Python variable references
        if word_value in self.defined_python_vars:
            return word_value

        # 10. Check if word contains $var like $IN/$input
        has_var = False
        content = word_value
        for v in self.defined_python_vars:
            if f"${v}" in content or f"${{{v}}}" in content:
                content = content.replace(f"${{{v}}}", f"{{{v}}}")
                content = content.replace(f"${v}", f"{{{v}}}")
                has_var = True
        if has_var:
            safe = content.replace('\\', '\\\\').replace('"', '\\"')
            return f'f"{safe}"'

        # 11. All other tokens (numbers, strings) must be quoted strings
        safe_value = word_value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{safe_value}"'

    def visit_redirect(self, node) -> str:
        raw_output = self.visit(node.output)
        if not raw_output:
            return ""

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
        self.defined_python_vars.add(var_name)

        # Handle parameter expansions: IN=${IN:-$SUITE_DIR/inputs/pg}
        param_match = re.match(r'^\$\{([^:}]+):-(.*?)\}$', var_value)
        if param_match:
            src_var = param_match.group(1)
            default_val = param_match.group(2)
            self.requires_os = True
            if src_var.isdigit():
                idx = int(src_var)
                self.positional_args.add(idx)
                if '$SUITE_DIR' in default_val:
                    clean_def = default_val.replace('$SUITE_DIR', "{os.environ.get('SUITE_DIR', '')}")
                    return f'{var_name} = _arg{idx} or f"{clean_def}"'
                return f'{var_name} = _arg{idx} or "{default_val}"'
            else:
                if '$SUITE_DIR' in default_val:
                    clean_def = default_val.replace('$SUITE_DIR', "{os.environ.get('SUITE_DIR', '')}")
                    return f'{var_name} = os.environ.get("{src_var}", f"{clean_def}")'
                return f'{var_name} = os.environ.get("{src_var}", "{default_val}")'

        # Handle $(basename ...) patterns
        if '$(basename' in var_value:
            self.requires_os = True
            self.requires_sys = True
            match = re.search(r'\$\(basename\s+\$?([A-Za-z0-9_]+)\)', var_value)
            if match:
                target_var = match.group(1)
                clean_val = var_value.replace('"', '').replace("'", "")
                clean_val = _POS_ARG_RE.sub(r'{_arg\1}', clean_val)
                clean_val = re.sub(r'\$\(basename\s+\$?[A-Za-z0-9_]+\)', f'{{os.path.basename({target_var})}}', clean_val)
                return f"{var_name} = f'{clean_val}'"

        # Check for positional arguments: var=$1, var="$5"
        pos_match = re.match(r'^"?\$(\d+)"?$', var_value)
        if pos_match:
            idx = int(pos_match.group(1))
            self.positional_args.add(idx)
            return f"{var_name} = _arg{idx}"

        if _POS_ARG_RE.search(var_value):
            for m in _POS_ARG_RE.finditer(var_value):
                self.positional_args.add(int(m.group(1)))
            sub_val = _POS_ARG_RE.sub(r'{_arg\1}', var_value.strip('"\''))
            return f"{var_name} = f'{sub_val}'"

        # Env variable assignment syntax: $NAME = <expr>
        if var_name.startswith('$'):
            env_name = var_name.lstrip('$')
            return f"${env_name} = \"{var_value.strip('\"')}\""

        return f"{var_name} = \"{var_value.strip('\"')}\""