import re
with open("core/capabilities.py", "r") as f:
    content = f.read()
if "from typing import" not in content:
    content = "from typing import Optional, List\n" + content
elif "Optional" not in content:
    content = content.replace("from typing import", "from typing import Optional, List,")
elif "List" not in content:
    content = content.replace("from typing import Optional", "from typing import Optional, List")
with open("core/capabilities.py", "w") as f:
    f.write(content)
