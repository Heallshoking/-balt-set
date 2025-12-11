#!/bin/bash
# AI Service Marketplace MVP - Quick Start Script

echo "🚀 Starting AI Service Marketplace MVP..."
echo ""

# Check if Python 3.11+ is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python $PYTHON_VERSION found"

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q 2>/dev/null || pip install fastapi uvicorn pydantic pydantic-settings python-dotenv -q

# Copy .env if not exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ Created .env from .env.example"
    fi
fi

# Start the server
echo ""
echo "🌐 Starting API server on http://localhost:8000"
echo "📊 API Docs available at http://localhost:8000/docs"
echo ""
echo "🔧 Available endpoints:"
echo "   - Client form:     http://localhost:8000/../frontend/index.html"
echo "   - Master terminal: http://localhost:8000/../frontend/master/terminal.html"
echo "   - API docs:        http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
