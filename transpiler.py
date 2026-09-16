import sys
import bashlex
import re
import os

_NAME_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

class BashToDSLTranspiler:
    def __init__(self):
        self.requires_glob = False
        self.requires_sys = False
        self.requires_os = False
        self.uses_arg1 = False  # Track if $1 is used
        self.uses_arg2 = False  # Track if $2 is used
        self.original_script = ""
    
    def get_raw_word(self, node):
        if hasattr(node, "pos") and getattr(self, "original_script", None):
            start, end = node.pos
            return self.original_script[start:end]
        return node.word

    def transpile(self, bash_script: str) -> str:
        """Parses a full Bash script and recursively translates it."""
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
                translated_lines.append(f"y = {res}")
                translated_lines.append("print(y)")
        
        # Build header boilerplate automatically
        header = []
        if self.requires_sys or self.uses_arg1 or self.uses_arg2:
            header.append("import sys")
        if self.requires_glob:
            header.append("import glob")
        if self.requires_os:
            header.append("import os")
            
        # Inject the explicit variable assignments right after imports
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
        """Translates pipelines, ignoring raw internal structural pipe operators."""
        commands = [part for part in getattr(node, 'parts', []) if part.kind != 'pipe']
        parts = [self.visit(part) for part in commands]
        return " $| ".join(parts)

    def visit_command(self, node) -> str:
        cmd_parts = []
        redirect_parts = []

        # Enumerate over parts to track which token is the base command
        for idx, part in enumerate(getattr(node, 'parts', [])):
            if part.kind == 'redirect':
                redirect_parts.append(self.visit(part))
            elif part.kind == 'word':
                # Pass an extra flag to visit_word indicating if it's the command name
                is_cmd_name = (idx == 0)
                translated_part = self.visit_word(part, is_command_name=is_cmd_name)
                if translated_part:
                    cmd_parts.append(translated_part)
            else:
                translated_part = self.visit(part)
                if translated_part:
                    cmd_parts.append(translated_part)

        if len(cmd_parts) > 1:
            head, args = cmd_parts[0], cmd_parts[1:]
            if args and all(self._is_single_dash_flag(a) for a in args):
                args[-1] = f'"{args[-1]}"'
            cmd_parts = [head] + args

        base_command = " ".join(cmd_parts)
        if redirect_parts:
            return f"{base_command} {' '.join(redirect_parts)}"
        return base_command

    @staticmethod
    def _is_single_dash_flag(rendered_arg: str) -> bool:
        return (rendered_arg.startswith('-')
                and not rendered_arg.startswith('--')
                and not rendered_arg.startswith('"'))

    def visit_word(self, node, is_command_name=False) -> str:
        word_value = node.word
        raw_value = self.get_raw_word(node)

        # Preserve original quoting semantics
        if raw_value.startswith("'") and raw_value.endswith("'"):
            content = raw_value[1:-1]

            safe = content.replace("\\", "\\\\").replace('"', '\\"')
            return f'"\'{safe}\'"'

        if raw_value.startswith('"') and raw_value.endswith('"'):
            content = raw_value[1:-1]

            if "{" in content and "}" in content:
                safe = content.replace("\\", "\\\\").replace('"', '\\"')
                return f"'\"{safe}\"'"

            safe = content.replace("\\", "\\\\").replace('"', '\\"')
            return f"'\"{safe}\"'"

        # positional arguments
        if '$1' in word_value:
            self.uses_arg1 = True
            return word_value.replace('"$1"', 'x').replace('$1', 'x')

        if '$2' in word_value:
            self.uses_arg2 = True
            return word_value.replace('"$2"', 'y').replace('$2', 'y')

        if word_value == " ":
            return '" "'

        # command name
        if is_command_name:
            return word_value

        # flags
        if word_value.startswith('-'):
            return word_value

        safe_value = word_value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{safe_value}"'

    def visit_redirect(self, node) -> str:
        target_file = self.visit(node.output)
        if not target_file:
            return ""
        
        if not (target_file.startswith('"') and target_file.endswith('"')):
            target_file = f'"{target_file}"'

        if node.type == '<':
            return f'$< {target_file}'
        elif node.type == '>':
            return f'$> {target_file}'
        else:
            if '<' in node.type:
                return f'$< {target_file}'
            return f'$> {target_file}'

    def visit_function(self, node) -> str:
        """Translates a Bash function definition into a Python/PEPPER def block."""
        func_name = node.name
        body_content = ""
        if hasattr(node, 'parts') and node.parts:
            body_content = self.visit(node.parts[0])
            
        indented_body = "\n".join(f"    {line}" for line in body_content.split("\n") if line.strip())
        if not indented_body.strip():
            indented_body = "    pass"
        return f"def {func_name}():\n{indented_body}"

    def visit_compound(self, node) -> str:
        """Handles compound statement blocks wrapped in { ... } or body groupings."""
        children = getattr(node, 'list', []) if hasattr(node, 'list') else getattr(node, 'parts', [])
        parts = [self.visit(part) for part in children]
        return "\n".join(p for p in parts if p)

    # === AUTOMATED HYBRID SYSTEM LOGIC ===
    def visit_for(self, node) -> str:
        """Translates a Bash for loop block into a Python for loop structure."""
        # 1. Isolate the loop variable (the first word node, e.g., 'item')
        words = [part for part in getattr(node, 'parts', []) if part.kind == 'word']
        loop_var = self.visit(words[0]) if words else "item"
        
        # 2. Find the target collection expression (everything between 'in' and the command boundary)
        # In bashlex, node.parts contains the variable and targets, while node.body or a compound holds the execution block.
        targets = words[1:] if len(words) > 1 else []
        raw_target = " ".join(self.visit(t) for t in targets)
        
        # Rule: If the target features a file expansion wildcard (*), map to hybrid Python semantics
        if "*" in raw_target:
            self.requires_glob = True
            self.requires_sys = True
            
            # Translate Bash argument tokens to Python list index structures cleanly
            python_target = raw_target.replace('"$1"', 'sys.argv[1]')\
                                      .replace('$1', 'sys.argv[1]')\
                                      .replace('"$2"', 'sys.argv[2]')\
                                      .replace('$2', 'sys.argv[2]')
            
            # Strip residual quotes so it strings together nicely inside the glob template
            python_target = python_target.replace('"', '').replace("'", "")
            loop_header = f"for {loop_var} in glob.glob(f'{python_target}'):"
        else:
            loop_header = f"for {loop_var} in {raw_target if raw_target else 'inputs'}:"
        
        # 3. Securely look for the loop execution body block
        body_node = getattr(node, 'body', None)
        if not body_node and hasattr(node, 'parts'):
            body_node = next((part for part in node.parts if part.kind in ('compound', 'list')), None)
            
        body_content = self.visit(body_node) if body_node else "pass"
        
        # Indent the execution body lines underneath our clean loop header
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
        """Handles structural loop operators like 'do' and 'done' gracefully as no-ops."""
        # This removes the `# [Unsupported Bash Node: operator]` comments from your loops.
        return ""

    def visit_assignment(self, node) -> str:
        """Handles variable definitions and translates Bash command substitutions to Python."""
        raw_assignment = str(node.word)
        
        # 1. Break the assignment into variable name and value (e.g., output_name and the rest)
        if '=' not in raw_assignment:
            return raw_assignment
        
        var_name, var_value = raw_assignment.split('=', 1)
        
        # 2. Check for $(basename $var) command substitution patterns
        if '$(basename' in var_value:
            self.requires_os = True
            self.requires_sys = True
            
            # Extract the variable inside basename (e.g., $item)
            # This regex grabs whatever is inside $(basename ...)
            match = re.search(r'\$\(basename\s+\$?([A-Za-z0-9_]+)\)', var_value)
            if match:
                target_var = match.group(1)
                
                # Strip out the bash string parts to construct a clean Python f-string
                # e.g., "$2/$(basename $item).zip" -> f"{sys.argv[2]}/{os.path.basename(item)}.zip"
                clean_value = var_value.replace('"', '').replace("'", "")
                
                # Replace the $2 or $1 targets
                clean_value = clean_value.replace('$1', '{sys.argv[1]}')\
                                          .replace('$2', '{sys.argv[2]}')
                
                # Replace the actual $(basename ...) block with the Python equivalent
                clean_value = re.sub(r'\$\(basename\s+\$?[A-Za-z0-9_]+\)', f'{{os.path.basename({target_var})}}', clean_value)
                
                return f"{var_name} = f'{clean_value}'"

        if '$1' in var_value or '$2' in var_value:
            self.requires_sys = True

        # Fallback default assignment handling
        processed = raw_assignment.replace('$1', 'sys.argv[1]')\
                                  .replace('$2', 'sys.argv[2]')
        return processed


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