"""
Check Result model
"""
import enum
from typing import Optional
from sqlalchemy import String, ForeignKey, Integer, Enum, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from ..base import Base


class CheckType(enum.Enum):
    """Check type"""
    TRIVY = "trivy"
    LICENSE = "license"
    # Future: Add more check types


class CheckStatus(enum.Enum):
    """Check status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class CheckResult(Base):
    """Check Result model"""
    __tablename__ = "check_results"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflows.id"), nullable=False, index=True)
    check_type: Mapped[CheckType] = mapped_column(Enum(CheckType), nullable=False, index=True)
    status: Mapped[CheckStatus] = mapped_column(
        Enum(CheckStatus),
        nullable=False,
        default=CheckStatus.PENDING,
        index=True
    )
    results: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON content as text
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relationships
    workflow: Mapped["Workflow"] = relationship("Workflow", back_populates="check_results")
    
    def __repr__(self) -> str:
        return f"<CheckResult(id={self.id}, workflow_id={self.workflow_id}, check_type={self.check_type.value}, status={self.status.value})>"

