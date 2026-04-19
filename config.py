import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]
DB_PATH = os.getenv("DB_PATH", "sqlite+aiosqlite:///xla_bot.db")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "300"))

PROXY_URL = os.getenv("PROXY_URL", None)
USE_PROXY = os.getenv("USE_PROXY", "False").lower() == "true"

POOL_API_URL = "https://pool.scalaproject.io/api/stats"
DIFFICULTY_TARGET = 120
