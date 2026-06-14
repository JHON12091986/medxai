"""
NINA Reasoning Kernel — Claude-inspired thinking harness.
Implements multi-level reasoning, constitutional AI checks, and anti-sycophancy.
"""
from typing import List, Dict, Any

CLAUDE_THINKING_SCAFFOLD = """
<thinking>
1. GOAL ANALYSIS: What is the user actually asking for? What is the hidden intent?
2. CONTEXTUAL AWARENESS: What already exists in the codebase? What are the dependencies?
3. RISK ASSESSMENT: What could break? Are there any security or stability concerns?
4. ALTERNATIVE STRATEGIES: Is there a simpler or more idiomatic way?
5. DEVIL'S ADVOCATE: Why might my proposed solution be wrong?
6. ERROR PATHS: What are the edge cases? How should they be handled?
7. FINAL PLAN: Step-by-step execution path.
</thinking>
"""

CONSTITUTIONAL_PRINCIPLES = [
    "Helpfulness: The response must directly address the user's goal with actionable steps.",
    "Honesty: State uncertainty plainly. Do not hallucinate capabilities or tool results.",
    "Harmlessness: Ensure no sensitive data is leaked and no destructive commands are run without confirmation.",
    "Nuance: Capture the technical depth and professional tone appropriate for a senior engineer.",
    "Criticality (Anti-Sycophancy): Push back on logically flawed requests. Propose better alternatives if the user's path is suboptimal.",
]

class ReasoningKernel:
    @staticmethod
    def get_system_frame(goal: str, context: str) -> str:
        principles = "\n".join([f"- {p}" for p in CONSTITUTIONAL_PRINCIPLES])
        return (
            f"Goal: {goal}\n"
            f"Memory: {context}\n\n"
            "## REASONING PROTOCOL (MANDATORY):\n"
            "You MUST use the following scaffold for every complex decision:\n"
            f"{CLAUDE_THINKING_SCAFFOLD}\n"
            "## CONSTITUTIONAL GUIDELINES:\n"
            f"{principles}\n\n"
            "THINK -> PLAN -> ACT each step.\n"
            "TOOL:web INPUT:query | TOOL:browser INPUT:url | TOOL:shell INPUT:cmd | TOOL:system INPUT:status\n"
            "FINAL:answer when done.\n"
        )

    @staticmethod
    def extract_thinking(response: str) -> str:
        import re
        match = re.search(r'<thinking>(.*?)</thinking>', response, re.DOTALL)
        return match.group(1).strip() if match else ""

    @staticmethod
    def filter_sycophancy(response: str) -> str:
        # Implementation of anti-sycophancy logic
        # For now, it's enforced via the system prompt and the thinking scaffold
        return response
