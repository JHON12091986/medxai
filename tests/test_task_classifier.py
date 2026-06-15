import pytest
from core.task_classifier import classify_task, ClassifiedTask

@pytest.mark.asyncio
async def test_classify_task_simple_keyword():
    """Test that SIMPLE_KEYWORDS return a quick/SIMPLE task."""
    text = "format some_file.py".ljust(301)
    messages = [{"role": "user", "content": "msg1"}, {"role": "assistant", "content": "msg2"}, {"role": "user", "content": text}]
    result = await classify_task(text, messages)
    assert result.task_type == "quick"

@pytest.mark.asyncio
async def test_classify_task_complex_keyword():
    """Test that COMPLEX_KEYWORDS return a research/COMPLEX task."""
    text = "architect a new microservice".ljust(301)
    messages = [{"role": "user", "content": "msg1"}, {"role": "assistant", "content": "msg2"}, {"role": "user", "content": text}]
    result = await classify_task(text, messages)
    assert result.task_type == "research"

@pytest.mark.asyncio
async def test_classify_task_short_no_history():
    """Test that short text with minimal history defaults to quick."""
    text = "Hello world"
    messages = [{"role": "user", "content": text}]
    result = await classify_task(text, messages)
    assert result.task_type == "quick"

@pytest.mark.asyncio
async def test_classify_task_long_history():
    """Test that long history triggers COMPLEX (research) classification."""
    text = "Small text".ljust(301)
    messages = [
        {"role": "user", "content": "A" * 4001},
        {"role": "assistant", "content": "B" * 4001},
        {"role": "user", "content": text}
    ]
    result = await classify_task(text, messages)
    assert result.task_type == "research"

@pytest.mark.asyncio
async def test_classify_task_sensitive_fallback():
    """Test fallback to sensitive keywords."""
    # Using 'confidential' which is not in SIMPLE_KEYWORDS
    text = "this is a confidential document".ljust(301)
    messages = [{"role": "user", "content": "msg1"}, {"role": "assistant", "content": "msg2"}, {"role": "user", "content": text}]
    result = await classify_task(text, messages)
    
    assert result.task_type == "sensitive"
    assert result.is_sensitive is True

@pytest.mark.asyncio
async def test_classify_task_coding_fallback():
    """Test fallback to coding keywords."""
    # Using 'python' and 'traceback'
    text = "explain this python traceback".ljust(301)
    messages = [{"role": "user", "content": "msg1"}, {"role": "assistant", "content": "msg2"}, {"role": "user", "content": text}]
    result = await classify_task(text, messages)
    assert result.task_type == "coding"

@pytest.mark.asyncio
async def test_classify_task_math_fallback():
    """Test fallback to math keywords."""
    text = "solve this equation".ljust(301)
    messages = [{"role": "user", "content": "msg1"}, {"role": "assistant", "content": "msg2"}, {"role": "user", "content": text}]
    result = await classify_task(text, messages)
    assert result.task_type == "math"

@pytest.mark.asyncio
async def test_classify_task_default_general():
    """Test that non-matching text defaults to general."""
    text = "Just a normal statement about life."
    text = text.ljust(301)
    messages = [{"role": "user", "content": "History"}, {"role": "assistant", "content": "Ok"}, {"role": "user", "content": text}]
    result = await classify_task(text, messages)
    assert result.task_type == "general"

@pytest.mark.asyncio
async def test_classify_task_empty_input():
    """Test edge case with empty text and messages."""
    result = await classify_task("", [])
    assert result.task_type == "quick"
