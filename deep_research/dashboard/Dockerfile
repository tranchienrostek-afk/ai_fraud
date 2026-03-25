FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# We use the requirements.txt from the root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy dashboard code
COPY deep_research/dashboard ./dashboard

# Set working directory to dashboard for app.py
WORKDIR /app/dashboard

# Expose port 5000
EXPOSE 5000

# Command to run the dashboard
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
