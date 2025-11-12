"""
User model
"""
from sqlalchemy import String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from ..base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User model"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    roles: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    
    # Relationships
    package_submissions: Mapped[List["PackageSubmission"]] = relationship(
        "PackageSubmission",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    license_allowlist_entries: Mapped[List["LicenseAllowlist"]] = relationship(
        "LicenseAllowlist",
        back_populates="created_by_user",
        foreign_keys="LicenseAllowlist.created_by"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email}, roles={self.roles})>"

