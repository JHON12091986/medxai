with open("core/observability.py", "r") as f:
    content = f.read()

new_content = "import json\n" + content

with open("core/observability.py", "w") as f:
    f.write(new_content)
