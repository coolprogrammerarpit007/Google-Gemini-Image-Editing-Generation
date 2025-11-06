import os
from dotenv import load_dotenv

# Load from project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '.env'))

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS", "")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

class Settings:
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    SERVER_HOST: str = os.getenv("SERVER_HOST", "http://localhost:9000")

   
    if all([DB_USER, DB_HOST, DB_NAME]):

        DATABASE_URL: str = f"mysql+asyncmy://{DB_USER}:{DB_PASS}@{DB_HOST}:3306/{DB_NAME}"

    else:
        print(" Missing MySQL env vars, falling back to SQLite.")
        DATABASE_URL: str = "sqlite+aiosqlite:///./fallback.db"


settings = Settings()
