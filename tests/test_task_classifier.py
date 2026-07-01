from core.task_classifier import classify_task, SIMPLE, COMPLEX

def test_classify_task_simple_keyword():
    """Test that SIMPLE_KEYWORDS return a quick/SIMPLE task."""
    text = "format some_file.py".ljust(301)
    messages = [{"role": "user", "content": "msg1"}, {"role": "assistant", "content": "msg2"}, {"role": "user", "content": text}]
    result = classify_task(text, messages)
    assert result.complexity == SIMPLE
    assert result._semantic_type == "quick"

def test_classify_task_complex_keyword():
    """Test that COMPLEX_KEYWORDS return a research/COMPLEX task."""
    text = "architect a new microservice".ljust(301)
    messages = [{"role": "user", "content": "msg1"}, {"role": "assistant", "content": "msg2"}, {"role": "user", "content": text}]
    result = classify_task(text, messages)
    assert result.complexity == COMPLEX
    assert result._semantic_type == "quick"

def test_classify_task_short_no_history():
    """Test that short text with minimal history defaults to quick."""
    text = "Hello world"
    messages = [{"role": "user", "content": text}]
    result = classify_task(text, messages)
    assert result.complexity == SIMPLE
    assert result._semantic_type == "quick"

def test_classify_task_long_history():
    """Test that long history triggers COMPLEX (research) classification."""
    text = "Small text".ljust(301)
    messages = [
        {"role": "user", "content": "A" * 35001},
        {"role": "assistant", "content": "B" * 35001},
        {"role": "user", "content": text}
    ]
    result = classify_task(text, messages)
    assert result.complexity == COMPLEX
    assert result._semantic_type == "quick"

def test_classify_task_sensitive_fallback():
    """Test fallback to sensitive keywords."""
    text = "this is a confidential document".ljust(301)
    messages = [{"role": "user", "content": "msg1"}, {"role": "assistant", "content": "msg2"}, {"role": "user", "content": text}]
    result = classify_task(text, messages)
    
    assert result.is_sensitive is True
    assert result.recommended_tier == "LOCAL"

def test_classify_task_coding_fallback():
    """Test fallback to coding keywords."""
    text = "explain this python code block".ljust(301)
    messages = [{"role": "user", "content": "msg1"}, {"role": "assistant", "content": "msg2"}, {"role": "user", "content": text}]
    result = classify_task(text, messages)
    assert result._semantic_type == "coding"

def test_classify_task_math_fallback():
    """Test fallback to math keywords."""
    text = "solve this equation".ljust(301)
    messages = [{"role": "user", "content": "msg1"}, {"role": "assistant", "content": "msg2"}, {"role": "user", "content": text}]
    result = classify_task(text, messages)
    assert result._semantic_type == "math"

def test_classify_task_default_general():
    """Test that non-matching text defaults to general."""
    text = "Just a normal statement about life."
    text = text.ljust(301)
    messages = [{"role": "user", "content": "History"}, {"role": "assistant", "content": "Ok"}, {"role": "user", "content": text}]
    result = classify_task(text, messages)
    assert result._semantic_type == "quick"

def test_classify_task_empty_input():
    """Test edge case with empty text and messages."""
    result = classify_task("", [])
    assert result.complexity == SIMPLE
    assert result._semantic_type == "quick"
