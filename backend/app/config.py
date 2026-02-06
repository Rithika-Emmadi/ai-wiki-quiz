"""Application configuration and environment variables."""
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache


_BACKEND_DIR = Path(__file__).resolve().parent.parent  # backend/
_DEFAULT_SQLITE_PATH = (_BACKEND_DIR / "wiki_quiz.db").as_posix()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    # Default to local SQLite so the project runs out-of-the-box (and quiz history persists)
    # Override via backend/.env to use MySQL, e.g.:
    # DATABASE_URL=mysql+pymysql://root:password@localhost:3306/wiki_quiz?charset=utf8mb4
    DATABASE_URL: str = f"sqlite:///{_DEFAULT_SQLITE_PATH}"
    
    # Groq API (free tier, no credit card required)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    # If GROQ_API_KEY is missing, fall back to a local heuristic generator so the app still runs.
    # Set REQUIRE_GROQ_API_KEY=true to disable the fallback and force real LLM generation.
    REQUIRE_GROQ_API_KEY: bool = False
    
    # App
    APP_NAME: str = "AI Wiki Quiz Generator"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
