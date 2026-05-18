import sys
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
        """
        Translates arguments, flags, and patterns strictly conforming to the 
        Python Shell Extension PEG grammar rules.
        """
        word_value = node.word
        
        # 1. Fix for lost spaces (e.g., ' ') -> must be an explicit string
        if word_value == " ":
            return '" "'

        # 2. If it is already explicitly quoted in the input, strip bashlex artifacts
        # and normalize it to double quotes for the PEG parser's `strings` rule
        if (word_value.startswith("'") and word_value.endswith("'")) or \
           (word_value.startswith('"') and word_value.endswith('"')):
            content = word_value[1:-1]
            return f'"{content}"'

        # 3. STRICT GRAMMAR SANITIZATION:
        # Check if the word contains characters that are NOT valid Python NAME tokens, 
        # or do not match your allowed flags (op='-' n=NAME) or variables (op='$' n=NAME).
        # Characters like \, [, ], ., -, and digits in argument positions must be strings.
        special_shell_chars = ['\\', '[', ']', '.', '*', '?', '{', '}', '(', ')']
        
        contains_special = any(char in word_value for char in special_shell_chars)
        is_complex_flag = word_value.startswith('-') and any(char in word_value[1:] for char in ['-', '.', '/', '\\'])
        is_range_or_num = any(char.isdigit() for char in word_value) and '-' in word_value

        if contains_special or is_complex_flag or is_range_or_num:
            # Escape internal backslashes for safe Python string compilation
            safe_value = word_value.replace('\\', '\\\\')
            return f'"{safe_value}"'
                
        # 4. Valid plain literals (e.g., sort, uniq, $1, -nr) flow through cleanly
        return word_value

    def visit_redirect(self, node) -> str:
        """Translates file redirections cleanly by tracking direction via node.type"""
        target_file = self.visit(node.output)
        
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


def run_verification_tests(transpiler):
    """Runs the 2 regression tests automatically on startup to verify stability."""
    print("====================================================")
    print("        RUNNING TRANSPILER VERIFICATION TESTS       ")
    print("====================================================")
    
    # Test 1: Cut parameter spacing regression
    bash_input_1 = "cat $1 | cut -d ' ' -f 2"
    dsl_output_1 = transpiler.transpile(bash_input_1)
    print(f"Test 1 [Bash]: {bash_input_1}")
    print(f"Test 1 [ DSL]: {dsl_output_1}")
    print("-" * 52)
    
    # Test 2: Directional stream inversion regression
    bash_input_2 = "cat < input.txt | grep error > output.log"
    dsl_output_2 = transpiler.transpile(bash_input_2)
    print(f"Test 2 [Bash]: {bash_input_2}")
    print(f"Test 2 [ DSL]: {dsl_output_2}")
    print("====================================================\n")


def interactive_loop():
    transpiler = BashToDSLTranspiler()
    
    # 1. Boot up validation tests first
    run_verification_tests(transpiler)
    
    # 2. Enter continuous prompt engine
    print("====================================================")
    print("  BASH TO PYTHON-SHELL EXTENSION TRANSPILER (CLI)   ")
    print("====================================================")
    print("Instructions:")
    print("  - Type or paste your Bash code below.")
    print("  - For multi-line code blocks, type 'MULTILINE' to start.")
    print("  - Type 'exit' or 'quit' to close the program.\n")

    while True:
        try:
            user_input = input("bash> ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
                
            # Handle block structures
            if user_input.upper() == 'MULTILINE':
                print("--- Entering Multi-line Mode (Type 'END' on a clean line to finish) ---")
                buffer = []
                while True:
                    line = input()
                    if line.strip().upper() == 'END':
                        break
                    buffer.append(line)
                user_input = "\n".join(buffer)
                print("--- Processing Code Block ---")

            # Transpile the active payload
            dsl_output = transpiler.transpile(user_input)
            
            print("\n--- Extended Python-Shell Syntax ---")
            print(dsl_output)
            print("------------------------------------\n")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\n[Error]: {e}\n")


if __name__ == "__main__":
    interactive_loop()