from tools.regex_cache import RegexRegistry, get_compiled

def test_regex_registry_initialization():
    registry = RegexRegistry()
    assert registry.get_compiled("sensitive_data") is not None
    assert registry.get_compiled("log_structure") is not None
    assert registry.get_compiled("task_classification") is not None

def test_register_new_pattern():
    registry = RegexRegistry()
    registry.register_pattern("custom", r"hello\s+world")
    pattern = registry.get_compiled("custom")
    assert pattern is not None
    assert pattern.match("hello world")

def test_get_compiled_nonexistent():
    registry = RegexRegistry()
    assert registry.get_compiled("nonexistent") is None

def test_module_level_helper():
    assert get_compiled("sensitive_data") is not None
    assert get_compiled("nonexistent") is None
