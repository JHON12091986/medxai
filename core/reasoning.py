"""
NINA Reasoning Kernel — Claude-inspired thinking harness.
Upgraded with 5 logic gates:
  1. ConstitutionalGate    — validate outputs against core principles
  2. MissionMemoryCarrier  — compressed context injected into every sub-task
  3. ToolFirstReflex       — prefer tools over text generation
  4. SycophancyDetector    — flag outputs that merely agree
  5. ContradictionDetector — surface conflicts between parallel results
Part of NINA Swarm v1.
"""
from __future__ import annotations
import re
from typing import List, Dict, Optional


# ── Thinking Scaffold ───────────────────────────────────────────────────────────

CLAUDE_THINKING_SCAFFOLD = """
<thinking>
1. GOAL ANALYSIS: What is the user actually asking for? What is the hidden intent?
2. CONTEXTUAL AWARENESS: What already exists in the codebase? What are the dependencies?
3. RISK ASSESSMENT: What could break? Any security or stability concerns?
4. ALTERNATIVE STRATEGIES: Is there a simpler or more idiomatic way?
5. DEVIL'S ADVOCATE: Why might my proposed solution be wrong?
6. ERROR PATHS: Edge cases? How should they be handled?
7. TOOL CHECK: Can a tool call answer this more reliably than generating text?
8. FINAL PLAN: Step-by-step execution path.
9. POST-TASK REVIEW: How can this implementation be optimised? (Required after every FINAL)
</thinking>
"""


# ── Constitutional Principles ──────────────────────────────────────────────────────

CONSTITUTIONAL_PRINCIPLES = [
    "Helpfulness: Response must directly address the user's goal with actionable steps.",
    "Honesty: State uncertainty plainly. Never hallucinate capabilities or tool results.",
    "Harmlessness: No sensitive data leaked; no destructive commands without confirmation.",
    "Nuance: Match technical depth and professional tone of a senior engineer.",
    "Anti-Sycophancy: Push back on flawed requests. Propose better alternatives when user's path is suboptimal.",
    "Mission Fidelity: Never drift from the root goal even when handling sub-tasks.",
    "Tool Preference: Prefer tool execution over text generation for verifiable facts.",
]


# ── Gate 1: ConstitutionalGate ───────────────────────────────────────────────────────

class ConstitutionalGate:
    """
    Checks any LLM output against NINA's constitutional principles.
    Returns (passed: bool, violations: List[str]).
    """
    VIOLATION_PATTERNS = [
        # Hallucination indicators
        (r"i (am|can|will) (definitely|certainly|absolutely)", "Overconfident claim"),
        (r"100%\s*(sure|certain|accurate|correct)",             "Overconfident claim"),
        # Harmful command patterns
        (r"rm -rf /(?!home|tmp|var)",                           "Potentially destructive command"),
        (r"DROP (TABLE|DATABASE|SCHEMA)",                       "Destructive SQL"),
        # Credential leakage
        (r"(api_key|password|secret)\s*=\s*['\"][^'\"]{8,}",   "Possible credential in output"),
    ]

    @classmethod
    def validate(cls, response: str) -> tuple[bool, List[str]]:
        violations = []
        for pattern, label in cls.VIOLATION_PATTERNS:
            if re.search(pattern, response, re.IGNORECASE):
                violations.append(label)
        return len(violations) == 0, violations

    @classmethod
    def inject_principles(cls) -> str:
        """Returns a formatted principle block for system prompts."""
        return "## CONSTITUTIONAL GUIDELINES:\n" + "\n".join(
            f"- {p}" for p in CONSTITUTIONAL_PRINCIPLES
        )


# ── Gate 2: MissionMemoryCarrier ──────────────────────────────────────────────────────

