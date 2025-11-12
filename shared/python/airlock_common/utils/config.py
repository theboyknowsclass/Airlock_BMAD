"""
Configuration helpers for Airlock Common
"""
import os
from typing import Optional, List, Any


def get_env(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Get environment variable
    
    Args:
        key: Environment variable key
        default: Default value if not set
        required: Whether the variable is required
    
    Returns:
        Environment variable value
    
    Raises:
        ValueError: If required and not set
    
    Example:
        >>> get_env("DATABASE_URL", default="localhost")
        'localhost'
    """
    value = os.getenv(key, default)
    if required and value is None:
        raise ValueError(f"Environment variable {key} is required")
    return value


def get_env_int(key: str, default: Optional[int] = None, required: bool = False) -> Optional[int]:
    """
    Get environment variable as integer
    
    Args:
        key: Environment variable key
        default: Default value if not set
        required: Whether the variable is required
    
    Returns:
        Environment variable value as integer
    
    Raises:
        ValueError: If required and not set, or if value is not a valid integer
    
    Example:
        >>> get_env_int("PORT", default=8000)
        8000
    """
    value = get_env(key, default=None if default is None else str(default), required=required)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Environment variable {key} must be a valid integer")


def get_env_bool(key: str, default: Optional[bool] = None, required: bool = False) -> Optional[bool]:
    """
    Get environment variable as boolean
    
    Args:
        key: Environment variable key
        default: Default value if not set
        required: Whether the variable is required
    
    Returns:
        Environment variable value as boolean
    
    Raises:
        ValueError: If required and not set, or if value is not a valid boolean
    
    Example:
        >>> get_env_bool("DEBUG", default=False)
        False
    """
    value = get_env(key, default=None if default is None else str(default), required=required)
    if value is None:
        return default
    value_lower = value.lower()
    if value_lower in ("true", "1", "yes", "on"):
        return True
    elif value_lower in ("false", "0", "no", "off"):
        return False
    else:
        raise ValueError(f"Environment variable {key} must be a valid boolean")


def get_env_list(key: str, default: Optional[List[str]] = None, separator: str = ",", required: bool = False) -> Optional[List[str]]:
    """
    Get environment variable as list
    
    Args:
        key: Environment variable key
        default: Default value if not set
        separator: Separator character (default: comma)
        required: Whether the variable is required
    
    Returns:
        Environment variable value as list
    
    Raises:
        ValueError: If required and not set
    
    Example:
        >>> get_env_list("ALLOWED_ORIGINS", default=["*"])
        ['*']
    """
    value = get_env(key, default=None if default is None else separator.join(default), required=required)
    if value is None:
        return default
    return [item.strip() for item in value.split(separator) if item.strip()]

