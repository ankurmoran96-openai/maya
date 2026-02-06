#!/bin/bash

# Update and install any necessary system dependencies
# (Usually not needed for pure Python, but good for stability)
echo "🚀 Initializing Mayaa System..."

# Install Python requirements
if [ -f requirements.txt ]; then
    echo "📦 Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "⚠️ requirements.txt not found! Installing manual packages..."
    pip install python-telegram-bot requests
fi

# Run the bot
echo "✨ Starting Mayaa v8.0..."
python3 mayaa.py