class MissionMemoryCarrier:
    """
    Ensures every sub-task prompt carries a compressed ≤500-token
    representation of the root mission. Prevents sub-agents from
    drifting away from the original objective.
    """

    MAX_TOKENS = 500
    CHARS_PER_TOKEN = 4  # conservative estimate

    @classmethod
    def wrap(cls, prompt: str, root_goal: str,
             completed_summaries: Optional[List[str]] = None,
             constraints: Optional[List[str]] = None) -> str:
        summaries_text = ""
        if completed_summaries:
            recent = completed_summaries[-3:]  # keep last 3
            summaries_text = " | ".join(recent)

        constraints_text = "; ".join(constraints or [])

        # Build compact mission block
        mission_block = (
            f"[MISSION MEMORY — do not lose sight of this]\n"
            f"ROOT GOAL: {root_goal[:200]}\n"
            f"CONSTRAINTS: {constraints_text[:100]}\n"
            f"PRIOR WORK: {summaries_text[:200]}\n"
            f"[END MISSION MEMORY]\n\n"
        )

        # Hard-trim to 500 tokens
        max_chars = cls.MAX_TOKENS * cls.CHARS_PER_TOKEN
        if len(mission_block) > max_chars:
            mission_block = mission_block[:max_chars] + "...\n\n"

        return mission_block + prompt


# ── Gate 3: ToolFirstReflex ─────────────────────────────────────────────────────────

class ToolFirstReflex:
    """
    Before generating a text answer, checks whether a tool call
    would answer the prompt more reliably.
    Returns (should_use_tool: bool, suggested_tool: str | None).
    """
    # Maps keyword patterns → tool name
    TOOL_TRIGGERS: List[tuple] = [
        (r"(read|open|show|print|cat)\s+.+\.(py|json|yaml|md|txt|toml)", "read_file"),
        (r"(run|execute|check|test)\s+(the\s+)?(tests?|pytest|unittest)",  "shell"),
        (r"(git (log|diff|status|blame))",                                 "shell"),
        (r"(list|find|search)\s+(file|dir|folder|path)",                   "shell"),
        (r"(curl|wget|http|api|endpoint|request)",                         "http"),
        (r"(memory|recall|remember|past session)",                         "memory"),
        (r"(quota|usage|limit|remaining)",                                  "ninagate_status"),
    ]

    @classmethod
    def check(cls, prompt: str) -> tuple[bool, Optional[str]]:
        for pattern, tool in cls.TOOL_TRIGGERS:
            if re.search(pattern, prompt, re.IGNORECASE):
                return True, tool
        return False, None

    @classmethod
    def inject_directive(cls) -> str:
        return (
            "TOOL-FIRST RULE: Before generating a text answer, check if a tool call "
            "would provide a more accurate or verifiable result. If so, use the tool first.\n"
        )


# ── Gate 4: SycophancyDetector ───────────────────────────────────────────────────────

class SycophancyDetector:
    """
    Detects whether an LLM response merely agrees with / mirrors the
    input prompt without adding genuine new information or critique.
    """
    HOLLOW_OPENERS = [
        "great idea", "absolutely", "certainly, ", "of course",
        "you're right", "you are right", "i agree completely",
        "that's a great", "excellent question", "great question",
        "as you suggested", "as you mentioned", "as you noted",
        "definitely", "i completely agree", "perfect idea",
        "you've made an excellent", "i totally agree",
    ]

    SUBSTANCE_INDICATORS = [
        "however", "on the other hand", "a better approach",
        "alternatively", "caution:", "risk:", "edge case",
        "consider instead", "this could break", "potential issue",
        "i'd suggest reconsidering", "one problem with",
    ]

    @classmethod
    def score(cls, response: str) -> float:
        """
        Returns a sycophancy score 0.0–1.0.
        0.0 = highly sycophantic, 1.0 = genuinely substantive.
        """
        lower = response.lower()
        sycophancy_hits = sum(1 for p in cls.HOLLOW_OPENERS if lower.startswith(p)
                              or f" {p} " in lower)
        substance_hits = sum(1 for s in cls.SUBSTANCE_INDICATORS if s in lower)

        raw = 1.0 - (sycophancy_hits * 0.15) + (substance_hits * 0.10)
        return max(0.0, min(1.0, raw))

    @classmethod
    def is_sycophantic(cls, response: str, threshold: float = 0.45) -> bool:
        return cls.score(response) < threshold

    @classmethod
    def inject_directive(cls) -> str:
        return (
            "ANTI-SYCOPHANCY RULE: Do not open with agreement, flattery, or validation. "
            "If the request has flaws, state them. Prefer pushback over agreement. "
            "Add genuine value beyond mirroring the user's premise.\n"
        )


