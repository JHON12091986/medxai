"""
NINA Agno-style Structured Schema Validation Pattern
Enforces strict schema validation (keys and type constraints) on model responses.
"""
import json
import re
from typing import Any, Dict, List, Type, Union

class SchemaValidationError(ValueError):
    pass

def extract_and_parse_json(text: str) -> Any:
    """
    Extracts the first valid JSON block or dictionary from text and parses it.
    """
    # Try finding markdown code block first
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        content = match.group(1).strip()
    else:
        content = text.strip()

    # Locate first curly brace if nested
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1 and end > start:
        content = content[start:end+1]

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise SchemaValidationError(f"Invalid JSON format: {e}")

def validate_against_schema(data: Dict[str, Any], required_keys: Dict[str, Union[Type[Any], List[Type[Any]]]]) -> None:
    """
    Validates that a dictionary contains all required keys with correct type definitions.
    """
    for key, expected_type in required_keys.items():
        if key not in data:
            raise SchemaValidationError(f"Missing required schema key: '{key}'")
        
        val = data[key]
        if isinstance(expected_type, list):
            # Check if value is one of the allowed types
            if not any(isinstance(val, t) for t in expected_type):
                allowed_names = ", ".join(t.__name__ for t in expected_type)
                raise SchemaValidationError(f"Key '{key}' must be one of types [{allowed_names}]. Got {type(val).__name__}.")
        else:
            if not isinstance(val, expected_type):
                raise SchemaValidationError(f"Key '{key}' must be of type {expected_type.__name__}. Got {type(val).__name__}.")
