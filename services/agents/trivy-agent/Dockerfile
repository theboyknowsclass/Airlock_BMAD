# Placeholder Dockerfile for api-gateway service
# TODO: Implement multi-stage build

FROM python:3.12-slim

WORKDIR /app

# Placeholder - will be implemented in Story 1.5
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

