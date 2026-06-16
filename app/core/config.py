from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv
import os

# Explicitly load .env from the project root
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))


class Settings(BaseSettings):
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")
    openai_model: str = "gpt-4o"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
