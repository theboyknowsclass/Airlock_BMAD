"""
Audit service for logging user management actions
"""
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from airlock_common.db.models.audit_log import AuditLog
import logging
import json

logger = logging.getLogger(__name__)


class AuditService:
    """Service for audit logging"""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize audit service
        
        Args:
            session: Database session
        """
        self.session = session
    
    async def log_action(
        self,
        user_id: Optional[int],
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """
        Log an audit action
        
        Args:
            user_id: ID of user performing the action (None for system actions)
            action: Action name (e.g., "user.created", "user.updated", "user.roles_updated")
            resource_type: Type of resource (e.g., "user", "package")
            resource_id: ID of the resource (optional)
            details: Additional details as dictionary (will be serialized to JSON)
        
        Returns:
            AuditLog: Created audit log entry
        """
        details_json = None
        if details:
            details_json = json.dumps(details)
        
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details_json,
            timestamp=datetime.utcnow(),
        )
        
        self.session.add(audit_log)
        await self.session.flush()
        await self.session.refresh(audit_log)
        
        logger.info(
            f"Audit log: user_id={user_id}, action={action}, "
            f"resource_type={resource_type}, resource_id={resource_id}"
        )
        
        return audit_log

