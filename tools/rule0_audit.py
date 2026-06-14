import json
import os
from datetime import datetime

def run_rule0_audit(scratchpad_path="/home/aibony/nina/data/gemini_scratch.jsonl", agents_md_path="/home/aibony/nina/AGENTS.md"):
    violations = []
    banned_tools = {}

    # Parse AGENTS.md to get banned tools and their nf equivalents
    # This is a simplified parser and might need refinement
    with open(agents_md_path, 'r') as f:
        content = f.read()
        banned_table_start = content.find("### BANNED TOOL DISPATCH TABLE:")
        banned_table_end = content.find("### ALLOWED — These native calls are always legitimate:")
        
        if banned_table_start != -1 and banned_table_end != -1:
            table_content = content[banned_table_start:banned_table_end]
            for line in table_content.split('
'):
                if line.startswith('| ') and 'nf' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 3:
                        banned_call = parts[1].split(':')[0].strip() # Get tool name, e.g., 'read_file' from 'read_file (existing file)'
                        nf_equivalent = parts[2].strip().split(' ')[0] # Get nf command, e.g., 'nf' from 'nf file read'
                        if banned_call and nf_equivalent:
                            banned_tools[banned_call] = nf_equivalent

    # Audit gemini_scratch.jsonl for violations
    if not os.path.exists(scratchpad_path):
        return ["RULE0_AUDIT_ERROR: Scratchpad file not found."]

    with open(scratchpad_path, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line)
                action = entry.get('action')
                detail = entry.get('detail', '')

                # Simple check for read_file calls
                if action == 'read' and 'read_file' in detail:
                    if 'read_file' in banned_tools:
                        violations.append(f"RULE0_VIOLATION: Used 'read_file' - should have used '{banned_tools['read_file']}'. Detail: {detail}")
                elif action == 'shell':
                    command = entry.get('command', '')
                    # Check for banned shell commands like 'cat', 'grep', 'ls', 'find'
                    for banned_shell_cmd in ['cat', 'grep', 'ls', 'find', 'head', 'tail', 'git log', 'git diff', 'git status', 'git blame']:
                        if command.startswith(banned_shell_cmd):
                            if banned_shell_cmd in banned_tools: # need to map these to their actual nf equivalents in the table
                                violations.append(f"RULE0_VIOLATION: Used '{banned_shell_cmd}' via run_shell_command - should have used '{banned_tools.get(banned_shell_cmd, 'nf equivalent')}'")
                            else: # Fallback if not perfectly mapped in the table parser
                                violations.append(f"RULE0_VIOLATION: Used '{banned_shell_cmd}' via run_shell_command - should have used an 'nf equivalent'")
            except json.JSONDecodeError:
                violations.append(f"RULE0_AUDIT_ERROR: Malformed JSON line in scratchpad: {line.strip()}")
    
    return violations

if __name__ == "__main__":
    audit_results = run_rule0_audit()
    if audit_results:
        print("RULE0 Audit Findings:")
        for violation in audit_results:
            print(f"- {violation}")
    else:
        print("RULE0 Audit: No violations found.")
