import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SERVER_HOST: str = os.getenv("SERVER_HOST", "http://localhost:9000")

settings = Settings()
