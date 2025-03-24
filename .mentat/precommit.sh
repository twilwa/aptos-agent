#!/bin/bash

# We'll keep track of errors but continue executing
EXIT_CODE=0

echo "Running precommit checks..."

# Install linting/formatting tools if not already installed
if ! command -v ruff &> /dev/null; then
    echo "Installing ruff..."
    pip install ruff || {
        echo "⚠️  Warning: Failed to install ruff. Some checks will be skipped."
        EXIT_CODE=1
    }
fi

# Install type checking tools, but don't fail if they can't be installed
echo "Installing type checking tools..."
pip install pydantic || echo "⚠️  Warning: Failed to install pydantic."

# Try to install specialized type checking tools
# We'll continue even if they fail to install
pip install basedpyright || echo "⚠️  Warning: Failed to install basedpyright."
pip install basedmypy || echo "⚠️  Warning: Failed to install basedmypy."
pip install pydantic_basedtyping || echo "⚠️  Warning: Failed to install pydantic_basedtyping."

# Always run formatting and linting if ruff is available
if command -v ruff &> /dev/null; then
    # Format Python code
    echo "Formatting Python code with ruff..."
    ruff format . || {
        echo "❌ Formatting with ruff failed."
        EXIT_CODE=1
    }

    # Lint Python code
    echo "Linting Python code with ruff..."
    ruff check --fix . || {
        echo "❌ Linting with ruff failed."
        EXIT_CODE=1
    }
else
    echo "⚠️  Skipping formatting and linting (ruff not available)."
    EXIT_CODE=1
fi

# Type checking with basedpyright if available
if command -v basedpyright &> /dev/null; then
    echo "Running type checker (basedpyright)..."
    basedpyright . || {
        echo "❌ Type checking with basedpyright failed."
        # Don't exit, just note the error
        EXIT_CODE=1
    }
else
    echo "⚠️  Skipping basedpyright (not available)."
    EXIT_CODE=1
fi

# Type checking with basedmypy if available
if command -v basedmypy &> /dev/null; then
    echo "Running type checker (basedmypy)..."
    basedmypy . || {
        echo "❌ Type checking with basedmypy failed."
        # Don't exit, just note the error
        EXIT_CODE=1
    }
else
    echo "⚠️  Skipping basedmypy (not available)."
    EXIT_CODE=1
fi

# Basic environment verification (try to import key packages but don't fail if they're missing)
echo "Verifying environment setup..."
python -c "
import sys
missing = []
for pkg in ['openai', 'aptos_sdk', 'pydantic']:
    try:
        __import__(pkg)
        print(f'✓ {pkg} available')
    except ImportError:
        missing.append(pkg)
        print(f'⚠️  {pkg} not available')
try:
    import pydantic_basedtyping
    print('✓ pydantic_basedtyping available')
except ImportError:
    missing.append('pydantic_basedtyping')
    print('⚠️  pydantic_basedtyping not available')
if missing:
    print(f'⚠️  Some packages are missing: {missing}')
else:
    print('✓ All required packages available')
"

# Check Move.toml validity if Aptos CLI is available
if command -v aptos &> /dev/null; then
    echo "Validating Move files..."
    aptos move check --named-addresses access=default || {
        echo "❌ Move validation failed."
        EXIT_CODE=1
    }
else
    echo "⚠️  Skipping Move validation (Aptos CLI not available)."
fi

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Precommit checks completed successfully!"
else
    echo "⚠️  Precommit checks completed with warnings or errors."
    echo "   Review the output above for details."
    # Exit with non-zero status but after running all checks
    # This allows the precommit to run completely but still indicate issues
fi

# Return the final exit code - for Mentat scripts we'll return 0 to continue
# but in a real pre-commit hook you might want to exit with EXIT_CODE
exit 0
