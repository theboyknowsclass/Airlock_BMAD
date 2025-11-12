"""
RabbitMQ exchange and queue definitions
"""
from typing import Dict, Any

# Exchange names
PACKAGE_EVENTS_EXCHANGE = "package.events"
WORKFLOW_EVENTS_EXCHANGE = "workflow.events"
CHECK_EVENTS_EXCHANGE = "check.events"
DLX_EXCHANGE = "dlx"  # Dead letter exchange

# Exchange configurations
EXCHANGE_CONFIGS: Dict[str, Dict[str, Any]] = {
    PACKAGE_EVENTS_EXCHANGE: {
        "type": "topic",
        "durable": True,
        "auto_delete": False,
    },
    WORKFLOW_EVENTS_EXCHANGE: {
        "type": "topic",
        "durable": True,
        "auto_delete": False,
    },
    CHECK_EVENTS_EXCHANGE: {
        "type": "topic",
        "durable": True,
        "auto_delete": False,
    },
    DLX_EXCHANGE: {
        "type": "direct",
        "durable": True,
        "auto_delete": False,
    },
}

# Routing key patterns
PACKAGE_EVENT_ROUTING_KEYS = {
    "submitted": "package.submitted",
    "validated": "package.validated",
    "requested": "package.requested",
    "stored": "package.stored",
    "published": "package.published",
}

WORKFLOW_EVENT_ROUTING_KEYS = {
    "created": "workflow.created",
    "approved": "workflow.approved",
    "rejected": "workflow.rejected",
    "completed": "workflow.completed",
}

CHECK_EVENT_ROUTING_KEYS = {
    "trivy_started": "check.trivy.started",
    "trivy_completed": "check.trivy.completed",
    "license_started": "check.license.started",
    "license_completed": "check.license.completed",
}

