@echo off
REM Claude Coder Agent Runner Script for Windows
REM This script builds and runs the Claude Coder Agent Docker container

echo 🚀 Claude Coder Agent - Docker Edition
echo ======================================

REM Create necessary directories
if not exist "scans" mkdir scans
if not exist "logs" mkdir logs
if not exist "data" mkdir data

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker and try again.
    pause
    exit /b 1
)

REM Build the Docker image
echo 🔨 Building Claude Coder Agent Docker image...
docker build -f Dockerfile.claude_coder -t claude-coder-agent .

REM Run the container
echo 🚀 Starting Claude Coder Agent...
docker run --rm ^
    -v "%cd%:/app/codebase:ro" ^
    -v "%cd%/scans:/app/scans" ^
    -v "%cd%/logs:/app/logs" ^
    -v "%cd%/data:/app/data" ^
    -e CLAUDE_API_KEY="sk-your-api-key" ^
    -e DEEPSEEK_API_KEY="sk-your-api-key" ^
    -e PYTHONPATH="/app" ^
    --name claude-coder-agent ^
    claude-coder-agent

echo ✅ Claude Coder Agent scan completed!
echo 📁 Scan results saved to: ./scans/
echo 📋 Logs saved to: ./logs/
pause 