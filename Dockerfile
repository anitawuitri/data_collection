FROM python:3.9-slim

WORKDIR /app

# Install system dependencies if needed (e.g., for matplotlib)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
COPY visualization/requirements.txt visualization/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r visualization/requirements.txt

# Copy application code
COPY . .

# Make scripts executable
RUN chmod +x *.sh scripts/*.sh

# Set entrypoint (optional, can be overridden)
ENTRYPOINT ["/bin/bash"]
