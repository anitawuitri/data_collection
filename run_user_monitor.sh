#!/bin/bash
IMAGE_NAME="gpu-monitor"

# Build image if not exists or if --build flag is passed
if [[ "$1" == "--build" ]] || [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" == "" ]]; then
    echo "Building Docker image..."
    docker build -t $IMAGE_NAME .
    if [[ "$1" == "--build" ]]; then
        shift # Remove --build from args
    fi
fi

# Ensure directories exist
mkdir -p data plots data_archive

# Run container
# --user: Run as current user to avoid permission issues with mounted volumes
# -e USER: Pass current username
# -v: Mount data directories
docker run --rm -it \
    --user $(id -u):$(id -g) \
    -e USER=$(whoami) \
    -e MPLCONFIGDIR=/tmp/matplotlib_cache \
    -v "$(pwd)/data:/app/data" \
    -v "$(pwd)/plots:/app/plots" \
    -v "$(pwd)/data_archive:/app/data_archive" \
    $IMAGE_NAME ./run_internal.sh "$@"
