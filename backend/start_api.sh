#!/bin/bash

# Email Auto Responder API Startup Script

echo "Starting Email Auto Responder API..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if required environment variables are set
if [ -z "$MY_EMAIL" ]; then
    echo "Warning: MY_EMAIL environment variable not set"
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "Warning: OPENAI_API_KEY environment variable not set"
fi

# Install dependencies if needed
echo "Installing/updating dependencies..."
pip install -e .

# Start the API server
echo "Starting API server on http://localhost:8002"
python api_server.py