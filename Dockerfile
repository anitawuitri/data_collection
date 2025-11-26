FROM python:3.9-slim

WORKDIR /app

# Install system dependencies if needed (e.g., for matplotlib)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Create user with a fixed UID/GID (will be overridden by entrypoint if needed, but good to have)
RUN groupadd -g 1000 user && \
    useradd -m -u 1000 -g 1000 -s /bin/bash user

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

# Set entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
