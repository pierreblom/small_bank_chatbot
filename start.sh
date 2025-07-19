#!/bin/bash

echo "🏦 Enhanced Banking Assistant - Starting Up"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if Ollama is running
echo "🤖 Checking Ollama status..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Warning: Ollama doesn't seem to be running on localhost:11434"
    echo "   Please start Ollama with: ollama serve"
    echo "   And ensure you have the llama3 model: ollama pull llama3"
    echo ""
fi

# Start the Flask backend
echo "🚀 Starting Flask backend on http://localhost:5001"
echo "   Press Ctrl+C to stop the server"
echo ""

python app.py 