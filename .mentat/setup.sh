#!/bin/bash

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check if Aptos CLI is installed
if ! command -v aptos &> /dev/null; then
    echo "Aptos CLI not found. Please install it following instructions at:"
    echo "https://aptos.dev/en/build/cli"
    echo "This is needed if you want to deploy Move contracts."
fi

echo "Setup complete! Your development environment is ready."
