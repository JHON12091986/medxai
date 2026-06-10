import json

with open("core/observability.py", "r") as f:
    content = f.read()

new_content = content.replace(
    'logger.info("nina_telemetry", **self.to_dict())',
    'logger.info(json.dumps(self.to_dict()))'
)

with open("core/observability.py", "w") as f:
    f.write(new_content)
