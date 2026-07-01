"""
tools/telegram_notify.py
Sends a Telegram message using TELEGRAM_BOT_TOKEN and TELEGRAMCHATID from .env.
"""

import os
import sys
import urllib.request
import urllib.parse
from pathlib import Path
from core.constants import (ENV_TELEGRAM_BOT_TOKEN, ENV_TELEGRAM_CHAT_ID, ENV_API_SECRET_KEY, ENV_OPENAI_API_KEY, ENV_CEREBRAS_API_KEY, ENV_GROQ_API_KEY, ENV_GEMINI_API_KEY, ENV_MISTRAL_API_KEY, ENV_OPENROUTER_API_KEY, ENV_DEEPSEEK_API_KEY, ENV_PERPLEXITY_API_KEY, ENV_TOGETHER_API_KEY, ENV_COHERE_API_KEY, ENV_FIREWORKS_API_KEY, ENV_XAI_API_KEY, ENV_SAMBANOVA_API_KEY, ENV_HYPERBOLIC_API_KEY, ENV_NOVITA_API_KEY, ENV_OLLAMA_HOST, ENV_EWS_USERNAME, ENV_EWS_MY_EMAIL, ENV_EWS_SHARED_EMAIL)
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(dotenv_path=None):
        if dotenv_path is None:
            dotenv_path = Path(__file__).parent.parent.resolve() / ".env"
        else:
            dotenv_path = Path(dotenv_path)
        if dotenv_path.exists():
            try:
                with open(dotenv_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        key, val = line.split("=", 1)
                        key = key.strip()
                        val = val.strip().strip("'\"")
                        os.environ[key] = val
            except Exception:
                pass

def send_message(message: str) -> bool:
    repo_root = Path(__file__).parent.parent.resolve()
    load_dotenv(repo_root / ".env")
    bot_token = os.environ.get(ENV_TELEGRAM_BOT_TOKEN)
    chat_id = os.environ.get("TELEGRAMCHATID")
    if not bot_token or not chat_id:
        print("⚠️ Telegram credentials not found in environment. Skipping notification.")
        return False
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = urllib.parse.urlencode({'chat_id': chat_id, 'text': message}).encode('utf-8')
    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req) as response:
            return response.status == 200
    except Exception as e:
        print(f"❌ Exception sending Telegram notification: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 telegram_notify.py <message>")
        sys.exit(1)
    msg = sys.argv[1]
    success = send_message(msg)
    sys.exit(0 if success else 1)
