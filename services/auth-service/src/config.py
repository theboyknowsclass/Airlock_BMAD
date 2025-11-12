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
    
    # ADFS Configuration (Production)
    ADFS_AUTHORIZATION_URL: str = os.getenv("ADFS_AUTHORIZATION_URL", "")
    ADFS_TOKEN_URL: str = os.getenv("ADFS_TOKEN_URL", "")
    ADFS_USERINFO_URL: str = os.getenv("ADFS_USERINFO_URL", "")
    ADFS_ISSUER: str = os.getenv("ADFS_ISSUER", "")
    
    # Mock OAuth Configuration (Development)
    MOCK_OAUTH_URL: str = os.getenv("MOCK_OAUTH_URL", "http://mock-oauth:9000")
    USE_MOCK_OAUTH: bool = os.getenv("USE_MOCK_OAUTH", "true").lower() == "true"
    
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

