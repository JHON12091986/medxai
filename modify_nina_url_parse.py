with open("core/nina.py", "r") as f:
    content = f.read()

search = """        # If routing through NinaGate, strip redundant instructions
        if "8765" in getattr(self.config, "onebrain_api_base", ""):
            self.system_prompt = ""
            if hasattr(self.router, "http") and self.router.http:
                self.router.http.headers["X-NINA-ROLE"] = "agent"
        else:"""

replace = """        # If routing through NinaGate, strip redundant instructions
        from urllib.parse import urlparse
        api_base = getattr(self.config, "onebrain_api_base", "") or ""
        parsed_url = urlparse(api_base)

        if parsed_url.port == 8765 or "8765" in api_base:
            self.system_prompt = ""
            if hasattr(self.router, "http") and self.router.http:
                self.router.http.headers["X-NINA-ROLE"] = "agent"
        else:"""

content = content.replace(search, replace)

with open("core/nina.py", "w") as f:
    f.write(content)

print("Updated core/nina.py with URL parsing.")
