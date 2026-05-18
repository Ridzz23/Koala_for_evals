import bashlex

class BashToDSLTranspiler:
    def __init__(self):
        pass

    def transpile(self, bash_script: str) -> str:
        """Parses a full Bash script and recursively translates it."""
        try:
            ast_trees = bashlex.parse(bash_script)
        except Exception as e:
            return f"# Parsing Error: {e}"

        translated_lines = []
        for tree in ast_trees:
            translated_lines.append(self.visit(tree))
        
        return "\n".join(translated_lines)

    def visit(self, node) -> str:
        """Recursive descent router based on the node kind."""
        method_name = f"visit_{node.kind}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node) -> str:
        raise NotImplementedError(f"Bash node kind '{node.kind}' is not supported yet.")

    def visit_pipeline(self, node) -> str:
        """Translates pipelines, ignoring raw internal structural pipe operators."""
        commands = [part for part in node.parts if part.kind != 'pipe']
        parts = [self.visit(part) for part in commands]
        return " $| ".join(parts)

    def visit_command(self, node) -> str:
        """Translates a single command unit, its arguments, and its redirects."""
        cmd_parts = []
        redirect_parts = []

        for part in node.parts:
            if part.kind == 'redirect':
                redirect_parts.append(self.visit(part))
            else:
                cmd_parts.append(self.visit(part))

        base_command = " ".join(cmd_parts)
        
        if redirect_parts:
            return f"{base_command} {' '.join(redirect_parts)}"
        return base_command

    def visit_word(self, node) -> str:
        """Translates arguments, literal words, flags, and variables."""
        word_value = node.word
        
        # FIX FOR LOST SPACE: If the argument is literally just an empty space,
        # explicitly wrap it in quotes so it doesn't get swallowed by join()
        if word_value == " ":
            return '" "'
                
        return word_value

    def visit_redirect(self, node) -> str:
        """Translates file redirections cleanly by tracking direction via node.type"""
        # 1. Recursively get the target filename string
        target_file = self.visit(node.output)
        
        # 2. Enforce grammar rule: Target filenames must be written as quoted strings
        if not (target_file.startswith('"') and target_file.endswith('"')):
            target_file = f'"{target_file}"'

        # 3. Use node.type string evaluation to determine the stream direction
        if node.type == '<':
            return f'$< {target_file}'
        elif node.type == '>':
            return f'$> {target_file}'
        else:
            # Fallback wrapper safety guard for other structural variants (like >>, 2>)
            if '<' in node.type:
                return f'$< {target_file}'
            return f'$> {target_file}'

# --- Verification Run ---
if __name__ == "__main__":
    transpiler = BashToDSLTranspiler()
    
    # Test 1: Professor's cut command
    bash_input = "cat $1 | cut -d ' ' -f 2"
    dsl_output = transpiler.transpile(bash_input)
    print("=== FIXED TRANSPILER VERIFICATION ===")
    print(f"Bash: {bash_input}")
    print(f"DSL:  {dsl_output}\n")
    
    # Test 2: Redirection chains
    bash_input_2 = "cat < input.txt | grep error > output.log"
    dsl_output_2 = transpiler.transpile(bash_input_2)
    print(f"Bash: {bash_input_2}")
    print(f"DSL:  {dsl_output_2}")