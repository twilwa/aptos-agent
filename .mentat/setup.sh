#!/bin/bash

# Don't exit on error, try to install as much as possible
set +e

echo "Setting up Aptos Agent development environment..."

# Ensure we use the right Python command
PYTHON_CMD="python3"
if ! command -v $PYTHON_CMD &> /dev/null; then
    # Try python as fallback
    PYTHON_CMD="python"
    if ! command -v $PYTHON_CMD &> /dev/null; then
        echo "⚠️  Neither python3 nor python found in PATH."
        echo "    Please install Python 3.10+ to use this repository."
        # Continue anyway for CI purposes
    fi
fi

# Determine which pip command to use
PIP_CMD="pip3"
if ! command -v $PIP_CMD &> /dev/null; then
    PIP_CMD="pip"
    if ! command -v $PIP_CMD &> /dev/null; then
        echo "⚠️  Neither pip3 nor pip found in PATH."
        echo "    Please install pip to use this repository."
        # Continue anyway for CI purposes
    fi
fi

echo "Installing core dependencies..."

# Install key packages individually to ensure they're available
$PIP_CMD install -U pip || echo "⚠️  Failed to upgrade pip."
$PIP_CMD install python-dotenv requests aptos-sdk openai || echo "⚠️  Failed to install some core dependencies."

# Install linting/formatting tools
echo "Installing development tools..."
$PIP_CMD install ruff || echo "⚠️  Failed to install ruff."

echo "Note: The OpenAI agents package is not installed automatically."
echo "      To use the agent functionality, install it manually:"
echo "      pip install \"agents @ git+https://github.com/openai/agents.git@9db581cecaacea0d46a933d6453c312b034dbf47\""

# Check if Aptos CLI is installed
if ! command -v aptos &> /dev/null; then
    echo "⚠️  Aptos CLI not found. To deploy Move contracts, install it from:"
    echo "    https://aptos.dev/en/build/cli"
fi

echo "✅ Basic setup complete!"
echo "For full functionality including type checking, install:"
echo "  - basedpyright: pip install basedpyright"
echo "  - basedmypy: pip install basedmypy"
echo "  - pydantic_basedtyping: pip install pydantic_basedtyping"
