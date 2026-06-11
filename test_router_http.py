import re

with open("core/router.py", "r") as f:
    code = f.read()

m = re.search(r'async def initialize\(self\):.*?self\.http = .*?', code, re.DOTALL)
if m:
    print(m.group(0))
