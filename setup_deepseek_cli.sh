#!/bin/bash

# DeepSeek CLI Setup Script
# This script sets up the DeepSeek CLI environment

echo "======================================"
echo "DeepSeek CLI Setup"
echo "======================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python $python_version is installed, but Python $required_version or later is required."
    exit 1
fi

echo "✓ Python $python_version detected"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"

# Check for .env file
if [ ! -f ".env" ]; then
    echo
    echo "⚠️  No .env file found. Creating from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ Created .env file from .env.example"
        echo
        echo "⚠️  Please edit .env and add your DeepSeek API key"
        echo "   You can get your API key from: https://platform.deepseek.com/api_keys"
    else
        # Create a basic .env file
        echo "# DeepSeek API Configuration" > .env
        echo "DEEPSEEK_API_KEY=your-api-key-here" >> .env
        echo "DEEPSEEK_API_ENDPOINT=https://api.deepseek.com/v1" >> .env
        echo "DEEPSEEK_MODEL=deepseek-chat" >> .env
        echo "✓ Created basic .env file"
        echo
        echo "⚠️  Please edit .env and replace 'your-api-key-here' with your actual API key"
        echo "   You can get your API key from: https://platform.deepseek.com/api_keys"
    fi
else
    echo "✓ .env file found"
fi

# Create run script
echo "Creating run script..."
cat > run_deepseek_cli.sh << 'EOF'
#!/bin/bash
# Activate virtual environment and run DeepSeek CLI

if [ -d "venv" ]; then
    source venv/bin/activate
    python deepseek_cli.py "$@"
else
    echo "Error: Virtual environment not found. Please run setup_deepseek_cli.sh first."
    exit 1
fi
EOF

chmod +x run_deepseek_cli.sh
echo "✓ Run script created"

# Create a system-wide command (optional)
echo
read -p "Would you like to create a system-wide 'deepseek' command? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Get the current directory
    current_dir=$(pwd)
    
    # Create alias command
    alias_command="alias deepseek='cd $current_dir && ./run_deepseek_cli.sh'"
    
    # Detect shell and add alias
    if [ -f "$HOME/.bashrc" ]; then
        if ! grep -q "alias deepseek=" "$HOME/.bashrc"; then
            echo "$alias_command" >> "$HOME/.bashrc"
            echo "✓ Added 'deepseek' alias to ~/.bashrc"
        fi
    fi
    
    if [ -f "$HOME/.zshrc" ]; then
        if ! grep -q "alias deepseek=" "$HOME/.zshrc"; then
            echo "$alias_command" >> "$HOME/.zshrc"
            echo "✓ Added 'deepseek' alias to ~/.zshrc"
        fi
    fi
    
    echo
    echo "✓ System-wide command created!"
    echo "  Restart your terminal or run 'source ~/.bashrc' (or ~/.zshrc) to use it."
fi

echo
echo "======================================"
echo "Setup completed successfully!"
echo "======================================"
echo
echo "To run DeepSeek CLI:"
echo "  ./run_deepseek_cli.sh"
echo
echo "Or with arguments:"
echo "  ./run_deepseek_cli.sh --help"
echo "  ./run_deepseek_cli.sh --chat \"Hello, how are you?\""
echo "  ./run_deepseek_cli.sh --reason \"What is 2+2?\""
echo "  ./run_deepseek_cli.sh --code \"fibonacci sequence\""
echo
echo "Enjoy using DeepSeek CLI!"