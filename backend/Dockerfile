# backend/Dockerfile
FROM python:3.11-slim-bookworm

# Install system dependencies for networking and postgres
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    curl \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1