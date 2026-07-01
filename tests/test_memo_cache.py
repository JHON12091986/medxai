import pytest
import time
import shutil
from pathlib import Path
from core.memo_cache import (
    cache_key,
    get_cached,
    set_cached,
    invalidate,
    purge_expired,
    cache_stats,
    HyperDriveCache,
    cache
)

def test_basic_memo_cache():
    key = cache_key("test_prompt", "test_context")
    assert get_cached(key) is None
    
    val = {"result": "ok", "nested": [1, 2, 3]}
    set_cached(key, val, ttl=10)
    
    assert get_cached(key) == val
    
    # Invalidate
    assert invalidate(key) is True
    assert get_cached(key) is None
    assert invalidate(key) is False

def test_hd_cache_exact():
    h_cache = HyperDriveCache("data/test_hd_cache.json")
    # Clean up old file if exists
    p = Path("data/test_hd_cache.json")
    if p.exists():
        p.unlink()
        
    prompt = "What is the capital of Bangladesh?"
    data = {"answer": "Dhaka"}
    
    h_cache.set(prompt, data, ttl=5)
    assert h_cache.get_exact(prompt) == data
    
    # Expiry
    h_cache.s[h_cache._hash_key(prompt)]["expires_at"] = time.time() - 1
    assert h_cache.get_exact(prompt) is None
    
    if p.exists():
        p.unlink()

def test_hd_cache_semantic():
    h_cache = HyperDriveCache("data/test_hd_cache_semantic.json")
    p = Path("data/test_hd_cache_semantic.json")
    if p.exists():
        p.unlink()
        
    h_cache.set("find all python files in core", "results_1", ttl=60)
    h_cache.set("grep for some keyword in tools", "results_2", ttl=60)
    
    # Semantic match
    assert h_cache.get_semantic("find python files in core", threshold=0.8) == "results_1"
    assert h_cache.get_semantic("grep keyword in tools", threshold=0.6) == "results_2"
    assert h_cache.get_semantic("something entirely different", threshold=0.8) is None
    
    if p.exists():
        p.unlink()

def test_hd_cache_tool():
    h_cache = HyperDriveCache("data/test_hd_cache_tool.json")
    p = Path("data/test_hd_cache_tool.json")
    if p.exists():
        p.unlink()
        
    h_cache.cache_tool_output("git_status", {"cwd": "/home/user"}, "On branch main\nnothing to commit", ttl=60)
    assert h_cache.get_tool_output("git_status", {"cwd": "/home/user"}) == "On branch main\nnothing to commit"
    assert h_cache.get_tool_output("git_status", {"cwd": "/home/other"}) is None
    
    if p.exists():
        p.unlink()
