import json
from pathlib import Path
from unittest.mock import patch, mock_open
from tools.validate_index import validate, reconcile_tests

def test_reconcile_tests():
    data = {
        "files": [
            {
                "path": "tools/non_existent.py",
                "requires_tests": True,
                "category": "tool",
                "role": "helper",
                "governed": True,
                "lifecycle": "active",
                "retention_policy": "standard"
            }
        ]
    }
    # Test that it correctly handles require_tests
    repo_root = Path(__file__).parent.parent.resolve()
    reconcile_tests(data, repo_root)
    # The file does not exist, so it should not be mutated or should be handled safely
    assert data["files"][0]["requires_tests"] is True

def test_validate_with_test_exempt():
    mock_data = {
        "files": [
            {
                "path": "tools/validate_index.py",
                "category": "tool",
                "role": "helper",
                "governed": True,
                "lifecycle": "active",
                "retention_policy": "standard",
                "requires_tests": True,
                "test_exempt": True,
                "summary": "Governed helper",
                "origin": "local",
                "tags": ["governance"]
            }
        ]
    }
    
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
        with patch("tools.validate_index.os.walk", return_value=[]):
            with patch("tools.validate_index.Path.exists", return_value=True):
                # Should pass since test_exempt is True and it won't complain about missing test
                res = validate(check_deltas=False, notify=False, reconcile=False)
                assert res is True
