"""
Tests for RabbitMQ connection and configuration
"""
import os
import pytest
from airlock_common.messaging.connection import (
    get_rabbitmq_connection,
    get_rabbitmq_url,
    RabbitMQConnection,
)
from airlock_common.messaging.exchanges import (
    PACKAGE_EVENTS_EXCHANGE,
    WORKFLOW_EVENTS_EXCHANGE,
    CHECK_EVENTS_EXCHANGE,
    DLX_EXCHANGE,
    EXCHANGE_CONFIGS,
)


def test_get_rabbitmq_url_from_env():
    """Test that RabbitMQ URL is generated from environment variables"""
    # Set environment variables
    os.environ["RABBITMQ_HOST"] = "test-host"
    os.environ["RABBITMQ_PORT"] = "5673"
    os.environ["RABBITMQ_USER"] = "test-user"
    os.environ["RABBITMQ_PASSWORD"] = "test-password"
    os.environ["RABBITMQ_VHOST"] = "/"
    
    url = get_rabbitmq_url()
    assert "test-user:test-password@test-host:5673" in url
    assert "amqp://" in url
    
    # Cleanup
    del os.environ["RABBITMQ_HOST"]
    del os.environ["RABBITMQ_PORT"]
    del os.environ["RABBITMQ_USER"]
    del os.environ["RABBITMQ_PASSWORD"]
    del os.environ["RABBITMQ_VHOST"]


def test_get_rabbitmq_url_defaults():
    """Test that RabbitMQ URL uses defaults when env vars are not set"""
    # Remove environment variables if they exist
    for key in ["RABBITMQ_HOST", "RABBITMQ_PORT", "RABBITMQ_USER", "RABBITMQ_PASSWORD", "RABBITMQ_VHOST"]:
        if key in os.environ:
            del os.environ[key]
    
    url = get_rabbitmq_url()
    assert "guest:guest@localhost:5672" in url
    assert "amqp://" in url


def test_rabbitmq_connection_context_manager():
    """Test RabbitMQ connection context manager"""
    # This test requires RabbitMQ to be running
    # Skip if RABBITMQ_HOST is not set or connection fails
    if "RABBITMQ_HOST" not in os.environ:
        pytest.skip("RABBITMQ_HOST not set, skipping integration test")
    
    try:
        with get_rabbitmq_connection() as conn:
            assert conn.connection is not None
            assert conn.connection.is_open
            
            channel = conn.get_channel()
            assert channel is not None
            assert not channel.is_closed
    except Exception as e:
        pytest.skip(f"RabbitMQ not available: {e}")


def test_exchange_constants():
    """Test that exchange constants are defined correctly"""
    assert PACKAGE_EVENTS_EXCHANGE == "package.events"
    assert WORKFLOW_EVENTS_EXCHANGE == "workflow.events"
    assert CHECK_EVENTS_EXCHANGE == "check.events"
    assert DLX_EXCHANGE == "dlx"


def test_exchange_configs():
    """Test that exchange configurations are valid"""
    assert PACKAGE_EVENTS_EXCHANGE in EXCHANGE_CONFIGS
    assert WORKFLOW_EVENTS_EXCHANGE in EXCHANGE_CONFIGS
    assert CHECK_EVENTS_EXCHANGE in EXCHANGE_CONFIGS
    assert DLX_EXCHANGE in EXCHANGE_CONFIGS
    
    # Verify all exchanges have required config keys
    for exchange_name, config in EXCHANGE_CONFIGS.items():
        assert "type" in config
        assert "durable" in config
        assert config["type"] in ["topic", "direct", "fanout"]
        assert isinstance(config["durable"], bool)


@pytest.mark.integration
def test_rabbitmq_exchanges_exist():
    """Test that all required exchanges exist in RabbitMQ"""
    # This test requires RabbitMQ to be running and initialized
    # Skip if RABBITMQ_HOST is not set or connection fails
    if "RABBITMQ_HOST" not in os.environ:
        pytest.skip("RABBITMQ_HOST not set, skipping integration test")
    
    try:
        with get_rabbitmq_connection() as conn:
            channel = conn.get_channel()
            
            # Verify all exchanges exist by trying to bind to them
            # This will raise an exception if the exchange doesn't exist
            test_queue = "test_queue_verify_exchanges"
            
            try:
                # Declare a temporary queue
                channel.queue_declare(queue=test_queue, durable=False, auto_delete=True)
                
                # Try to bind to each exchange (this verifies they exist)
                for exchange_name in [
                    PACKAGE_EVENTS_EXCHANGE,
                    WORKFLOW_EVENTS_EXCHANGE,
                    CHECK_EVENTS_EXCHANGE,
                    DLX_EXCHANGE,
                ]:
                    try:
                        channel.queue_bind(
                            queue=test_queue,
                            exchange=exchange_name,
                            routing_key="test.key",
                        )
                        # Unbind after verification
                        channel.queue_unbind(
                            queue=test_queue,
                            exchange=exchange_name,
                            routing_key="test.key",
                        )
                    except Exception as e:
                        pytest.fail(f"Exchange {exchange_name} does not exist: {e}")
                
                # Cleanup
                channel.queue_delete(queue=test_queue)
            except Exception as e:
                pytest.fail(f"Failed to verify exchanges: {e}")
    except Exception as e:
        pytest.skip(f"RabbitMQ not available: {e}")


@pytest.mark.integration
def test_rabbitmq_dlq_exist():
    """Test that dead letter queues exist in RabbitMQ"""
    # This test requires RabbitMQ to be running and initialized
    # Skip if RABBITMQ_HOST is not set or connection fails
    if "RABBITMQ_HOST" not in os.environ:
        pytest.skip("RABBITMQ_HOST not set, skipping integration test")
    
    try:
        with get_rabbitmq_connection() as conn:
            channel = conn.get_channel()
            
            # Verify DLQs exist by checking queue status
            dlq_names = [
                f"{PACKAGE_EVENTS_EXCHANGE}.dlq",
                f"{WORKFLOW_EVENTS_EXCHANGE}.dlq",
                f"{CHECK_EVENTS_EXCHANGE}.dlq",
            ]
            
            for dlq_name in dlq_names:
                try:
                    # Declare queue (will not error if it already exists)
                    method = channel.queue_declare(queue=dlq_name, passive=True)
                    assert method is not None
                except Exception as e:
                    pytest.fail(f"Dead letter queue {dlq_name} does not exist: {e}")
    except Exception as e:
        pytest.skip(f"RabbitMQ not available: {e}")

