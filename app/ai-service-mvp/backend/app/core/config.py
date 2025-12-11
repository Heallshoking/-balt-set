"""
Configuration settings for AI Service Marketplace
Environment variables and application settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "AI Service Marketplace"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/ai_service_mvp"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080", "http://localhost:5173"]
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    # AI Services
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""
    
    # Payment Gateway (YooKassa)
    YOOKASSA_SHOP_ID: str = ""
    YOOKASSA_SECRET_KEY: str = ""
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Platform Commission (20-30%)
    PLATFORM_COMMISSION_RATE: float = 0.25  # 25%
    
    # Yandex Maps API
    YANDEX_MAPS_API_KEY: str = ""
    
    # SMS/Phone Verification
    SMS_PROVIDER_API_KEY: str = ""
    
    # File Storage
    MEDIA_STORAGE_PATH: str = "./media"
    MAX_UPLOAD_SIZE_MB: int = 10
    
    # Job Matching
    MASTER_RESPONSE_TIMEOUT_MINUTES: int = 15
    MAX_MASTER_DAILY_JOBS: int = 10
    
    # Pricing
    MINIMUM_JOB_COST: float = 500.0
    MAXIMUM_JOB_COST: float = 50000.0
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_file_encoding='utf-8',
        extra='ignore'
    )


settings = Settings()
