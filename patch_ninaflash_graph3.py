import sys

with open("tools/ninaflash.py", "r") as f:
    content = f.read()

target = """    try:
        try:
        print(json.dumps(graph, indent=2))
    except BrokenPipeError:
        import sys, os
        sys.stdout = open(os.devnull, 'w')
        sys.exit(0)
    except BrokenPipeError:"""

new_target = """    try:
        print(json.dumps(graph, indent=2))
    except BrokenPipeError:
        import sys, os
        sys.stdout = open(os.devnull, 'w')
        sys.exit(0)"""

if target in content:
    content = content.replace(target, new_target)
    with open("tools/ninaflash.py", "w") as f:
        f.write(content)
else:
    # Just fix manually using regex or lines
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line == "    try:":
            if lines[i+1] == "        try:":
                if lines[i+2] == "        print(json.dumps(graph, indent=2))":
                    lines.pop(i)
                    break
    content = '\n'.join(lines)
    with open("tools/ninaflash.py", "w") as f:
        f.write(content)
