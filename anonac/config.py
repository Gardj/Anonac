import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass
class Settings:
    bot_token: str = os.getenv("BOT_TOKEN")
    database_url: str = os.getenv("DATABASE_URL")

settings = Settings()
