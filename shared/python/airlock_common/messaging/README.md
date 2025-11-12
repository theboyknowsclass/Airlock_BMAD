# RabbitMQ Messaging Utilities

This package provides RabbitMQ connection management and initialization utilities for the Airlock system.

## Features

- **Connection Management**: Easy-to-use RabbitMQ connection utility with context manager support
- **Exchange Configuration**: Pre-configured exchanges for package, workflow, and check events
- **Dead Letter Queues**: Automatic dead letter queue configuration for error handling
- **Initialization Script**: Automated RabbitMQ initialization script

## Exchanges

The following exchanges are configured:

- **package.events**: Topic exchange for package-related events
- **workflow.events**: Topic exchange for workflow-related events
- **check.events**: Topic exchange for check-related events
- **dlx**: Direct exchange for dead letter queues

## Dead Letter Queues

The following dead letter queues are configured:

- **package.events.dlq**: Dead letter queue for package events
- **workflow.events.dlq**: Dead letter queue for workflow events
- **check.events.dlq**: Dead letter queue for check events

## Usage

### Connection

```python
from airlock_common.messaging.connection import get_rabbitmq_connection

# Using context manager (recommended)
with get_rabbitmq_connection() as conn:
    channel = conn.get_channel()
    # Use channel to publish/consume messages
    channel.basic_publish(
        exchange='package.events',
        routing_key='package.submitted',
        body='{"package": "example", "version": "1.0.0"}'
    )
```

### Environment Variables

The connection utility reads the following environment variables:

- `RABBITMQ_HOST`: RabbitMQ host (default: localhost)
- `RABBITMQ_PORT`: RabbitMQ port (default: 5672)
- `RABBITMQ_USER`: RabbitMQ username (default: guest)
- `RABBITMQ_PASSWORD`: RabbitMQ password (default: guest)
- `RABBITMQ_VHOST`: RabbitMQ virtual host (default: /)

### Initialization

To initialize RabbitMQ with exchanges and queues:

```bash
# From project root
cd shared/python/airlock_common
python scripts/init_rabbitmq.py
```

Or use the wait and init script:

```bash
# Linux/Mac
./scripts/wait_and_init_rabbitmq.sh

# Windows
.\scripts\wait_and_init_rabbitmq.ps1
```

## Testing

### Unit Tests (No RabbitMQ Required)

```bash
cd shared/python/airlock_common
pytest tests/test_rabbitmq_connection.py -v -k "not integration"
```

### Integration Tests (Requires RabbitMQ)

```bash
# Set environment variables
export RABBITMQ_HOST=localhost
export RABBITMQ_PORT=5672
export RABBITMQ_USER=guest
export RABBITMQ_PASSWORD=guest

# Run integration tests
cd shared/python/airlock_common
pytest tests/test_rabbitmq_connection.py -v -m integration
pytest tests/test_rabbitmq_init.py -v -m integration
```

## Docker Setup

When using Docker Compose, RabbitMQ is already configured in `docker-compose.prod.yml`. To initialize exchanges and queues after RabbitMQ is ready:

```bash
# Start RabbitMQ
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev up -d rabbitmq

# Wait for RabbitMQ to be ready (healthcheck)
docker-compose -f docker-compose.prod.yml -f docker-compose.dev.yml --env-file .env.dev ps rabbitmq

# Initialize RabbitMQ (from host machine)
export RABBITMQ_HOST=localhost
export RABBITMQ_PORT=5672
export RABBITMQ_USER=airlock
export RABBITMQ_PASSWORD=airlock
cd shared/python/airlock_common
python scripts/init_rabbitmq.py
```

## Management UI

The RabbitMQ management UI is available on port 15672 (in development):

- **URL**: http://localhost:15672
- **Username**: From `RABBITMQ_USER` environment variable
- **Password**: From `RABBITMQ_PASSWORD` environment variable

## Routing Keys

### Package Events

- `package.submitted`: Package submitted for approval
- `package.validated`: Package validation complete
- `package.requested`: Package request created
- `package.stored`: Package stored in artifact storage
- `package.published`: Package published to registry

### Workflow Events

- `workflow.created`: Workflow created
- `workflow.approved`: Workflow approved
- `workflow.rejected`: Workflow rejected
- `workflow.completed`: Workflow completed

### Check Events

- `check.trivy.started`: Trivy check started
- `check.trivy.completed`: Trivy check completed
- `check.license.started`: License check started
- `check.license.completed`: License check completed

## Examples

### Publishing a Message

```python
from airlock_common.messaging.connection import get_rabbitmq_connection
from airlock_common.messaging.exchanges import PACKAGE_EVENTS_EXCHANGE

with get_rabbitmq_connection() as conn:
    channel = conn.get_channel()
    channel.basic_publish(
        exchange=PACKAGE_EVENTS_EXCHANGE,
        routing_key='package.submitted',
        body='{"package": "example", "version": "1.0.0"}',
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
        )
    )
```

### Consuming Messages

```python
from airlock_common.messaging.connection import get_rabbitmq_connection
from airlock_common.messaging.exchanges import PACKAGE_EVENTS_EXCHANGE

def callback(ch, method, properties, body):
    print(f"Received: {body}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

with get_rabbitmq_connection() as conn:
    channel = conn.get_channel()
    queue = channel.queue_declare(queue='package.submitted.queue', durable=True)
    channel.queue_bind(
        queue='package.submitted.queue',
        exchange=PACKAGE_EVENTS_EXCHANGE,
        routing_key='package.submitted'
    )
    channel.basic_consume(
        queue='package.submitted.queue',
        on_message_callback=callback
    )
    channel.start_consuming()
```

## Error Handling

Messages that fail processing or are rejected are automatically routed to dead letter queues:

- Failed package events → `package.events.dlq`
- Failed workflow events → `workflow.events.dlq`
- Failed check events → `check.events.dlq`

Dead letter queues are bound to the `dlx` exchange with routing keys matching the queue name.

