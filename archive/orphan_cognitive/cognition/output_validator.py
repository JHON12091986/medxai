"""Output validator — checks every model response for quality signals: refusals, hallucination markers, truncation. Returns a ValidationResult so the caller can decide whether to retry."""

import dataclasses
import enum
import re
import logging
import typing

_ = (re, typing)


class ValidationIssue(enum.Enum):
    REFUSAL = "REFUSAL"
    HALLUCINATION_MARKER = "HALLUCINATION_MARKER"
    TRUNCATED = "TRUNCATED"
    TOO_SHORT = "TOO_SHORT"
    OK = "OK"

@dataclasses.dataclass
class ValidationResult:
    passed: bool
    issues: list[ValidationIssue]
    original_response: str
    cleaned_response: str

    @property
    def summary(self) -> str:
        if self.passed:
            return 'PASS'
        return 'FAIL: ' + ', '.join(i.value for i in self.issues)

REFUSAL_PHRASES: tuple = (
    "i'm sorry, i can't", "i cannot assist", "i'm not able to",
    "as an ai language model", "i don't have the ability to",
    "i apologize, but i cannot", "i'm unable to", "not able to help",
    "cannot provide", "i must decline"
)

HALLUCINATION_MARKERS: tuple = (
    "i don't have access to", "as of my knowledge cutoff",
    "as of my last update", "i don't have real-time",
    "i cannot browse", "my training data", "as of early 202",
    "i cannot access the internet", "i don't have the ability to search"
)

TRUNCATION_ENDINGS: tuple = (
    "...", "…", "to be continued", "[truncated]", "etc etc",
)

MIN_RESPONSE_TOKENS: int = 10


def _estimate_tokens(text: str) -> int:
    """Estimate token count as len(text.split())."""
    return len(text.split())

def validate_response(response: str, *, min_tokens: int = MIN_RESPONSE_TOKENS) -> ValidationResult:
    """Validate a model response. Returns ValidationResult. Always returns the original response in cleaned_response unless it is a pure refusal (then cleaned_response is empty string)."""
    issues = []
    text_lower = response.lower().strip()

    if any(phrase in text_lower for phrase in REFUSAL_PHRASES):
        issues.append(ValidationIssue.REFUSAL)
        cleaned = ''
    else:
        cleaned = response

    if any(marker in text_lower for marker in HALLUCINATION_MARKERS):
        issues.append(ValidationIssue.HALLUCINATION_MARKER)

    stripped_end = response.rstrip()
    if any(stripped_end.endswith(ending) for ending in TRUNCATION_ENDINGS):
        issues.append(ValidationIssue.TRUNCATED)

    if _estimate_tokens(response) < min_tokens:
        issues.append(ValidationIssue.TOO_SHORT)

    passed = len(issues) == 0 or (len(issues) == 1 and ValidationIssue.HALLUCINATION_MARKER in issues and ValidationIssue.REFUSAL not in issues)

    if not passed:
        logging.debug(f'[output_validator] issues={[i.value for i in issues]} response_preview={response[:60]!r}')

    return ValidationResult(
        passed=passed,
        issues=issues,
        original_response=response,
        cleaned_response=cleaned
    )

def should_retry(result: ValidationResult) -> bool:
    """True if the response failed and is worth retrying (not a refusal — refusals are deterministic and retrying wastes tokens)."""
    if ValidationIssue.REFUSAL in result.issues:
        return False
    return not result.passed

def build_retry_prompt(original_query: str, bad_response: str, result: ValidationResult) -> str:
    """Build a rephrased prompt for retry. Adds context about what went wrong."""
    _ = bad_response
    issues_str = result.summary
    return f'[NINA RETRY — previous response had issues: {issues_str}]\nPlease answer again more completely and accurately:\n{original_query}'
