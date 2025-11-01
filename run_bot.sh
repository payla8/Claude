#!/bin/bash
# Startup script for Crypto Investment AI Bot

echo "=================================================="
echo "  CRYPTO INVESTMENT AI BOT - Startup Script"
echo "=================================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install/upgrade dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✓ Dependencies installed"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "✓ .env file created. Please edit it with your API keys if using live trading."
fi

# Create necessary directories
mkdir -p logs data/historical data/live

echo ""
echo "=================================================="
echo "  Starting Crypto AI Bot..."
echo "=================================================="
echo ""

# Run the bot
python3 crypto_bot.py

# Deactivate virtual environment on exit
deactivate
