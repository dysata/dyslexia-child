from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    api_key: str = os.getenv("API_KEY", "dev-key")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")

settings = Settings()
