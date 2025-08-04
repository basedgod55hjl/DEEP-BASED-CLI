#!/bin/bash

# Claude Coder Agent Runner Script
# This script builds and runs the Claude Coder Agent Docker container

set -e

echo "🚀 Claude Coder Agent - Docker Edition"
echo "======================================"

# Create necessary directories
mkdir -p scans logs data

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build the Docker image
echo "🔨 Building Claude Coder Agent Docker image..."
docker build -f Dockerfile.claude_coder -t claude-coder-agent .

# Run the container
echo "🚀 Starting Claude Coder Agent..."
docker run --rm \
    -v "$(pwd):/app/codebase:ro" \
    -v "$(pwd)/scans:/app/scans" \
    -v "$(pwd)/logs:/app/logs" \
    -v "$(pwd)/data:/app/data" \
    -e CLAUDE_API_KEY="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" \
    -e DEEPSEEK_API_KEY="sk-90e0dd863b8c4e0d879a02851a0ee194" \
    -e PYTHONPATH="/app" \
    --name claude-coder-agent \
    claude-coder-agent

echo "✅ Claude Coder Agent scan completed!"
echo "📁 Scan results saved to: ./scans/"
echo "📋 Logs saved to: ./logs/" 