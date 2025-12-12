# Multi-stage build untuk optimasi ukuran image
FROM python:3.11-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy dependencies dari builder stage
COPY --from=builder /root/.local /root/.local

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/

# Pastikan scripts di PATH
ENV PATH=/root/.local/bin:$PATH

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV SECRET_KEY="production-secret-key-change-this"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/docs')" || exit 1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]