"""
API Key model
"""
from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional

from ..base import Base, TimestampMixin


class APIKey(Base, TimestampMixin):
    """API Key model"""
    __tablename__ = "api_keys"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    key_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    scopes: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array as text
    permissions: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array as text
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    
    def __repr__(self) -> str:
        return f"<APIKey(id={self.id}, key_hash={self.key_hash[:10]}..., expires_at={self.expires_at})>"

