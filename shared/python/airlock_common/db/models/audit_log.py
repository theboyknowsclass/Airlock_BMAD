"""
Audit Log model
"""
from sqlalchemy import String, ForeignKey, Integer, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional

from ..base import Base


class AuditLog(Base):
    """Audit Log model"""
    __tablename__ = "audit_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON content as text
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True, server_default=func.now())
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action={self.action}, resource_type={self.resource_type}, timestamp={self.timestamp})>"

