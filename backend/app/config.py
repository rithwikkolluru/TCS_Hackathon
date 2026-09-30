import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Repo root directory
ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "Intelligent Branch Service Load and Customer Experience Optimizer"
    API_V1_PREFIX: str = "api"
    DEBUG: bool = True

    # Database: Defaults to local SQLite file; can be overridden by PostgreSQL URL
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{ROOT_DIR}/banking_optimizer.db")

    # Security & JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "banking-ai-secret-key-production-ready-2026-tcs")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_MINUTES: int = int(os.getenv("JWT_EXPIRATION_MINUTES", "1440"))

    # Redis URL
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
