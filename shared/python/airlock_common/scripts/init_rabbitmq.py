"""
RabbitMQ initialization script
Waits for RabbitMQ to be ready, then configures exchanges and queues
"""
import sys
import os
import time
import logging

# Add parent directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
shared_dir = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, shared_dir)

# Import directly from messaging module to avoid importing database models
from airlock_common.messaging.init_rabbitmq import initialize_rabbitmq
from airlock_common.messaging.connection import get_rabbitmq_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def wait_for_rabbitmq(max_attempts: int = 30, delay: int = 2):
    """
    Wait for RabbitMQ to be ready
    
    Args:
        max_attempts: Maximum number of connection attempts
        delay: Delay between attempts (seconds)
        
    Returns:
        True if RabbitMQ is ready, False otherwise
    """
    logger.info("Waiting for RabbitMQ to be ready...")
    
    for attempt in range(1, max_attempts + 1):
        try:
            with get_rabbitmq_connection() as conn:
                channel = conn.get_channel()
                # Try to declare a test queue to verify connection
                channel.queue_declare(queue="test", durable=False, auto_delete=True)
                channel.queue_delete(queue="test")
                logger.info("RabbitMQ is ready!")
                return True
        except Exception as e:
            if attempt < max_attempts:
                logger.info(f"Attempt {attempt}/{max_attempts}: RabbitMQ not ready yet, waiting {delay}s...")
                time.sleep(delay)
            else:
                logger.error(f"Failed to connect to RabbitMQ after {max_attempts} attempts: {e}")
                return False
    
    return False


def main():
    """Main initialization function"""
    logger.info("Starting RabbitMQ initialization...")
    
    # Wait for RabbitMQ to be ready
    if not wait_for_rabbitmq():
        logger.error("RabbitMQ is not ready. Exiting.")
        sys.exit(1)
    
    # Initialize RabbitMQ configuration
    if not initialize_rabbitmq():
        logger.error("Failed to initialize RabbitMQ configuration. Exiting.")
        sys.exit(1)
    
    logger.info("RabbitMQ initialization completed successfully!")
    sys.exit(0)


if __name__ == "__main__":
    main()

