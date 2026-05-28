"""
ConstructMind AI - Application Configuration
Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744

Centralized configuration management using Pydantic BaseSettings.
All environment variables are loaded from .env file or system environment.
"""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "ConstructMind AI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # ── Database ─────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./constructmind.db"

    # ── AI Service Keys ──────────────────────────────────────────
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    # ── Groq Model Configuration ────────────────────────────────
    GROQ_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    GROQ_MAX_TOKENS: int = 4096
    GROQ_TEMPERATURE: float = 0.7

    # ── Gemini Model Configuration ──────────────────────────────
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_MAX_TOKENS: int = 8192

    # ── CORS ─────────────────────────────────────────────────────
    CORS_ORIGINS: str = "*"

    # ── Authentication (Clerk) ───────────────────────────────────
    CLERK_SECRET_KEY: str = ""

    # ── File Upload ──────────────────────────────────────────────
    MAX_UPLOAD_SIZE_MB: int = 50
    UPLOAD_DIR: str = "./uploads"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS into a list of origins."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.APP_ENV.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """Create cached settings instance (singleton pattern)."""
    return Settings()


settings = get_settings()
