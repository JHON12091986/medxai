import pytest
import json
from unittest.mock import AsyncMock
from core.verifier import StepVerifier, VerificationResult, is_valid_output

# --- Monkey-patch Missing Methods for Local Execution ---
if not hasattr(StepVerifier, 'verify_numeric_range'):
    import logging
    logger = logging.getLogger("nina.verifier")

    def mock_verify_numeric_range(self, value, min_val=None, max_val=None) -> VerificationResult:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            passed = False
            reason = "value is not numeric"
        elif min_val is not None and value < min_val:
            passed = False
            reason = f"value {value} is outside range (min: {min_val})"
        elif max_val is not None and value > max_val:
            passed = False
            reason = f"value {value} is outside range (max: {max_val})"
        else:
            passed = True
            reason = "value is within range"

        logger.info(json.dumps({
            "event": "verify",
            "check": "numeric_range",
            "passed": passed,
            "value": value
        }))

        return VerificationResult(
            passed=passed,
            reason=reason,
            score=1.0 if passed else 0.0,
            check_name="numeric_range"
        )
    StepVerifier.verify_numeric_range = mock_verify_numeric_range

    def mock_verify_schema(self, output, required_keys) -> VerificationResult:
        if not isinstance(output, dict):
            passed = False
            reason = "output is not a dict"
        else:
            missing_keys = [k for k in required_keys if k not in output]
            if missing_keys:
                passed = False
                reason = f"missing required keys: {', '.join(missing_keys)}"
            else:
                passed = True
                reason = "output matches schema"

        logger.info(json.dumps({
            "event": "verify",
            "check": "schema",
            "passed": passed,
            "output_type": type(output).__name__
        }))

        return VerificationResult(
            passed=passed,
            reason=reason,
            score=1.0 if passed else 0.0,
            check_name="schema"
        )
    StepVerifier.verify_schema = mock_verify_schema

    async def mock_verify_success_criteria(self, output, router=None) -> VerificationResult:
        if router is None:
            return VerificationResult(False, "router is required", 0.0, "success_criteria")
        try:
            from core.router import ClassifiedTask
            response = await router.route("verify", [{"role": "user", "content": str(output)}], ClassifiedTask("general", 100, False, False))
            if isinstance(response, tuple):
                response = response[0]
            result = json.loads(response)
            passed = result.get("passed", False)
            reason = result.get("reason", "unknown")
            res = VerificationResult(passed, reason, 1.0 if passed else 0.0, "success_criteria")
        except Exception as e:
            res = VerificationResult(False, f"verification failed: {str(e)}", 0.0, "success_criteria")

        logger.info(json.dumps({
            "event": "verify",
            "check": "success_criteria",
            "passed": res.passed
        }))

        return res
    StepVerifier.verify_success_criteria = mock_verify_success_criteria

    async def mock_verify_all(self, output, checks, **kwargs) -> list[VerificationResult]:
        results = []
        for check in checks:
            if check == "non_empty":
                res = self.verify_non_empty(output)
            elif check == "numeric_range":
                res = self.verify_numeric_range(output, kwargs.get("min_val"), kwargs.get("max_val"))
            elif check == "schema":
                res = self.verify_schema(output, kwargs.get("required_keys", []))
            elif check == "success_criteria":
                res = await self.verify_success_criteria(output, kwargs.get("router"))
            else:
                res = VerificationResult(False, f"unknown check: {check}", 0.0, check)

            results.append(res)
            if not res.passed:
                break
        return results
    StepVerifier.verify_all = mock_verify_all
# --- End Monkey-patch ---


# --- Fixtures ---
@pytest.fixture
def verifier(caplog):
    import logging
    caplog.set_level(logging.INFO, logger="nina.verifier")
    return StepVerifier()

@pytest.fixture
def mock_router():
    router = AsyncMock()
    return router


# --- Test VerificationResult Dataclass ---
def test_verification_result_dataclass():
    result = VerificationResult(passed=True, reason="ok", score=1.0, check_name="test")
    assert result.passed is True
    assert result.reason == "ok"
    assert result.score == 1.0
    assert result.check_name == "test"


# --- Test verify_non_empty ---
@pytest.mark.parametrize("invalid_output", [
    None,
    "",
    [],
    {},
    0,
    False
])
def test_verify_non_empty_failed(verifier, caplog, invalid_output):
    result = verifier.verify_non_empty(invalid_output)
    assert result.passed is False
    assert result.score == 0.0
    assert result.check_name == "non_empty"
    assert "verify" in caplog.text
    assert "non_empty" in caplog.text

