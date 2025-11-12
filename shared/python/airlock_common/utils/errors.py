"""
Custom exception classes for Airlock Common
"""
from typing import Optional, Dict, Any


class AirlockError(Exception):
    """Base exception for Airlock errors"""
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Airlock error
        
        Args:
            message: Error message
            code: Error code
            details: Additional error details
        """
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary"""
        return {
            "error": {
                "code": self.code or "AIRLOCK_ERROR",
                "message": self.message,
                "details": self.details,
            }
        }


class ValidationError(AirlockError):
    """Validation error"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="VALIDATION_ERROR", details=details)


class NotFoundError(AirlockError):
    """Resource not found error"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="NOT_FOUND", details=details)


class UnauthorizedError(AirlockError):
    """Unauthorized error"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="UNAUTHORIZED", details=details)


class ForbiddenError(AirlockError):
    """Forbidden error"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="FORBIDDEN", details=details)


class ConflictError(AirlockError):
    """Conflict error"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="CONFLICT", details=details)


class ServiceUnavailableError(AirlockError):
    """Service unavailable error"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="SERVICE_UNAVAILABLE", details=details)

