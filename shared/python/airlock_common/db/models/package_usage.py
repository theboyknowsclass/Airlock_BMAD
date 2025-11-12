"""
Package Usage model
"""
from sqlalchemy import String, ForeignKey, Integer, DateTime, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from ..base import Base


class PackageUsage(Base):
    """Package Usage model - tracks which projects use approved packages"""
    __tablename__ = "package_usage"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    package_request_id: Mapped[int] = mapped_column(
        ForeignKey("package_requests.id"),
        nullable=False,
        index=True
    )
    project_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    
    # Relationships
    package_request: Mapped["PackageRequest"] = relationship("PackageRequest", back_populates="package_usage")
    
    # Index for querying by project_name
    __table_args__ = (
        Index("ix_package_usage_project_name", "project_name"),
    )
    
    def __repr__(self) -> str:
        return f"<PackageUsage(id={self.id}, package_request_id={self.package_request_id}, project_name={self.project_name})>"

