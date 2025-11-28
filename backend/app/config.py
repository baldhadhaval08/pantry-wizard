"""Configuration management for PantryWizard backend."""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "sqlite:///./pantry.db"
    
    # JWT
    JWT_SECRET: str = "asdfasdfasdf"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Ollama Configuration (for text generation)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b-instruct-q4_K_M"
    
    # Image Generation
    IMAGE_MODE: str = "ollama"  # "ollama" or "placeholder"
    OLLAMA_IMAGE_MODEL: str = "abedalswaity7/flux-prompt:latest"  # Ollama image generation model
    
    # API
    API_V1_PREFIX: str = "/api"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
