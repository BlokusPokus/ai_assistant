# Multi-stage Dockerfile for Personal Assistant TDAH
# Optimized for production with security hardening

# ===== STAGE 1: Build Environment =====
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ===== STAGE 2: Production Runtime =====
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app/src" \
    ENVIRONMENT="production"

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create application directory
WORKDIR /app

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Set proper permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/overall || exit 1

# Default command
CMD ["python", "-m", "uvicorn", "apps.fastapi_app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ===== STAGE 3: Development (optional) =====
FROM production as development

# Switch back to root for development tools
USER root

# Install development dependencies
RUN apt-get update && apt-get install -y \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Install development Python packages
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    black \
    flake8 \
    mypy

# Switch back to appuser
USER appuser

# Set development environment
ENV ENVIRONMENT="development" \
    DEBUG="true"

# Development command with hot reload
CMD ["python", "-m", "uvicorn", "apps.fastapi_app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 