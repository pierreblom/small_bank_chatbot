#!/bin/bash

# Banking Chatbot Backend Startup Script

echo "🏦 Starting Banking Chatbot Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
echo "📚 Checking dependencies..."
pip install flask flask-cors

# Start the backend
echo "🚀 Starting Flask backend on http://localhost:5001"
echo "Press Ctrl+C to stop the server"
echo ""

python app.py 