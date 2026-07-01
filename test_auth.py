import requests
import hashlib
import hmac
import time

API_KEY = "fIPvR3bIfR)qqGyPp8MOEHP_60)NSDpO_1(13ukdvkAnYPfJ^=-I-64G0D]8v_SK2"
PRIVATE_KEY = "u05{05c_B~u{ix{exLp3HYH{L^gMJqD9FGgJjMA{GX}azmbV}S4~Pw6aoY{=B^e"

def test_auth():
    ts = int(time.time())
    params = {"api_key": API_KEY, "ts": ts}
    
    # 1. Ordenar parámetros alfabéticamente
    sorted_params = sorted(params.items())
    # 2. Construir cadena: clavevalor sin separadores
    param_string = "".join(f"{k}{v}" for k, v in sorted_params)
    print("🔑 Cadena para firma:", param_string)
    
    # 3. Calcular HMAC-SHA256
    sig = hmac.new(
        PRIVATE_KEY.encode('utf-8'),
        param_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    print("🔐 Firma generada:", sig)
    
    params["api_sig"] = sig
    
    url = "https://api.sandbox.gengo.com/v2/account/balance/"
    response = requests.get(url, params=params)
    print("📡 Status:", response.status_code)
    print("📄 Respuesta:", response.text)

if __name__ == "__main__":
    test_auth()