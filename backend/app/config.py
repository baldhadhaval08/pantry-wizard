"""Configuration management for PantryWizard backend."""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "sqlite:///./pantry.db"
    
    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # LLM Configuration
    LLM_MODE: str = "ollama"  # "local", "ollama", or "api"
    LLM_API_URL: Optional[str] = None  # e.g., "https://api.openai.com/v1/chat/completions"
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL_PATH: Optional[str] = None  # Path to local model
    LLM_MODEL_NAME: str = "mistralai/Mistral-7B-Instruct-v0.2"  # For local mode
    # Ollama Configuration (for Python 3.13+)
    OLLAMA_BASE_URL: str = "http://localhost:11434"  # Ollama API URL
    OLLAMA_MODEL: str = "llama3.1:8b-instruct-q4_K_M"  # Ollama model name
    
    # Image Generation
    IMAGE_MODE: str = "placeholder"  # "placeholder", "local_sd", or "api"
    SD_MODEL_PATH: Optional[str] = None  # Path to Stable Diffusion model
    SD_MODEL_NAME: str = "runwayml/stable-diffusion-v1-5"
    
    # Hardware
    USE_CUDA: bool = False
    DEVICE: str = "cpu"  # "cpu" or "cuda"
    
    # API
    API_V1_PREFIX: str = "/api"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

