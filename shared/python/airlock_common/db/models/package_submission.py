"""
Package Submission model
"""
import enum
from typing import List
from sqlalchemy import String, Text, ForeignKey, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base, TimestampMixin


class SubmissionStatus(enum.Enum):
    """Package submission status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PackageSubmission(Base, TimestampMixin):
    """Package Submission model"""
    __tablename__ = "package_submissions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    project_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    project_version: Mapped[str] = mapped_column(String(50), nullable=False)
    package_lock_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON content as text
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus),
        nullable=False,
        default=SubmissionStatus.PENDING,
        index=True
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="package_submissions")
    package_requests: Mapped[List["PackageRequest"]] = relationship(
        "PackageRequest",
        back_populates="submission",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<PackageSubmission(id={self.id}, user_id={self.user_id}, project_name={self.project_name}, status={self.status.value})>"

