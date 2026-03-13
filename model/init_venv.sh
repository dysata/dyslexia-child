#!/bin/bash
# model/init_venv.sh

MODEL_DIR="/app/model"
VENV_DIR="$MODEL_DIR/venv"
REQ_FILE="$MODEL_DIR/requirements.txt"
MARKER_FILE="$MODEL_DIR/.venv_installed_hash"

echo "Checking Model Environment..."

# 1. Calculate hash of current requirements.txt
if [ ! -f "$REQ_FILE" ]; then
    echo "Error: requirements.txt not found!"
    exit 1
fi
CURRENT_HASH=$(md5sum "$REQ_FILE" | awk '{print $1}')

# 2. Check if we need to reinstall
NEED_INSTALL=false

if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating..."
    NEED_INSTALL=true
elif [ ! -f "$MARKER_FILE" ]; then
    echo "Marker file missing. Reinstalling to be safe..."
    NEED_INSTALL=true
else
    STORED_HASH=$(cat "$MARKER_FILE")
    if [ "$CURRENT_HASH" != "$STORED_HASH" ]; then
        echo "requirements.txt changed. Updating environment..."
        NEED_INSTALL=true
    else
        echo "Environment is up to date."
    fi
fi

# 3. Perform Installation if needed
if [ "$NEED_INSTALL" = true ]; then
    echo "Setting up Python venv..."
    
    # Remove old venv if it exists to ensure clean state
    if [ -d "$VENV_DIR" ]; then
        rm -rf "$VENV_DIR"
    fi

    # Create venv
    python3 -m venv "$VENV_DIR"
    
    # Upgrade pip
    "$VENV_DIR/bin/pip" install --upgrade pip
    
    # Install requirements
    echo "Installing dependencies (this may take a while)..."
    "$VENV_DIR/bin/pip" install -r "$REQ_FILE"
    
    # Save hash marker
    echo "$CURRENT_HASH" > "$MARKER_FILE"
    echo "Saved current hash"

    echo "Model environment ready!"
else
    exit 0
fi
