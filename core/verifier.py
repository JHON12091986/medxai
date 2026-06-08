import logging
import json
from dataclasses import dataclass

logger = logging.getLogger("nina.verifier")

@dataclass
class VerificationResult:
    passed: bool
    reason: str
    score: float
    check_name: str

class StepVerifier:
    def verify_non_empty(self, output) -> VerificationResult:
        if output is None:
            passed, score, reason = False, 0.0, "output is None"
        elif isinstance(output, str) and output == "":
            passed, score, reason = False, 0.0, "output is empty string"
        elif isinstance(output, list) and output == []:
            passed, score, reason = False, 0.0, "output is empty list"
        elif isinstance(output, dict) and output == {}:
            passed, score, reason = False, 0.0, "output is empty dict"
        elif isinstance(output, bool) and output is False:
            passed, score, reason = False, 0.0, "output is False"
        elif isinstance(output, int) and not isinstance(output, bool) and output == 0:
            passed, score, reason = False, 0.0, "output is integer 0"
        else:
            passed, score, reason = True, 1.0, "output is non-empty"

        logger.info(json.dumps({
            "event": "verify",
            "check": "non_empty",
            "passed": passed,
            "output_type": type(output).__name__
        }))

        return VerificationResult(
            passed=passed,
            reason=reason,
            score=score,
            check_name="non_empty"
        )

def is_valid_output(output) -> bool:
    verifier = StepVerifier()
    result = verifier.verify_non_empty(output)
    return result.passed
