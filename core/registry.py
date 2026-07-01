"""NINA capability registry — @nina_tool decorator for auto-registration of NinaFlash tool functions into config/capability_registry.yaml."""

import functools
import logging
import os

try:
    import yaml
except ImportError:
    yaml = None
    logging.warning("PyYAML not available. Capability registry will run in no-op mode.")

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'capability_registry.yaml')

def _load_registry() -> dict:
    """Load the capability registry YAML. Returns empty dict with tools/models lists if file missing or yaml unavailable."""
    if yaml is None:
        return {'tools': [], 'models': []}
    try:
        with open(REGISTRY_PATH, 'r') as f:
            registry = yaml.safe_load(f)
            if not registry:
                return {'tools': [], 'models': []}
            if 'tools' not in registry:
                registry['tools'] = []
            if 'models' not in registry:
                registry['models'] = []
            return registry
    except Exception as e:
        logging.warning(f"Failed to load registry: {e}")
        return {'tools': [], 'models': []}

def _save_registry(registry: dict) -> None:
    """Save registry dict back to YAML file. No-op if yaml unavailable."""
    if yaml is None:
        return
    try:
        with open(REGISTRY_PATH, 'w') as f:
            yaml.dump(registry, f, default_flow_style=False, allow_unicode=True)
    except Exception as e:
        logging.error(f"Failed to save registry: {e}")

def nina_tool(*, description: str, input_schema: dict | None = None, output_schema: dict | None = None, executor: str = 'ninaflash', quota_provider: str | None = None):
    """Decorator that registers a NinaFlash tool function into config/capability_registry.yaml. Usage: @nina_tool(description="...") def my_tool(...)."""
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        
        # We load and update the registry during decorator definition time as specified
        registry = _load_registry()
        tool_entry = {
            'id': fn.__name__,
            'description': description,
            'executor': executor,
            'input_schema': input_schema or {},
            'output_schema': output_schema or {},
            'quota_provider': quota_provider,
            'status': 'online'
        }
        
        # Check if a tool with id == fn.__name__ already exists
        tools = registry.get('tools', [])
        found = False
        for idx, tool in enumerate(tools):
            if tool.get('id') == fn.__name__:
                tools[idx] = tool_entry
                found = True
                break
        if not found:
            tools.append(tool_entry)
            
        registry['tools'] = tools
        _save_registry(registry)
        logging.info(f'[registry] registered tool: {fn.__name__}')
        
        # Returns fn unchanged
        return fn
    return decorator
