#!/bin/bash

# Exit on error but keep track of the overall status
set -e

echo "Installing Python dependencies..."

# Create a temporary requirements file without the agents package
grep -v "agents @" requirements.txt > /tmp/requirements_without_agents.txt || true

# Install everything except agents
echo "Installing main dependencies..."
pip install -r /tmp/requirements_without_agents.txt

# Try to install agents separately with better error handling
echo "Attempting to install OpenAI agents package..."
if ! pip install "agents @ git+https://github.com/openai/agents.git@9db581cecaacea0d46a933d6453c312b034dbf47"; then
    echo "⚠️  Warning: Could not install OpenAI agents package automatically."
    echo "    You may need to install it manually:"
    echo "    pip install \"agents @ git+https://github.com/openai/agents.git@9db581cecaacea0d46a933d6453c312b034dbf47\""
    echo "    or check if there's a newer version available."
fi

# Check if Aptos CLI is installed
if ! command -v aptos &> /dev/null; then
    echo "⚠️  Aptos CLI not found. Please install it following instructions at:"
    echo "    https://aptos.dev/en/build/cli"
    echo "    This is needed if you want to deploy Move contracts."
fi

echo "Setup complete! Your development environment is ready."
