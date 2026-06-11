with open("core/nina.py", "r") as f:
    content = f.read()

prompt_search = """        self.system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            datetime=time.strftime("%Y-%m-%dT%H:%M:%S+0600"), memory_context="")

        self.system_prompt += \"\"\"

## RESPONSE STYLE & FORMATTING (enforce always)
- Lead directly with the core answer. No introduction, no conversational preamble.
- Default to extreme conciseness: 1-3 sentences maximum, unless the user explicitly requests details or code.
- Lists only for 3+ discrete items. No bullet soup.
- Prefer exact numbers over vague quantities.
- If unsure, say so in one line.
- Telegram: Use Telegram-friendly Markdown (bold for emphasis, inline code/code blocks for commands, concise bullets). Keep the response under 1000 characters.
\"\"\""""

prompt_replace = """        # If routing through NinaGate, strip redundant instructions
        if "8765" in getattr(self.config, "onebrain_api_base", ""):
            self.system_prompt = ""
            if hasattr(self.router, "http") and self.router.http:
                self.router.http.headers["X-NINA-ROLE"] = "agent"
        else:
            self.system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
                datetime=time.strftime("%Y-%m-%dT%H:%M:%S+0600"), memory_context="")
            self.system_prompt += \"\"\"

## RESPONSE STYLE & FORMATTING (enforce always)
- Lead directly with the core answer. No introduction, no conversational preamble.
- Default to extreme conciseness: 1-3 sentences maximum, unless the user explicitly requests details or code.
- Lists only for 3+ discrete items. No bullet soup.
- Prefer exact numbers over vague quantities.
- If unsure, say so in one line.
- Telegram: Use Telegram-friendly Markdown (bold for emphasis, inline code/code blocks for commands, concise bullets). Keep the response under 1000 characters.
\"\"\""""

content = content.replace(prompt_search, prompt_replace)

with open("core/nina.py", "w") as f:
    f.write(content)

print("Re-applied core/nina.py modifications.")
