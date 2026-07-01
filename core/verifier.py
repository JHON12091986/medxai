from typing import Any
import re
import logging
import json
import asyncio
from dataclasses import dataclass
from typing import List, Dict, Optional
from core.router import HybridRouter
from core.task_classifier import ClassifiedTask
from core.config import NinaConfig
logger = logging.getLogger('nina.verifier')

@dataclass
class VerificationResult:
    passed: bool
    reason: str
    score: float
    check_name: str

class StepVerifier:
    def verify_non_empty(self, output: Any) -> VerificationResult:
        if output is None:
            passed, score, reason = (False, 0.0, 'output is None')
        elif isinstance(output, str) and output == '':
            passed, score, reason = (False, 0.0, 'output is empty string')
        elif isinstance(output, list) and output == []:
            passed, score, reason = (False, 0.0, 'output is empty list')
        elif isinstance(output, dict) and output == {}:
            passed, score, reason = (False, 0.0, 'output is empty dict')
        elif isinstance(output, bool) and output is False:
            passed, score, reason = (False, 0.0, 'output is False')
        elif isinstance(output, int) and (not isinstance(output, bool)) and (output == 0):
            passed, score, reason = (False, 0.0, 'output is integer 0')
        else:
            passed, score, reason = (True, 1.0, 'output is non-empty')
        logger.info(json.dumps({'event': 'verify', 'check': 'non_empty', 'passed': passed, 'output_type': type(output).__name__}))
        return VerificationResult(passed=passed, reason=reason, score=score, check_name='non_empty')

    async def verify_success_criteria(self, output: Any, criteria: str) -> VerificationResult:
        prompt = f'Does this output satisfy the criteria? Output: <{output}>. Criteria: <{criteria}>. Reply with JSON only: {{"passed": true, "reason": "one sentence"}}'
        passed = False
        reason = 'verification failed: unknown error'
        score = 0.0
        try:
            cfg = NinaConfig()
            router = HybridRouter(config=cfg)
            await router.initialize()
            res_str = await router.single_turn(prompt, [])
            try:
                if '```json' in res_str:
                    res_str = res_str.split('```json')[1].split('```')[0].strip()
                elif '```' in res_str:
                    res_str = res_str.split('```')[1].split('```')[0].strip()
                res = json.loads(res_str.strip())
                passed = bool(res.get('passed', False))
                reason = res.get('reason', 'no reason provided')
                score = 1.0 if passed else 0.0
            except json.JSONDecodeError as e:
                reason = f'verification failed: invalid JSON response - {e}'
        except Exception as e:
            reason = f'verification failed: {e}'
        logger.info(json.dumps({'event': 'verify', 'check': 'success_criteria', 'passed': passed}))
        return VerificationResult(passed=passed, reason=reason, score=score, check_name='success_criteria')

    async def semantic_score(self, output: str, success_criteria: str) -> dict:
        prompt = f'Score this output 1-5 for how well it satisfies the criteria.\nCriteria: {success_criteria}\nOutput: {output}\nReply with JSON only: {{"score": N, "reason": "one sentence"}}'
        passed = False
        reason = 'verifier error'
        score = 0
        try:
            cfg = NinaConfig()
            router = HybridRouter(config=cfg)
            await router.initialize()
            task = ClassifiedTask(task_type='verification', estimated_tokens=200, is_parallel_candidate=False, is_sensitive=False)
            res_str = await router.route(prompt, [], task)
            try:
                if '```json' in res_str:
                    res_str = res_str.split('```json')[1].split('```')[0].strip()
                elif '```' in res_str:
                    res_str = res_str.split('```')[1].split('```')[0].strip()
                res = json.loads(res_str.strip())
                score = int(res.get('score', 0))
                reason = res.get('reason', 'no reason provided')
                passed = bool(score >= 3)
            except (json.JSONDecodeError, ValueError) as e:
                reason = f'verifier error: invalid JSON response - {e}'
        except Exception as e:
            reason = f'verifier error'
        logger.info(json.dumps({'event': 'verify', 'check': 'semantic_score', 'passed': passed, 'score': score}))
        return {'score': score, 'reason': reason, 'passed': passed}

    def verify_numeric_range(self, output: Any, min_val: float = None, max_val: float = None) -> VerificationResult:
        passed = False
        reason = ''
        score = 0.0
        try:
            val = float(output)
            passed = True
            score = 1.0
            if min_val is not None and val < min_val:
                passed = False
                score = 0.0
                reason = f'value {val} is below minimum {min_val}'
            elif max_val is not None and val > max_val:
                passed = False
                score = 0.0
                reason = f'value {val} is above maximum {max_val}'
            else:
                reason = 'numeric value in range'
        except (ValueError, TypeError):
            passed = False
            score = 0.0
            reason = 'output is not numeric'
        logger.info(json.dumps({'event': 'verify', 'check': 'numeric_range', 'passed': passed}))
        return VerificationResult(passed=passed, reason=reason, score=score, check_name='numeric_range')

    def _extract_numeric_value(self, expected, max_val, min_val, output, passed, reason, tolerance, value):
        if output is not None:
            if isinstance(output, (int, float)):
                if isinstance(output, bool):
                    reason = 'output is boolean, not numeric'
                else:
                    value = float(output)
            elif isinstance(output, str):
                match = re.search('[-+]?\\d*\\.?\\d+', output)
                if match:
                    try:
                        value = float(match.group())
                    except ValueError:
                        pass
            if value is not None:
                passed = True
                reason = 'numeric assertion passed'
                if expected is not None:
                    if abs(value - expected) > tolerance:
                        passed = False
                        reason = f'value {value} does not match expected {expected} within tolerance {tolerance}'
                if passed and min_val is not None:
                    if value < min_val:
                        passed = False
                        reason = f'value {value} is below minimum {min_val}'
                if passed and max_val is not None:
                    if value > max_val:
                        passed = False
                        reason = f'value {value} is above maximum {max_val}'
        return (passed, reason, value)

    def numeric_assert(self, output: str | int | float, min_val: float | None=None, max_val: float | None=None, expected: float | None=None, tolerance: float=0.01) -> dict:
        passed = False
        reason = 'output is not numeric or None'
        value = None
        passed, reason, value = self._extract_numeric_value(expected, max_val, min_val, output, passed, reason, tolerance, value)
        logger.info(json.dumps({'event': 'verify', 'check': 'numeric_assert', 'passed': passed, 'value': value}))
        return {'value': value, 'passed': passed, 'reason': reason}

    def verify_schema(self, output: dict, required_keys: List[str]) -> VerificationResult:
        passed = False
        reason = ''
        score = 0.0
        if not isinstance(output, dict):
            reason = 'output is not a dictionary'
        else:
            missing = [k for k in required_keys if k not in output]
            if missing:
                reason = f"missing keys: {', '.join(missing)}"
            else:
                passed = True
                score = 1.0
                reason = 'schema valid'
        logger.info(json.dumps({'event': 'verify', 'check': 'schema', 'passed': passed}))
        return VerificationResult(passed=passed, reason=reason, score=score, check_name='schema')

    async def verify_all(self, output: Any, checks: List[dict]) -> List[VerificationResult]:
        results = []
        for check in checks:
            check_type = check.get('type')
            kwargs = {k: v for k, v in check.items() if k != 'type'}
            if check_type == 'non_empty':
                res = self.verify_non_empty(output)
            elif check_type == 'numeric_range':
                res = self.verify_numeric_range(output, **kwargs)
            elif check_type == 'schema':
                res = self.verify_schema(output, **kwargs)
            elif check_type == 'success_criteria':
                res = await self.verify_success_criteria(output, **kwargs)
            else:
                res = VerificationResult(passed=False, reason=f'unknown check type: {check_type}', score=0.0, check_name='unknown')
            results.append(res)
            if not res.passed:
                break
        return results

def is_valid_output(output: Any) -> bool:
    verifier = StepVerifier()
    result = verifier.verify_non_empty(output)
    return result.passed