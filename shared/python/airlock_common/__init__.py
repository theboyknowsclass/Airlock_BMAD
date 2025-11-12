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

# Utility exports
from .utils import (
    setup_logging,
    get_logger,
    AirlockError,
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    ServiceUnavailableError,
    validate_email,
    validate_url,
    validate_uuid,
    get_env,
    get_env_int,
    get_env_bool,
    get_env_list,
)

# Constants exports
from .constants import (
    API_VERSION,
    API_PREFIX,
    HEALTH_ENDPOINT,
    LIVE_ENDPOINT,
    READY_ENDPOINT,
    HTTP_STATUS_OK,
    HTTP_STATUS_CREATED,
    HTTP_STATUS_BAD_REQUEST,
    HTTP_STATUS_UNAUTHORIZED,
    HTTP_STATUS_FORBIDDEN,
    HTTP_STATUS_NOT_FOUND,
    HTTP_STATUS_CONFLICT,
    HTTP_STATUS_INTERNAL_SERVER_ERROR,
    HTTP_STATUS_SERVICE_UNAVAILABLE,
    ERROR_CODE_VALIDATION_ERROR,
    ERROR_CODE_NOT_FOUND,
    ERROR_CODE_UNAUTHORIZED,
    ERROR_CODE_FORBIDDEN,
    ERROR_CODE_CONFLICT,
    ERROR_CODE_INTERNAL_SERVER_ERROR,
    ERROR_CODE_SERVICE_UNAVAILABLE,
    ROLE_SUBMITTER,
    ROLE_REVIEWER,
    ROLE_ADMIN,
    ROLES,
)

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
    "setup_logging",
    "get_logger",
    "AirlockError",
    "ValidationError",
    "NotFoundError",
    "UnauthorizedError",
    "ForbiddenError",
    "ConflictError",
    "ServiceUnavailableError",
    "validate_email",
    "validate_url",
    "validate_uuid",
    "get_env",
    "get_env_int",
    "get_env_bool",
    "get_env_list",
    "API_VERSION",
    "API_PREFIX",
    "HEALTH_ENDPOINT",
    "LIVE_ENDPOINT",
    "READY_ENDPOINT",
    "HTTP_STATUS_OK",
    "HTTP_STATUS_CREATED",
    "HTTP_STATUS_BAD_REQUEST",
    "HTTP_STATUS_UNAUTHORIZED",
    "HTTP_STATUS_FORBIDDEN",
    "HTTP_STATUS_NOT_FOUND",
    "HTTP_STATUS_CONFLICT",
    "HTTP_STATUS_INTERNAL_SERVER_ERROR",
    "HTTP_STATUS_SERVICE_UNAVAILABLE",
    "ERROR_CODE_VALIDATION_ERROR",
    "ERROR_CODE_NOT_FOUND",
    "ERROR_CODE_UNAUTHORIZED",
    "ERROR_CODE_FORBIDDEN",
    "ERROR_CODE_CONFLICT",
    "ERROR_CODE_INTERNAL_SERVER_ERROR",
    "ERROR_CODE_SERVICE_UNAVAILABLE",
    "ROLE_SUBMITTER",
    "ROLE_REVIEWER",
    "ROLE_ADMIN",
    "ROLES",
]

