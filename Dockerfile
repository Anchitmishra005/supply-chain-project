# =============================================================================
#  Dockerfile – Supply Chain Data Pipeline
# =============================================================================

FROM python:3.11-slim

# System dependencies for MySQL client
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Default command: run the ETL pipeline
CMD ["python", "-m", "etl.pipeline"]
