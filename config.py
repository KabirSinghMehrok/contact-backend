"""Configuration management for the LLM Backend API."""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings."""
    
    # API Configuration
    API_TITLE: str = os.getenv("API_TITLE", "LLM Backend API")
    API_DESCRIPTION: str = os.getenv("API_DESCRIPTION", "FastAPI backend for LLM-based table data processing")
    API_VERSION: str = os.getenv("API_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    API_KEY_HEADER: str = os.getenv("API_KEY_HEADER", "X-API-Key")
    
    # Google AI
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Intent Classification Categories
    INTENT_CATEGORIES: List[str] = [
        # "data_filtering",    # Filter, search, or select specific data
        "data_transformation",  # Modify, format, or restructure data
        # "data_analysis"      # Analyze, summarize, or generate insights
    ]

# Global settings instance
settings = Settings()
