import requests
import json

def test_health():
    try:
        r = requests.get("http://127.0.0.1:9502/health")
        assert r.status_code == 200
        data = r.json()
        assert data["ia_loaded"] == True
        print("✅ Health test passed")
    except Exception as e:
        print(f"❌ Health test failed: {e}")

def test_analyze():
    try:
        r = requests.get("http://127.0.0.1:9502/analyze/Python")
        assert r.status_code == 200
        assert "Modo Tiburón Supremo" in r.text
        print("✅ Analyze test passed")
    except Exception as e:
        print(f"❌ Analyze test failed: {e}")

if __name__ == "__main__":
    test_health()
    test_analyze()
    print("🎯 Pruebas completadas!")