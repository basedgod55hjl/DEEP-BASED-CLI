#!/bin/bash
# 🚀 BASED CODER CLI - Run Script
# Made by @Lucariolucario55 on Telegram

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run the main CLI
python main.py "$@"