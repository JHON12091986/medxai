"""
NINA Cognitive Module Registry
Enables dynamic discovery and hot-swapping of cognitive modules.
"""
from __future__ import annotations
from typing import Dict
from .base import CognitiveModule

class CognitiveRegistry:
    def __init__(self) -> None:
        self._modules: Dict[str, CognitiveModule] = {}

    def register(self, module: CognitiveModule) -> None:
        if not hasattr(module, "name") or not module.name:
            raise ValueError(f"CognitiveModule missing .name attribute: {module!r}")
        self._modules[module.name] = module

    def get(self, name: str) -> CognitiveModule:
        if name not in self._modules:
            available = list(self._modules.keys())
            raise KeyError(f"Cognitive module '{name}' not found. Registered: {available}")
        return self._modules[name]

    def has(self, name: str) -> bool:
        return name in self._modules

    def list_modules(self) -> Dict[str, str]:
        return {name: mod.version for name, mod in self._modules.items()}

    def reset(self) -> None:
        """Clear all registered modules. Use in tests and hot-reload only."""
        self._modules.clear()

# Global shared registry
registry = CognitiveRegistry()
