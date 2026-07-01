import requests
import hashlib
import hmac
import time

API_KEY = "fIPvR3bIfR)qqGyPp8MOEHP_60)NSDpO_1(13ukdvkAnYPfJ^=-I-64G0D]8v_SK2"
PRIVATE_KEY = "u05{05c_B~u{ix{exLp3HYH{L^gMJqD9FGgJjMA{GX}azmbV}S4~Pw6aoY{=B^e"

def test_balance():
    ts = int(time.time())
    params = {"api_key": API_KEY, "ts": ts}
    sorted_params = sorted(params.items())
    param_string = "".join(f"{k}{v}" for k, v in sorted_params)
    sig = hmac.new(PRIVATE_KEY.encode(), param_string.encode(), hashlib.sha256).hexdigest()
    params["api_sig"] = sig
    
    url = "https://api.sandbox.gengo.com/v2/account/balance/"
    r = requests.get(url, params=params)
    print("Status:", r.status_code)
    print("Respuesta:", r.text)

test_balance()