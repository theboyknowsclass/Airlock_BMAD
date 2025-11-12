"""
RabbitMQ initialization script
Configures exchanges, queues, and dead letter queues
"""
import sys
import os
import logging
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from airlock_common.messaging.connection import get_rabbitmq_connection
from airlock_common.messaging.exchanges import (
    EXCHANGE_CONFIGS,
    PACKAGE_EVENTS_EXCHANGE,
    WORKFLOW_EVENTS_EXCHANGE,
    CHECK_EVENTS_EXCHANGE,
    DLX_EXCHANGE,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def declare_exchange(channel, exchange_name: str, config: Dict[str, Any]):
    """
    Declare an exchange
    
    Args:
        channel: RabbitMQ channel
        exchange_name: Exchange name
        config: Exchange configuration
    """
    try:
        channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=config["type"],
            durable=config["durable"],
            auto_delete=config.get("auto_delete", False),
        )
        logger.info(f"Declared exchange: {exchange_name} ({config['type']})")
    except Exception as e:
        logger.error(f"Failed to declare exchange {exchange_name}: {e}")
        raise


def declare_dlq(channel, queue_name: str, dlx_name: str = DLX_EXCHANGE):
    """
    Declare a dead letter queue
    
    Args:
        channel: RabbitMQ channel
        queue_name: Queue name (e.g., "package.events.dlq")
        dlx_name: Dead letter exchange name
    """
    try:
        # Declare DLQ as a regular durable queue
        channel.queue_declare(
            queue=queue_name,
            durable=True,
        )
        # Bind DLQ to DLX with routing key matching queue name
        channel.queue_bind(
            queue=queue_name,
            exchange=dlx_name,
            routing_key=queue_name,
        )
        logger.info(f"Declared dead letter queue: {queue_name}")
    except Exception as e:
        logger.error(f"Failed to declare DLQ {queue_name}: {e}")
        raise


def initialize_rabbitmq():
    """
    Initialize RabbitMQ exchanges and queues
    """
    logger.info("Initializing RabbitMQ configuration...")
    
    try:
        with get_rabbitmq_connection() as conn:
            channel = conn.get_channel()
            
            # Declare dead letter exchange first
            logger.info("Declaring dead letter exchange...")
            declare_exchange(channel, DLX_EXCHANGE, EXCHANGE_CONFIGS[DLX_EXCHANGE])
            
            # Declare main exchanges
            logger.info("Declaring main exchanges...")
            for exchange_name, config in EXCHANGE_CONFIGS.items():
                if exchange_name != DLX_EXCHANGE:
                    declare_exchange(channel, exchange_name, config)
            
            # Declare dead letter queues for each exchange
            logger.info("Declaring dead letter queues...")
            dlq_names = [
                f"{PACKAGE_EVENTS_EXCHANGE}.dlq",
                f"{WORKFLOW_EVENTS_EXCHANGE}.dlq",
                f"{CHECK_EVENTS_EXCHANGE}.dlq",
            ]
            
            for dlq_name in dlq_names:
                declare_dlq(channel, dlq_name, DLX_EXCHANGE)
            
            logger.info("RabbitMQ initialization completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"Failed to initialize RabbitMQ: {e}")
        return False


if __name__ == "__main__":
    success = initialize_rabbitmq()
    sys.exit(0 if success else 1)

