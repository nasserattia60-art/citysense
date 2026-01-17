# Multi-stage build for CitySense
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/logs /app/media

# Collect static files
RUN python manage.py collectstatic --no-input --clear || true

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000

# Expose port (use static port for build, runtime uses $PORT)
EXPOSE 8000

# Run migrations and start server
CMD python manage.py migrate --no-input && exec gunicorn citysense.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --worker-class sync --max-requests 100 --timeout 30
