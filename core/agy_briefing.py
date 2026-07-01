def generate_agy_brief(file_paths: list, task: str) -> str:
    import re
    briefs = []
    keywords = re.findall(r'\w+', task.lower())
    for path in file_paths:
        try:
            with open(path) as f:
                lines = f.readlines()
            relevant = [f"{path}:{i+1}: {l.rstrip()}" for i, l in enumerate(lines)
                       if any(kw in l.lower() for kw in keywords)][:10]
            briefs.extend(relevant)
        except FileNotFoundError:
            briefs.append(f"{path}: NOT FOUND")
    brief = " | ".join(briefs)
    result = f"CONTEXT: {brief[:1800]} | TASK: {task[:150]} | VERIFY: run pytest tests/"
    return result[:2000]
