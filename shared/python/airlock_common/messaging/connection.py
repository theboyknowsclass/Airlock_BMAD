"""
RabbitMQ connection management
"""
import os
import logging
from typing import Optional
import pika
from pika.connection import URLParameters
from pika.exceptions import AMQPConnectionError, AMQPChannelError

logger = logging.getLogger(__name__)


def get_rabbitmq_url() -> str:
    """
    Get RabbitMQ connection URL from environment variables
    
    Returns:
        RabbitMQ connection URL in format: amqp://user:password@host:port/vhost
        
    Environment Variables:
        RABBITMQ_HOST: RabbitMQ host (default: localhost)
        RABBITMQ_PORT: RabbitMQ port (default: 5672)
        RABBITMQ_USER: RabbitMQ username (default: guest)
        RABBITMQ_PASSWORD: RabbitMQ password (default: guest)
        RABBITMQ_VHOST: RabbitMQ virtual host (default: /)
    """
    host = os.getenv("RABBITMQ_HOST", "localhost")
    port = os.getenv("RABBITMQ_PORT", "5672")
    user = os.getenv("RABBITMQ_USER", "guest")
    password = os.getenv("RABBITMQ_PASSWORD", "guest")
    vhost = os.getenv("RABBITMQ_VHOST", "/")
    
    # URL encode vhost if needed (replace / with %2F)
    if vhost == "/":
        vhost_encoded = "%2F"
    else:
        vhost_encoded = vhost.replace("/", "%2F")
    
    return f"amqp://{user}:{password}@{host}:{port}/{vhost_encoded}"


class RabbitMQConnection:
    """RabbitMQ connection manager"""
    
    def __init__(
        self,
        rabbitmq_url: Optional[str] = None,
        connection_attempts: int = 3,
        retry_delay: int = 2,
    ):
        """
        Initialize RabbitMQ connection
        
        Args:
            rabbitmq_url: RabbitMQ connection URL (default: from environment)
            connection_attempts: Number of connection attempts
            retry_delay: Delay between retry attempts (seconds)
        """
        self.rabbitmq_url = rabbitmq_url or get_rabbitmq_url()
        self.connection_attempts = connection_attempts
        self.retry_delay = retry_delay
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
    
    def connect(self) -> pika.BlockingConnection:
        """
        Establish connection to RabbitMQ
        
        Returns:
            RabbitMQ connection
            
        Raises:
            AMQPConnectionError: If connection fails
        """
        if self.connection and self.connection.is_open:
            return self.connection
        
        parameters = URLParameters(self.rabbitmq_url)
        parameters.connection_attempts = self.connection_attempts
        parameters.retry_delay = self.retry_delay
        
        try:
            self.connection = pika.BlockingConnection(parameters)
            logger.info("Connected to RabbitMQ")
            return self.connection
        except AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def get_channel(self) -> pika.channel.Channel:
        """
        Get or create a channel
        
        Returns:
            RabbitMQ channel
            
        Raises:
            AMQPConnectionError: If connection fails
            AMQPChannelError: If channel creation fails
        """
        if not self.connection or not self.connection.is_open:
            self.connect()
        
        if not self.channel or self.channel.is_closed:
            self.channel = self.connection.channel()
            logger.debug("Created RabbitMQ channel")
        
        return self.channel
    
    def close(self):
        """Close connection and channel"""
        if self.channel and self.channel.is_open:
            self.channel.close()
            logger.debug("Closed RabbitMQ channel")
        
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info("Closed RabbitMQ connection")
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def __del__(self):
        """Cleanup on deletion"""
        try:
            self.close()
        except Exception:
            pass


def get_rabbitmq_connection(
    rabbitmq_url: Optional[str] = None,
    connection_attempts: int = 3,
    retry_delay: int = 2,
) -> RabbitMQConnection:
    """
    Get RabbitMQ connection instance
    
    Args:
        rabbitmq_url: RabbitMQ connection URL (default: from environment)
        connection_attempts: Number of connection attempts
        retry_delay: Delay between retry attempts (seconds)
        
    Returns:
        RabbitMQConnection instance
    """
    return RabbitMQConnection(
        rabbitmq_url=rabbitmq_url,
        connection_attempts=connection_attempts,
        retry_delay=retry_delay,
    )

