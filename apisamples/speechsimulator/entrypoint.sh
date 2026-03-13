#!/bin/sh
set -e

# Define the base storage path
STORAGE_DIR="/app/storage"

# List of required subdirectories
SUBDIRS="game1 game1d game2 game2d game3 game3f rrrex tmp"

echo "Checking/creating storage structure in $STORAGE_DIR..."

# Ensure base directory exists
mkdir -p "$STORAGE_DIR"

# Create subdirectories if they don't exist
for dir in $SUBDIRS; do
    if [ ! -d "$STORAGE_DIR/$dir" ]; then
        echo "Creating directory: $STORAGE_DIR/$dir"
        mkdir -p "$STORAGE_DIR/$dir"
    fi
done

echo "Storage ready. Starting application..."

# Execute the main command passed to docker (or default CMD from Dockerfile)
exec "$@"

