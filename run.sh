#!/bin/bash

# Flight Price Aggregator API - Quick Start Script

echo "🚀 Flight Price Aggregator API"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✅ Python version: $(python3 --version)"
echo ""

# Check if venv exists, if not create it
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✨ Setup complete!"
echo ""
echo "🌐 Starting API on http://localhost:8080"
echo "📚 Docs available at http://localhost:8080/docs"
echo "⌨️  Press Ctrl+C to stop"
echo ""

# Run the application
python main.py
