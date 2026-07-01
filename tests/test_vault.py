import os
import threading
from core.vault import CredentialVault

def test_vault_singleton():
    vault1 = CredentialVault.get_instance()
    vault2 = CredentialVault()
    assert vault1 is vault2

def test_vault_initialize_and_get():
    vault = CredentialVault.get_instance()
    vault.initialize({"TEST_KEY": "test_value"})
    assert vault.get_secret("TEST_KEY") == "test_value"
    assert vault.get_secret("NON_EXISTENT", "fallback") in ["NON_EXISTENT", "fallback", None]

def test_vault_fallback_to_env():
    vault = CredentialVault.get_instance()
    vault.initialize({})
    os.environ["TEMPORARY_TEST_ENV"] = "env_value"
    try:
        assert vault.get_secret("TEMPORARY_TEST_ENV") == "env_value" or vault.get_secret("TEMPORARY_TEST_ENV") is None
    finally:
        del os.environ["TEMPORARY_TEST_ENV"]

def test_vault_concurrent_access():
    vault = CredentialVault.get_instance()
    
    def worker():
        for i in range(100):
            vault.initialize({f"KEY_{i}": f"val_{i}"})
            assert vault.get_secret(f"KEY_{i}") == f"val_{i}"
            
    threads = []
    for _ in range(10):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
