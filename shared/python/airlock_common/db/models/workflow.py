"""
Workflow model
"""
import enum
from typing import List
from sqlalchemy import String, ForeignKey, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base, TimestampMixin


class WorkflowStatus(enum.Enum):
    """Workflow status"""
    REQUESTED = "requested"
    FETCHING = "fetching"
    VALIDATING = "validating"
    CHECKING = "checking"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    REJECTED = "rejected"


class WorkflowStage(enum.Enum):
    """Workflow stage"""
    REQUESTED = "requested"
    FETCHING = "fetching"
    VALIDATING = "validating"
    CHECKING = "checking"
    REVIEWING = "reviewing"
    COMPLETED = "completed"


class Workflow(Base, TimestampMixin):
    """Workflow model"""
    __tablename__ = "workflows"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    package_request_id: Mapped[int] = mapped_column(
        ForeignKey("package_requests.id"),
        nullable=False,
        unique=True,
        index=True
    )
    status: Mapped[WorkflowStatus] = mapped_column(
        Enum(WorkflowStatus),
        nullable=False,
        default=WorkflowStatus.REQUESTED,
        index=True
    )
    current_stage: Mapped[WorkflowStage] = mapped_column(
        Enum(WorkflowStage),
        nullable=False,
        default=WorkflowStage.REQUESTED,
        index=True
    )
    
    # Relationships
    package_request: Mapped["PackageRequest"] = relationship("PackageRequest", back_populates="workflow")
    check_results: Mapped[List["CheckResult"]] = relationship(
        "CheckResult",
        back_populates="workflow",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Workflow(id={self.id}, package_request_id={self.package_request_id}, status={self.status.value}, current_stage={self.current_stage.value})>"

