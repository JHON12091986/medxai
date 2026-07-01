import logging
import re

logger = logging.getLogger("nina.security")

class CircuitState:
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF-OPEN"

class BehavioralCircuitBreaker:
    def __init__(self, cost_limit: float = 0.25, max_tool_calls_per_run: int = 6):
        self.state = CircuitState.CLOSED
        self.session_cost = 0.0
        self.cost_limit = cost_limit
        self.max_tool_calls = max_tool_calls_per_run
        self.tool_call_count = 0
        self.consecutive_failures = 0

    def record_cost(self, cost: float) -> None:
        self.session_cost += cost
        if self.session_cost >= self.cost_limit:
            self.trip(f"Cost limit exceeded: ${self.session_cost:.4f} >= ${self.cost_limit:.4f}")

    def record_tool_call(self, tool_name: str, input_str: str) -> None:
        self.tool_call_count += 1
        if self.tool_call_count >= self.max_tool_calls:
            self.trip(f"Maximum tool calls exceeded: {self.tool_call_count} >= {self.max_tool_calls}")
        if self._is_dangerous_pattern(tool_name, input_str):
            self.trip(f"Dangerous command pattern detected in {tool_name}: '{input_str}'")

    def record_failure(self) -> None:
        self.consecutive_failures += 1
        if self.consecutive_failures >= 3:
            self.trip("Multiple consecutive step failures")

    def record_success(self) -> None:
        self.consecutive_failures = 0
        if self.state == CircuitState.HALF_OPEN:
            logger.info("Circuit Breaker transitioned HALF-OPEN -> CLOSED after successful step.")
            self.state = CircuitState.CLOSED

    def trip(self, reason: str) -> None:
        self.state = CircuitState.OPEN
        logger.critical(f"Circuit Breaker TRIPPED (State: OPEN) - Reason: {reason}")
        raise RuntimeError(f"Circuit Breaker TRIPPED (State: OPEN) - Reason: {reason}")

    def _is_dangerous_pattern(self, tool_name: str, input_str: str) -> bool:
        if tool_name == "shell":
            dangerous_exprs = [
                r"\brm\s+-rf\s+/",
                r"\brm\s+-rf\s+\*",
                r"\bdrop\s+table\b",
                r"\bdelete\s+from\b",
                r"\bformat\b",
                r":\(\)\{\s*:\s*\|\s*:\s*&\s*\}\s*;",  # Fork bomb
                r"/dev/sd[a-z]"
            ]
            for expr in dangerous_exprs:
                if re.search(expr, input_str, re.IGNORECASE):
                    return True
        return False
