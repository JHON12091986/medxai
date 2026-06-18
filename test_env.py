import os
from dotenv import load_dotenv
load_dotenv()
print(f'Token detectado: {os.getenv(''TELEGRAM_BOT_TOKEN'')}')
