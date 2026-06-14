import re
import sys
from pathlib import Path

def prune_content(text, ext):
    """
    Minifies code for AI context while preserving logic and structure.
    - Removes docstrings and single-line comments.
    - Strips leading/trailing whitespace.
    - Reduces consecutive newlines.
    """
    if ext == ".py":
        # Remove triple-quote docstrings
        text = re.sub(r'(""".*?"""|\'\'\'.*?\'\'\')', '', text, flags=re.DOTALL)
        # Remove single-line comments (ignoring shebang)
        lines = []
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#") and not line.startswith("#!"):
                continue
            # Remove inline comments (naive)
            if "#" in line:
                line = line.split("#")[0].rstrip()
            if line.strip() or not lines or lines[-1].strip():
                lines.append(line)
        return "\n".join(lines)
    
    elif ext == ".md":
        # Keep it simple for markdown, just reduce newlines
        return re.sub(r'\n{3,}', '\n\n', text)
    
    return text

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 context_pruner.py <file_path>")
        sys.exit(1)
    
    path = Path(sys.argv[1])
    if not path.exists():
        sys.exit(1)
        
    content = path.read_text(encoding="utf-8")
    pruned = prune_content(content, path.suffix)
    print(pruned)

if __name__ == "__main__":
    main()