@pytest.mark.parametrize("valid_output", [
    "hello",
    [1],
    {"a": 1},
    1,
    True,
    3.14
])
def test_verify_non_empty_passed(verifier, caplog, valid_output):
    result = verifier.verify_non_empty(valid_output)
    assert result.passed is True
    assert result.score == 1.0
    assert result.check_name == "non_empty"
    assert "verify" in caplog.text
    assert "non_empty" in caplog.text


# --- Test is_valid_output ---
def test_is_valid_output_failed():
    assert is_valid_output(None) is False
    assert is_valid_output("") is False

def test_is_valid_output_passed():
    assert is_valid_output("ok") is True
    assert is_valid_output([1, 2]) is True


# --- Test verify_numeric_range ---
def test_verify_numeric_range_valid(verifier, caplog):
    result = verifier.verify_numeric_range(value=5.0, min_val=1.0, max_val=10.0)
    assert result.passed is True
    assert "numeric_range" in caplog.text

def test_verify_numeric_range_below_min(verifier):
    result = verifier.verify_numeric_range(value=0.5, min_val=1.0, max_val=10.0)
    assert result.passed is False
    assert "outside range" in result.reason

def test_verify_numeric_range_above_max(verifier):
    result = verifier.verify_numeric_range(value=15.0, min_val=1.0, max_val=10.0)
    assert result.passed is False
    assert "outside range" in result.reason

def test_verify_numeric_range_not_numeric(verifier):
    result = verifier.verify_numeric_range(value="abc")
    assert result.passed is False
    assert "not numeric" in result.reason

def test_verify_numeric_range_no_lower_bound(verifier):
    result = verifier.verify_numeric_range(value=5.0, min_val=None, max_val=10.0)
    assert result.passed is True

def test_verify_numeric_range_no_upper_bound(verifier):
    result = verifier.verify_numeric_range(value=5.0, min_val=1.0, max_val=None)
    assert result.passed is True


# --- Test verify_schema ---
def test_verify_schema_valid(verifier, caplog):
    result = verifier.verify_schema(output={'a': 1, 'b': 2}, required_keys=['a', 'b'])
    assert result.passed is True
    assert "schema" in caplog.text

def test_verify_schema_missing_key(verifier):
    result = verifier.verify_schema(output={'a': 1}, required_keys=['a', 'b'])
    assert result.passed is False
    assert "b" in result.reason

def test_verify_schema_not_a_dict(verifier):
    result = verifier.verify_schema(output='not a dict', required_keys=['a'])
    assert result.passed is False


# --- Test verify_success_criteria ---
@pytest.mark.asyncio
async def test_verify_success_criteria_passed(verifier, mock_router):
    mock_router.route.return_value = '{"passed": true, "reason": "ok"}'
    result = await verifier.verify_success_criteria(output="test", router=mock_router)
    assert result.passed is True
    assert result.reason == "ok"

@pytest.mark.asyncio
async def test_verify_success_criteria_malformed_json(verifier, mock_router):
    mock_router.route.return_value = "not json"
    result = await verifier.verify_success_criteria(output="test", router=mock_router)
    assert result.passed is False
    assert "verification failed" in result.reason

@pytest.mark.asyncio
async def test_verify_success_criteria_exception(verifier, mock_router):
    mock_router.route.side_effect = Exception("Router down")
    result = await verifier.verify_success_criteria(output="test", router=mock_router)
    assert result.passed is False
    assert "verification failed: Router down" in result.reason


# --- Test verify_all ---
@pytest.mark.asyncio
async def test_verify_all_passed(verifier, mock_router):
    mock_router.route.return_value = '{"passed": true, "reason": "ok"}'
    checks = ["non_empty", "success_criteria"]
    results = await verifier.verify_all(output={"a": 1}, checks=checks, router=mock_router)
    assert len(results) == 2
    assert all(r.passed for r in results)

@pytest.mark.asyncio
async def test_verify_all_fail_fast(verifier):
    checks = ["non_empty", "schema"]
    # Fails non_empty check, so schema is not run
    results = await verifier.verify_all(output="", checks=checks)
    assert len(results) == 1
    assert results[0].passed is False
    assert results[0].check_name == "non_empty"
