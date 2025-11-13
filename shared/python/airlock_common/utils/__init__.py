"""
Utility functions and helpers for Airlock Common
"""
from .logging import setup_logging, get_logger
from .errors import (
    AirlockError,
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    ServiceUnavailableError,
)
from .validation import validate_email, validate_url, validate_uuid
from .config import get_env, get_env_int, get_env_bool, get_env_list
from .jwt import (
    JWTConfig,
    create_access_token,
    create_refresh_token,
    decode_token,
    create_user_access_token,
    create_user_refresh_token,
    create_api_key_access_token,
    create_api_key_refresh_token,
)

__all__ = [
    "setup_logging",
    "get_logger",
    "AirlockError",
    "ValidationError",
    "NotFoundError",
    "UnauthorizedError",
    "ForbiddenError",
    "ConflictError",
    "ServiceUnavailableError",
    "validate_email",
    "validate_url",
    "validate_uuid",
    "get_env",
    "get_env_int",
    "get_env_bool",
    "get_env_list",
    "JWTConfig",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "create_user_access_token",
    "create_user_refresh_token",
    "create_api_key_access_token",
    "create_api_key_refresh_token",
]

