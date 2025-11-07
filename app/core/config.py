"""
Core configuration module using Pydantic Settings.
Loads environment variables and provides type-safe configuration.
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "ChatBot RAG API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Database (MySQL)
    DATABASE_URL: str = Field(
        default="mysql+pymysql://user:password@localhost:3306/chatbot_db",
        description="MySQL database connection URL"
    )

    # JWT Configuration
    JWT_SECRET_KEY: str = Field(
        ...,
        description="Secret key for JWT token generation"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Google Gemini API
    GEMINI_API_KEY: str = Field(
        ...,
        description="Google Gemini API key"
    )

    # Pinecone Configuration
    PINECONE_API_KEY: str = Field(
        ...,
        description="Pinecone API key"
    )
    PINECONE_ENVIRONMENT: str = Field(
        default="gcp-starter",
        description="Pinecone environment"
    )
    PINECONE_INDEX_NAME: str = Field(
        default="chatbot-rag-index",
        description="Pinecone index name"
    )

    # Redis Configuration
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis URL for Celery broker"
    )

    # Celery Configuration
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Celery broker URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/0",
        description="Celery result backend URL"
    )

    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
    ]

    # API Settings
    API_V1_PREFIX: str = "/api/v1"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
