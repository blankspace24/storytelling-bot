"""
Centralized settings module for StoryLens.

All environment variables and configuration values are defined here.
Other modules import from this file instead of reading os.environ directly.

Usage:
    from config.settings import settings
    api_key = settings.MISTRAL_API_KEY
    model = settings.DEFAULT_MODEL
"""

import os
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # ─── Mistral AI ───
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "mistral-large-latest")

    # ─── FastAPI Server ───
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_RELOAD: bool = os.getenv("API_RELOAD", "true").lower() == "true"

    # ─── Streamlit ───
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8501"))
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")

    # ─── LLM Parameters ───
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    LLM_MAX_RETRIES: int = int(os.getenv("LLM_MAX_RETRIES", "3"))

    # ─── App Info ───
    APP_NAME: str = "StoryLens"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-powered script analysis for storytelling intelligence"


# Singleton instance — import this everywhere
settings = Settings()
