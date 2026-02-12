# Production Web Console Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose web port
EXPOSE 8501

# Run web console

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Healthcheck contract:
# - Endpoint: GET /healthz on port 8501
# - Returns HTTP 200 when critical dependencies are healthy
# - Returns HTTP 503 when service is degraded/unhealthy
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD ["curl", "--fail", "--silent", "--show-error", "http://127.0.0.1:8501/healthz"]

RUN useradd -m -u 10001 appuser && chown -R appuser:appuser /app

USER appuser

CMD ["uvicorn", "src.main:app", "--host=0.0.0.0", "--port=8501"]
