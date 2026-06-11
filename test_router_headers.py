import re

with open("core/router.py", "r") as f:
    router_code = f.read()

# Let's see how headers are passed in _call_provider
matches = re.finditer(r'headers=({.*?})', router_code)
for m in matches:
    print(m.group(1))
