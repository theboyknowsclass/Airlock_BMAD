"""
Package model - for fetched/approved packages
"""
from sqlalchemy import String, Text, DateTime, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional
import enum

from ..base import Base, TimestampMixin


class PackageStatus(enum.Enum):
    """Package status"""
    PENDING = "pending"
    FETCHED = "fetched"
    APPROVED = "approved"
    REJECTED = "rejected"


class Package(Base, TimestampMixin):
    """Package model - stores fetched package data from NPM registry"""
    __tablename__ = "packages"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[PackageStatus] = mapped_column(
        Enum(PackageStatus),
        nullable=False,
        default=PackageStatus.PENDING,
        index=True
    )
    package_metadata: Mapped[Optional[str]] = mapped_column("metadata", Text, nullable=True)  # JSON content as text (package.json metadata)
    fetched_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Unique constraint on name + version
    __table_args__ = (
        Index("ix_packages_name_version", "name", "version", unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<Package(id={self.id}, name={self.name}, version={self.version}, status={self.status.value})>"

