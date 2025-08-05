#!/bin/bash

echo "🏦 Starting Enhanced Banking Assistant Backend (Modular)"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Check if Ollama is running
echo "Checking Ollama connection..."
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "⚠️  Warning: Ollama is not running on localhost:11434"
    echo "   Please start Ollama first: ollama serve"
    echo "   Then pull the model: ollama pull small-bank-chat"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting..."
        exit 1
    fi
fi

# Start the application
echo "Starting Flask application..."
echo "=================================================="
python app_new.py 