"""
NINA Modular Cognitive Layer Base Interfaces
Defines abstract/base interfaces for hot-swappable cognitive modules.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

class CognitiveModule(ABC):
    """Base class for all hot-swappable cognitive modules."""
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        pass


class BasePlanner(CognitiveModule):
    """Interface for cognitive planners."""
    @abstractmethod
    async def generate_plan(self, goal: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Decomposes a high-level goal into structured tasks."""
        pass


class BaseReflector(CognitiveModule):
    """Interface for cognitive reflection/critique modules."""
    @abstractmethod
    async def reflect(self, goal: str, execution_trace: List[tuple[str, str]]) -> str:
        """Analyzes execution history and generates corrective strategies.
        
        MUST return a JSON string with keys:
          - should_revise: bool
          - reason: str (one sentence explanation)
        Example: '{"should_revise": true, "reason": "Agent is looping on the same tool."}'
        """
        pass


class BaseEvaluator(CognitiveModule):
    """Interface for step-by-step or final answer evaluation."""
    @abstractmethod
    async def evaluate(self, goal: str, result: str, trace: List[tuple[str, str]]) -> Dict[str, Any]:
        """Evaluates output quality, returning verification score and suggestions.
        
        MUST return a dict with keys:
          - score: int (0-100; 0 on failure/exception, never 100 on exception)
          - matches_goal: bool
          - issues: List[str]
          - suggestions: List[str]
        """
        pass


class BaseVerifier(CognitiveModule):
    """Interface for syntax, import, and logic verification."""
    @abstractmethod
    async def verify(self, code_or_content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Validates syntactic or logical correctness."""
        pass
