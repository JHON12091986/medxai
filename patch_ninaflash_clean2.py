import sys

with open("tools/ninaflash.py", "r") as f:
    content = f.read()

# Make sure we don't accidentally bloat with auto-formatting from the `ruff --fix`
# since that seems to have caused issues
