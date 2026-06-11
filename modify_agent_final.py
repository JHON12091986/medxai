with open("core/agent.py", "r") as f:
    content = f.read()

system_frame_search = """        # System frame injected once — never repeated in step loop
        system_frame = (
            f"Goal: {goal}\\n"
            f"Memory: {context}\\n"
            "THINK -> PLAN -> ACT each step.\\n"
            "TOOL:web INPUT:query | TOOL:browser INPUT:url | TOOL:shell INPUT:cmd | TOOL:system INPUT:status\\n"
            "FINAL:answer when done.\\n"
            "RULE: live data/prices/news — MUST use TOOL:web first."
        )"""

system_frame_replace = """        # System frame injected once — never repeated in step loop
        # F-03x: Strip redundant instructions if routing through NinaGate (AG-M-10)
        from urllib.parse import urlparse
        api_base = getattr(self.config, "onebrain_api_base", "") or ""
        parsed_url = urlparse(api_base)

        if parsed_url.port == 8765 or "8765" in api_base:
            system_frame = f"Goal: {goal}\\nMemory: {context}"
        else:
            system_frame = (
                f"Goal: {goal}\\n"
                f"Memory: {context}\\n"
                "THINK -> PLAN -> ACT each step.\\n"
                "TOOL:web INPUT:query | TOOL:browser INPUT:url | TOOL:shell INPUT:cmd | TOOL:system INPUT:status\\n"
                "FINAL:answer when done.\\n"
                "RULE: live data/prices/news — MUST use TOOL:web first."
            )"""

content = content.replace(system_frame_search, system_frame_replace)

with open("core/agent.py", "w") as f:
    f.write(content)

print("Re-applied core/agent.py modifications with URL parsing.")
