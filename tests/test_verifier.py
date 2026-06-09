import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from core.verifier import StepVerifier, VerificationResult, is_valid_output

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

@pytest.fixture
def mock_config():
    config = MagicMock()
    return config


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
    result = verifier.verify_numeric_range(output=5.0, min_val=1.0, max_val=10.0)
    assert result.passed is True
    assert "numeric_range" in caplog.text

def test_verify_numeric_range_below_min(verifier):
    result = verifier.verify_numeric_range(output=0.5, min_val=1.0, max_val=10.0)
    assert result.passed is False
    assert "below minimum" in result.reason

def test_verify_numeric_range_above_max(verifier):
    result = verifier.verify_numeric_range(output=15.0, min_val=1.0, max_val=10.0)
    assert result.passed is False
    assert "above maximum" in result.reason

def test_verify_numeric_range_not_numeric(verifier):
    result = verifier.verify_numeric_range(output="abc")
    assert result.passed is False
    assert "not numeric" in result.reason

def test_verify_numeric_range_no_lower_bound(verifier):
    result = verifier.verify_numeric_range(output=5.0, min_val=None, max_val=10.0)
    assert result.passed is True

def test_verify_numeric_range_no_upper_bound(verifier):
    result = verifier.verify_numeric_range(output=5.0, min_val=1.0, max_val=None)
    assert result.passed is True


# --- Test verify_schema ---
def test_verify_schema_valid(verifier, caplog):
    result = verifier.verify_schema(output={'a': 1, 'b': 2}, required_keys=['a', 'b'])
    assert result.passed is True
    assert "schema" in caplog.text

def test_verify_schema_missing_key(verifier):
    result = verifier.verify_schema(output={'a': 1}, required_keys=['a', 'b'])
    assert result.passed is False
    assert "missing keys: b" in result.reason

def test_verify_schema_not_a_dict(verifier):
    result = verifier.verify_schema(output='not a dict', required_keys=['a'])
    assert result.passed is False


# --- Test verify_success_criteria ---
@pytest.mark.asyncio
async def test_verify_success_criteria_passed(verifier, mock_router, mock_config):
    with patch('core.verifier.NinaConfig', return_value=mock_config), \
         patch('core.verifier.HybridRouter', return_value=mock_router):
        mock_router.initialize = AsyncMock()
        mock_router.single_turn = AsyncMock(return_value='{"passed": true, "reason": "ok"}')
        result = await verifier.verify_success_criteria(output="test", criteria="be good")
        assert result.passed is True
        assert result.reason == "ok"

@pytest.mark.asyncio
async def test_verify_success_criteria_malformed_json(verifier, mock_router, mock_config):
    with patch('core.verifier.NinaConfig', return_value=mock_config), \
         patch('core.verifier.HybridRouter', return_value=mock_router):
        mock_router.initialize = AsyncMock()
        mock_router.single_turn = AsyncMock(return_value="not json")
        result = await verifier.verify_success_criteria(output="test", criteria="be good")
        assert result.passed is False
        assert "invalid JSON" in result.reason

@pytest.mark.asyncio
async def test_verify_success_criteria_exception(verifier, mock_router, mock_config):
    with patch('core.verifier.NinaConfig', return_value=mock_config), \
         patch('core.verifier.HybridRouter', return_value=mock_router):
        mock_router.initialize = AsyncMock()
        mock_router.single_turn = AsyncMock(side_effect=Exception("Router down"))
        result = await verifier.verify_success_criteria(output="test", criteria="be good")
        assert result.passed is False
        assert "Router down" in result.reason


# --- Test verify_all ---
@pytest.mark.asyncio
async def test_verify_all_passed(verifier, mock_router, mock_config):
    with patch('core.verifier.NinaConfig', return_value=mock_config), \
         patch('core.verifier.HybridRouter', return_value=mock_router):
        mock_router.initialize = AsyncMock()
        mock_router.single_turn = AsyncMock(return_value='{"passed": true, "reason": "ok"}')
        checks = [
            {"type": "non_empty"},
            {"type": "success_criteria", "criteria": "be good"}
        ]
        results = await verifier.verify_all(output={"a": 1}, checks=checks)
        assert len(results) == 2
        assert all(r.passed for r in results)

@pytest.mark.asyncio
async def test_verify_all_fail_fast(verifier):
    checks = [
        {"type": "non_empty"},
        {"type": "schema", "required_keys": ["a"]}
    ]
    # Fails non_empty check, so schema is not run
    results = await verifier.verify_all(output="", checks=checks)
    assert len(results) == 1
    assert results[0].passed is False
    assert results[0].check_name == "non_empty"
