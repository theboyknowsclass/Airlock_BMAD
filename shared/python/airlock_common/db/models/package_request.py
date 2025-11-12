"""
Package Request model
"""
from sqlalchemy import String, ForeignKey, Integer, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from ..base import Base, TimestampMixin


class PackageRequestStatus(enum.Enum):
    """Package request status"""
    PENDING = "pending"
    IN_WORKFLOW = "in_workflow"
    APPROVED = "approved"
    REJECTED = "rejected"


class PackageRequest(Base, TimestampMixin):
    """Package Request model"""
    __tablename__ = "package_requests"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("package_submissions.id"), nullable=False, index=True)
    package_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    package_version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[PackageRequestStatus] = mapped_column(
        Enum(PackageRequestStatus),
        nullable=False,
        default=PackageRequestStatus.PENDING,
        index=True
    )
    
    # Relationships
    submission: Mapped["PackageSubmission"] = relationship("PackageSubmission", back_populates="package_requests")
    workflow: Mapped["Workflow"] = relationship("Workflow", back_populates="package_request", uselist=False)
    package_usage: Mapped[List["PackageUsage"]] = relationship(
        "PackageUsage",
        back_populates="package_request",
        cascade="all, delete-orphan"
    )
    
    # Unique constraint on package_name + package_version + submission_id
    __table_args__ = (
        Index("ix_package_requests_name_version_submission", "package_name", "package_version", "submission_id", unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<PackageRequest(id={self.id}, submission_id={self.submission_id}, package_name={self.package_name}, package_version={self.package_version}, status={self.status.value})>"

