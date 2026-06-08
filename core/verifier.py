import logging
import json
import asyncio
from dataclasses import dataclass
from core.router import HybridRouter
from core.config import NinaConfig

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


    def verify_success_criteria(self, output, criteria: str) -> VerificationResult:
        prompt = f'Does this output satisfy the criteria? Output: <{output}>. Criteria: <{criteria}>. Reply with JSON only: {{"passed": true/false, "reason": "one sentence"}}'
        passed = False
        reason = "verification failed: unknown error"
        score = 0.0
        try:
            cfg = NinaConfig()
            router = HybridRouter(config=cfg)

            async def run_router():
                await router.initialize()
                return await router.single_turn(prompt, [])

            loop = asyncio.get_event_loop()
            if loop.is_running():
                import nest_asyncio
                nest_asyncio.apply()

            res_str = asyncio.run(run_router())
            try:
                if res_str.startswith("```json"):
                    res_str = res_str.split("```json")[1].split("```")[0].strip()
                elif res_str.startswith("```"):
                    res_str = res_str.split("```")[1].strip()
                res = json.loads(res_str)
                passed = bool(res.get("passed", False))
                reason = res.get("reason", "no reason provided")
                score = 1.0 if passed else 0.0
            except json.JSONDecodeError as e:
                reason = f"verification failed: {e}"
        except Exception as e:
            reason = f"verification failed: {e}"

        logger.info(json.dumps({
            "event": "verify",
            "check": "success_criteria",
            "passed": passed
        }))

        return VerificationResult(
            passed=passed,
            reason=reason,
            score=score,
            check_name="success_criteria"
        )

    def verify_numeric_range(self, output, min_val: float = None, max_val: float = None) -> VerificationResult:
        passed = False
        reason = ""
        score = 0.0

        try:
            val = float(output)
            passed = True
            score = 1.0

            if min_val is not None and val < min_val:
                passed = False
                score = 0.0
                reason = f"value {val} is outside range [{min_val}, {max_val}]"
            elif max_val is not None and val > max_val:
                passed = False
                score = 0.0
                reason = f"value {val} is outside range [{min_val}, {max_val}]"
            else:
                reason = "numeric value in range"

        except (ValueError, TypeError):
            passed = False
            score = 0.0
            reason = "output is not numeric"

        logger.info(json.dumps({
            "event": "verify",
            "check": "numeric_range",
            "passed": passed
        }))

        return VerificationResult(
            passed=passed,
            reason=reason,
            score=score,
            check_name="numeric_range"
        )

    def verify_schema(self, output: dict, required_keys: list) -> VerificationResult:
        passed = False
        reason = ""
        score = 0.0

        if not isinstance(output, dict):
            reason = "output is not a dictionary"
        else:
            missing = [k for k in required_keys if k not in output]
            if missing:
                reason = f"missing keys: {', '.join(missing)}"
            else:
                passed = True
                score = 1.0
                reason = "schema valid"

        logger.info(json.dumps({
            "event": "verify",
            "check": "schema",
            "passed": passed
        }))

        return VerificationResult(
            passed=passed,
            reason=reason,
            score=score,
            check_name="schema"
        )

    def verify_all(self, output, checks: list[dict]) -> list[VerificationResult]:
        results = []
        for check in checks:
            check_type = check.get("type")
            kwargs = {k: v for k, v in check.items() if k != "type"}

            if check_type == "non_empty":
                res = self.verify_non_empty(output)
            elif check_type == "numeric_range":
                res = self.verify_numeric_range(output, **kwargs)
            elif check_type == "schema":
                res = self.verify_schema(output, **kwargs)
            elif check_type == "success_criteria":
                res = self.verify_success_criteria(output, **kwargs)
            else:
                res = VerificationResult(passed=False, reason=f"unknown check type: {check_type}", score=0.0, check_name="unknown")

            results.append(res)
            if not res.passed:
                break

        return results


def is_valid_output(output) -> bool:
    verifier = StepVerifier()
    result = verifier.verify_non_empty(output)
    return result.passed
