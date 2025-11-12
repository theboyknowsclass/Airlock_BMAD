"""
Authorization code model for OAuth 2.0 Authorization Code flow
"""
from datetime import datetime
from typing import Optional, Dict
from dataclasses import dataclass


@dataclass
class AuthCode:
    """Authorization code model"""
    code: str
    user_id: str
    client_id: str
    redirect_uri: str
    scope: Optional[str] = None
    expires_at: datetime = None


class AuthCodeStore:
    """In-memory store for authorization codes"""
    
    def __init__(self):
        self._codes: Dict[str, AuthCode] = {}
    
    def store(self, auth_code: AuthCode):
        """Store authorization code"""
        self._codes[auth_code.code] = auth_code
    
    def get(self, code: str) -> Optional[AuthCode]:
        """Get authorization code"""
        return self._codes.get(code)
    
    def delete(self, code: str):
        """Delete authorization code"""
        if code in self._codes:
            del self._codes[code]
    
    def cleanup_expired(self):
        """Clean up expired authorization codes"""
        now = datetime.utcnow()
        expired_codes = [
            code for code, auth_code in self._codes.items()
            if auth_code.expires_at < now
        ]
        for code in expired_codes:
            del self._codes[code]

