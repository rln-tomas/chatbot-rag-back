"""
Core configuration module using Pydantic Settings.
Loads environment variables and provides type-safe configuration.
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


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

    # LLM Provider Configuration
    LLM_PROVIDER: str = Field(
        default="gemini",
        description="LLM provider to use: 'gemini' or 'ollama'"
    )
    
    # Google Gemini API
    GEMINI_API_KEY: str = Field(
        default="",
        description="Google Gemini API key (required if LLM_PROVIDER=gemini)"
    )
    GEMINI_MODEL: str = Field(
        default="gemini-2.0-flash-exp",
        description="Gemini model to use"
    )
    GEMINI_EMBEDDING_MODEL: str = Field(
        default="models/embedding-001",
        description="Gemini embedding model to use"
    )
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = Field(
        default="http://localhost:11434",
        description="Ollama base URL (use https://api.ollamacloud.com for Ollama Cloud)"
    )
    OLLAMA_API_KEY: str = Field(
        default="",
        description="Ollama API key (required for Ollama Cloud)"
    )
    OLLAMA_MODEL: str = Field(
        default="llama3.2",
        description="Ollama model to use for chat/completion"
    )
    OLLAMA_EMBEDDING_MODEL: str = Field(
        default="nomic-embed-text",
        description="Ollama model to use for embeddings"
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
        default="rag-testing",
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

    @field_validator("DATABASE_URL")
    @classmethod
    def clean_database_url(cls, v: str) -> str:
        """
        Clean and fix DATABASE_URL:
        - Strip whitespace and newlines (Railway variable issue)
        - Replace mysql:// with mysql+pymysql:// if needed
        """
        # Strip whitespace and newlines
        v = v.strip()

        # Replace mysql:// with mysql+pymysql:// for SQLAlchemy driver
        if v.startswith("mysql://"):
            v = v.replace("mysql://", "mysql+pymysql://", 1)

        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
