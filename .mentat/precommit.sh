#!/bin/bash

# Exit on error
set -e

echo "Running precommit checks..."

# Install linting/formatting tools if not already installed
if ! command -v ruff &> /dev/null; then
    echo "Installing ruff..."
    pip install ruff
fi

if ! command -v basedpyright &> /dev/null; then
    echo "Installing basedpyright..."
    pip install basedpyright
fi

if ! command -v basedmypy &> /dev/null; then
    echo "Installing basedmypy..."
    pip install basedmypy
fi

if ! python -c "import pydantic_basedtyping" &> /dev/null; then
    echo "Installing pydantic and pydantic_basedtyping..."
    pip install pydantic pydantic_basedtyping
fi

# Format Python code
echo "Formatting Python code with ruff..."
ruff format .

# Lint Python code
echo "Linting Python code with ruff..."
ruff check --fix .

# Type checking with basedpyright
echo "Running type checker (basedpyright)..."
basedpyright .

# Type checking with basedmypy
echo "Running type checker (basedmypy)..."
basedmypy .

# Test setup verification (quick test to ensure environment is working)
echo "Verifying environment setup..."
python -c "import openai; import aptos_sdk; import pydantic; import pydantic_basedtyping; print('Environment verification successful!')"

# Check Move.toml validity if Aptos CLI is available
if command -v aptos &> /dev/null; then
    echo "Validating Move files..."
    aptos move check --named-addresses access=default
fi

echo "Precommit checks completed successfully!"
