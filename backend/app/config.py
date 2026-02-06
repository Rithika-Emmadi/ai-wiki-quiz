"""Application configuration and environment variables."""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database (use sqlite:///./wiki_quiz.db for local dev without MySQL)
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/wiki_quiz?charset=utf8mb4"
    
    # Groq API (free tier, no credit card required)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    
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
