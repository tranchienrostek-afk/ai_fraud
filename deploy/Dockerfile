# Use lightweight Python image (no Playwright)
FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Install system dependencies first (better caching)
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* \
    && apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# Create virtual environment
RUN python -m venv /opt/venv

# Update PATH to use virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --default-timeout=120 --retries=5 --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
