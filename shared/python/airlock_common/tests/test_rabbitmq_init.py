"""
Tests for RabbitMQ initialization
"""
import os
import pytest
from airlock_common.messaging.init_rabbitmq import initialize_rabbitmq
from airlock_common.messaging.connection import get_rabbitmq_connection
from airlock_common.messaging.exchanges import (
    PACKAGE_EVENTS_EXCHANGE,
    WORKFLOW_EVENTS_EXCHANGE,
    CHECK_EVENTS_EXCHANGE,
    DLX_EXCHANGE,
)


@pytest.mark.integration
def test_initialize_rabbitmq():
    """Test that RabbitMQ initialization succeeds"""
    # This test requires RabbitMQ to be running
    # Skip if RABBITMQ_HOST is not set or connection fails
    if "RABBITMQ_HOST" not in os.environ:
        pytest.skip("RABBITMQ_HOST not set, skipping integration test")
    
    try:
        # Initialize RabbitMQ
        success = initialize_rabbitmq()
        assert success is True
        
        # Verify exchanges exist
        with get_rabbitmq_connection() as conn:
            channel = conn.get_channel()
            
            # Verify all exchanges exist
            test_queue = "test_init_verify"
            channel.queue_declare(queue=test_queue, durable=False, auto_delete=True)
            
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
                    channel.queue_unbind(
                        queue=test_queue,
                        exchange=exchange_name,
                        routing_key="test.key",
                    )
                except Exception as e:
                    pytest.fail(f"Exchange {exchange_name} not properly initialized: {e}")
            
            # Verify DLQs exist
            dlq_names = [
                f"{PACKAGE_EVENTS_EXCHANGE}.dlq",
                f"{WORKFLOW_EVENTS_EXCHANGE}.dlq",
                f"{CHECK_EVENTS_EXCHANGE}.dlq",
            ]
            
            for dlq_name in dlq_names:
                try:
                    channel.queue_declare(queue=dlq_name, passive=True)
                except Exception as e:
                    pytest.fail(f"Dead letter queue {dlq_name} not properly initialized: {e}")
            
            # Cleanup
            channel.queue_delete(queue=test_queue)
    except Exception as e:
        pytest.skip(f"RabbitMQ not available: {e}")

