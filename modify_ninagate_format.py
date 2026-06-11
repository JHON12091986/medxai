with open("ninagate/main.py", "r") as f:
    content = f.read()

search = """        # Get optional formatting vars from payload (or default to empty)
        fmt_vars = payload.get("nina_template_vars", {})
        dt = fmt_vars.get("datetime", time.strftime("%Y-%m-%dT%H:%M:%S+0600"))
        ctx = fmt_vars.get("memory_context", "")
        formatted_prompt = system_templates[role].format(datetime=dt, memory_context=ctx)"""

replace = """        # Determine template variables
        import datetime
        dt = time.strftime("%Y-%m-%dT%H:%M:%S+0600")

        # Try to dynamically populate variables if present in the template,
        # using whatever context we can extract or empty defaults.
        # But for 'agent' template, we know it needs {datetime} and {memory_context}.
        # For security and generic support, we format with basic defaults.
        try:
            formatted_prompt = system_templates[role].format(datetime=dt, memory_context="")
        except KeyError:
            # Fallback if format string contains unknown keys
            formatted_prompt = system_templates[role]"""

content = content.replace(search, replace)

with open("ninagate/main.py", "w") as f:
    f.write(content)

print("Updated ninagate/main.py formatting logic.")
