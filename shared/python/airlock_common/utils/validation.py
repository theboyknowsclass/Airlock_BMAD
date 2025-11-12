"""
Validation utilities for Airlock Common
"""
import re
import uuid
from typing import Optional
from urllib.parse import urlparse


def validate_email(email: str) -> bool:
    """
    Validate email address
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid, False otherwise
    
    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid-email")
        False
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """
    Validate URL
    
    Args:
        url: URL to validate
    
    Returns:
        True if valid, False otherwise
    
    Example:
        >>> validate_url("https://example.com")
        True
        >>> validate_url("invalid-url")
        False
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_uuid(uuid_string: str) -> bool:
    """
    Validate UUID
    
    Args:
        uuid_string: UUID string to validate
    
    Returns:
        True if valid, False otherwise
    
    Example:
        >>> validate_uuid("123e4567-e89b-12d3-a456-426614174000")
        True
        >>> validate_uuid("invalid-uuid")
        False
    """
    try:
        uuid.UUID(uuid_string)
        return True
    except (ValueError, TypeError):
        return False

