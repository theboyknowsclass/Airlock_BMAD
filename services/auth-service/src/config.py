"""
Configuration for Authentication Service
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Service Configuration
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "auth-service")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    
    # OAuth2 Configuration
    OAUTH2_CLIENT_ID: str = os.getenv("OAUTH2_CLIENT_ID", "airlock-client")
    OAUTH2_CLIENT_SECRET: str = os.getenv("OAUTH2_CLIENT_SECRET", "")
    OAUTH2_REDIRECT_URI: str = os.getenv("OAUTH2_REDIRECT_URI", "http://localhost:8001/api/v1/auth/callback")
    FRONTEND_CALLBACK_URI: str = os.getenv("FRONTEND_CALLBACK_URI", "http://localhost:3000/auth/callback")
    
    # OAuth2 Provider URLs (configured via environment variables)
    OAUTH2_AUTHORIZATION_URL: str = os.getenv("OAUTH2_AUTHORIZATION_URL", "")
    OAUTH2_TOKEN_URL: str = os.getenv("OAUTH2_TOKEN_URL", "")
    OAUTH2_USERINFO_URL: str = os.getenv("OAUTH2_USERINFO_URL", "")
    OAUTH2_ISSUER: str = os.getenv("OAUTH2_ISSUER", "")
    
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "dev-secret-key-change-in-production-123456789012345678901234567890",
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ISSUER: str = os.getenv("JWT_ISSUER", "airlock-auth-service")
    
    # Token Expiry
    ACCESS_TOKEN_EXPIRY_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRY_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRY_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRY_DAYS", "7"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

