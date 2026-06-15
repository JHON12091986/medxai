"""
tools/telegram_notify.py
Sends a Telegram message using TELEGRAMBOTTOKEN and TELEGRAMCHATID from .env.
"""

import os
import sys
import urllib.request
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv

def send_message(message: str) -> bool:
    repo_root = Path(__file__).parent.parent.resolve()
    load_dotenv(repo_root / ".env")
    bot_token = os.environ.get("TELEGRAMBOTTOKEN")
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
