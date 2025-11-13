"""
Configuration for User Management Service
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Service Configuration
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "user-service")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    
    # Database Configuration
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "airlock")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "airlock")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "airlock")
    DB_ECHO: str = os.getenv("DB_ECHO", "false")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    
    # JWT Configuration (for token validation)
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "dev-secret-key-change-in-production-123456789012345678901234567890",
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ISSUER: str = os.getenv("JWT_ISSUER", "airlock-auth-service")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

