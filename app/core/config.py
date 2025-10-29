"""Application configuration management."""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "Google Calendar Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str
    TEST_DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    ALLOWED_METHODS: str = "GET,POST,PUT,PATCH,DELETE"
    ALLOWED_HEADERS: str = "*"
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def parse_allowed_origins(cls, v: str) -> List[str]:
        """Parse comma-separated origins into list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("ALLOWED_METHODS")
    @classmethod
    def parse_allowed_methods(cls, v: str) -> List[str]:
        """Parse comma-separated methods into list."""
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v
    
    @property
    def cors_origins(self) -> List[str]:
        """Get CORS origins as list."""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        return self.ALLOWED_ORIGINS
    
    @property
    def cors_methods(self) -> List[str]:
        """Get CORS methods as list."""
        if isinstance(self.ALLOWED_METHODS, str):
            return [method.strip() for method in self.ALLOWED_METHODS.split(",")]
        return self.ALLOWED_METHODS
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
