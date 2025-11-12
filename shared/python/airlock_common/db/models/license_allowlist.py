"""
License Allowlist model
"""
from sqlalchemy import String, ForeignKey, Integer, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from ..base import Base, TimestampMixin


class LicenseAllowlist(Base, TimestampMixin):
    """License Allowlist model - approved licenses for validation"""
    __tablename__ = "license_allowlist"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    license_identifier: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    license_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    
    # Relationships
    created_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="license_allowlist_entries",
        foreign_keys=[created_by]
    )
    
    def __repr__(self) -> str:
        return f"<LicenseAllowlist(id={self.id}, license_identifier={self.license_identifier}, license_name={self.license_name}, is_active={self.is_active})>"