# ── Gate 5: ContradictionDetector ─────────────────────────────────────────────────────

class ContradictionDetector:
    """
    When merging parallel results, detects logical conflicts
    and surfaces them explicitly rather than silently averaging.
    """
    NEGATION_PAIRS = [
        ("will",   "will not"),    ("is",      "is not"),
        ("can",    "cannot"),      ("should",  "should not"),
        ("true",   "false"),       ("enable",  "disable"),
        ("add",    "remove"),      ("start",   "stop"),
        ("always", "never"),       ("success", "failure"),
    ]

    @classmethod
    def find(cls, results: Dict[str, str]) -> List[Dict]:
        """
        Args:
            results: dict of {label: text}
        Returns:
            list of {label_a, label_b, conflict_phrase, excerpt_a, excerpt_b}
        """
        conflicts = []
        items = list(results.items())
        for i, (la, ra) in enumerate(items):
            for lb, rb in items[i + 1:]:
                for pos, neg in cls.NEGATION_PAIRS:
                    if pos in ra.lower() and neg in rb.lower():
                        conflicts.append({
                            "label_a": la, "label_b": lb,
                            "conflict": f"'{pos}' vs '{neg}'",
                            "excerpt_a": ra[:100],
                            "excerpt_b": rb[:100],
                        })
        return conflicts

    @classmethod
    def build_resolution_prompt(cls, conflicts: List[Dict],
                                root_goal: str) -> str:
        lines = [f"[CONFLICT RESOLUTION REQUEST]\nRoot goal: {root_goal}\n"]
        for c in conflicts:
            lines.append(
                f"CONFLICT: '{c['conflict']}'\n"
                f"  Source A ({c['label_a']}): {c['excerpt_a']}\n"
                f"  Source B ({c['label_b']}): {c['excerpt_b']}\n"
            )
        lines.append(
            "Resolve each conflict explicitly. Do not average. "
            "State which position is correct and why."
        )
        return "\n".join(lines)


# ── ReasoningKernel (main public interface, backward-compatible) ─────────────────

class ReasoningKernel:
    """
    Unified entry point. Composes all 5 gates into a coherent system frame.
    Backward-compatible with callers that use get_system_frame().
    """

    gate_constitutional = ConstitutionalGate()
    gate_mission        = MissionMemoryCarrier()
    gate_tool_first     = ToolFirstReflex()
    gate_sycophancy     = SycophancyDetector()
    gate_contradiction  = ContradictionDetector()

    @staticmethod
    def get_system_frame(goal: str, context: str = "") -> str:
        """
        Build a full system prompt frame with all gates active.
        Drop-in replacement for the previous get_system_frame().
        """
        principles = ConstitutionalGate.inject_principles()
        tool_rule  = ToolFirstReflex.inject_directive()
        syco_rule  = SycophancyDetector.inject_directive()

        return (
            f"Goal: {goal}\n"
            f"Memory: {context}\n\n"
            "## REASONING PROTOCOL (MANDATORY):\n"
            "You MUST use the following scaffold for every complex decision:\n"
            f"{CLAUDE_THINKING_SCAFFOLD}\n"
            f"{principles}\n\n"
            f"{tool_rule}\n"
            f"{syco_rule}\n"
            "THINK -> PLAN -> ACT each step.\n"
            "TOOL:web INPUT:query | TOOL:browser INPUT:url | "
            "TOOL:shell INPUT:cmd | TOOL:system INPUT:status\n"
            "FINAL:answer when done.\n"
        )

    @staticmethod
    def extract_thinking(response: str) -> str:
        match = re.search(r'<thinking>(.*?)</thinking>', response, re.DOTALL)
        return match.group(1).strip() if match else ""

    @staticmethod
    def filter_sycophancy(response: str) -> str:
        """Flags sycophantic responses. Returns response with prepended warning if flagged."""
        if SycophancyDetector.is_sycophantic(response):
            return "[SYCOPHANCY DETECTED — response may lack genuine critique]\n" + response
        return response

    @staticmethod
    def validate_output(response: str) -> tuple[bool, List[str]]:
        """Run ConstitutionalGate over a response. Returns (passed, violations)."""
        return ConstitutionalGate.validate(response)
