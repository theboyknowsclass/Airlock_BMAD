# Multi-stage build for API Key Service
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy shared library and requirements
COPY shared/python/airlock_common /tmp/airlock_common
COPY services/api-key-service/requirements.txt /tmp/requirements.txt

# Install shared library first
RUN pip install --no-cache-dir --user -e /tmp/airlock_common

# Install other dependencies (skip the -e line for shared library)
RUN pip install --no-cache-dir --user \
    fastapi==0.115.0 \
    uvicorn[standard]==0.32.1 \
    python-multipart==0.0.12 \
    pydantic==2.10.4 \
    pydantic-settings==2.7.1 \
    sqlalchemy[asyncio]==2.0.36 \
    asyncpg==0.30.0 \
    aiosqlite==0.20.0 \
    bcrypt==4.2.0 \
    PyJWT==2.9.0 \
    cryptography==43.0.3 \
    httpx==0.27.2

# Production stage
FROM python:3.12-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy shared library to production stage (needed for editable install)
COPY shared/python/airlock_common /tmp/airlock_common

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY services/api-key-service/src/ ./src/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
