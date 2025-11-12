"""
Airlock Common - Shared Python utilities and models
"""

__version__ = "0.1.0"

# Database exports
from .db.database import get_db, Database
from .db.base import Base
from .db.models import (
    User,
    PackageSubmission,
    PackageRequest,
    Package,
    Workflow,
    CheckResult,
    AuditLog,
    APIKey,
    PackageUsage,
    LicenseAllowlist,
)

# Messaging exports (lazy import to avoid circular dependencies)
try:
    from .messaging.connection import get_rabbitmq_connection, RabbitMQConnection
    from .messaging.exchanges import (
        PACKAGE_EVENTS_EXCHANGE,
        WORKFLOW_EVENTS_EXCHANGE,
        CHECK_EVENTS_EXCHANGE,
        DLX_EXCHANGE,
    )
except ImportError:
    # pika may not be installed
    get_rabbitmq_connection = None
    RabbitMQConnection = None
    PACKAGE_EVENTS_EXCHANGE = None
    WORKFLOW_EVENTS_EXCHANGE = None
    CHECK_EVENTS_EXCHANGE = None
    DLX_EXCHANGE = None

__all__ = [
    "get_db",
    "Database",
    "Base",
    "User",
    "PackageSubmission",
    "PackageRequest",
    "Package",
    "Workflow",
    "CheckResult",
    "AuditLog",
    "APIKey",
    "PackageUsage",
    "LicenseAllowlist",
    "get_rabbitmq_connection",
    "RabbitMQConnection",
    "PACKAGE_EVENTS_EXCHANGE",
    "WORKFLOW_EVENTS_EXCHANGE",
    "CHECK_EVENTS_EXCHANGE",
    "DLX_EXCHANGE",
]

