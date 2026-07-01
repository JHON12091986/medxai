"""
NINA Modular Cognitive Layer
Decouples cognitive processes into standalone, hot-swappable modules.
"""
from __future__ import annotations
from .base import CognitiveModule, BasePlanner, BaseReflector, BaseEvaluator, BaseVerifier
from .planner import CognitivePlanner
from .reflector import CognitiveReflector
from .evaluator import CognitiveEvaluator
from .verifier import CognitiveVerifier
from .registry import registry, CognitiveRegistry

__all__ = [
    "CognitiveModule",
    "BasePlanner",
    "BaseReflector",
    "BaseEvaluator",
    "BaseVerifier",
    "CognitivePlanner",
    "CognitiveReflector",
    "CognitiveEvaluator",
    "CognitiveVerifier",
    "registry",
    "CognitiveRegistry",
]
