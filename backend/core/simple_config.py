"""
Simple configuration for legal betting service
"""
import os
from typing import List

class Settings:
    """Application settings"""
    def __init__(self):
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///legal_betting.db")
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        self.PORT = int(os.getenv("PORT", 8000))
        self.ALLOWED_HOSTS = ["*"]

settings = Settings()