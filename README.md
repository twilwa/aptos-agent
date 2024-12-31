# Setting Up Your First Aptos Agent (Python Edition)

The Aptos blockchain allows developers to interact with Move modules (smart contracts) through various SDKs. This tutorial will help you set up a Python-based Aptos Agent that can interact with the blockchain, similar to how you might use ethers.js or web3.js with Ethereum.

This tutorial assumes you're familiar with JavaScript/Node.js and have some blockchain experience. It's inspired by [Brian Wong's](https://x.com/briannwongg/status/1867716033659965672) Aptos Agent Template ([on Replit](https://replit.com/@brianwww/Aptos-Agent)). You'll learn how to:

1. Set up a Python development environment (think Node.js, but for Python)
2. Create a virtual environment (similar to Node.js projects having their own `node_modules`)
3. Create a basic Aptos Agent (getting your file structure set up) that runs in test mode
4. Get ready to interact with the Aptos blockchain (see our next tutorial!)

💡 **For Node.js Developers**: Throughout this tutorial, we'll provide analogies to Node.js/JavaScript concepts to help you understand Python's approach.

## Part 1: Project Creation

1. Create your project directory:```bash
mkdir aptos-agent
cd aptos-agent
```

2. Initialize git:
```bash
git init
```
You should see:
```
Initialized empty Git repository in .../aptos-agent/.git/
```

3. Create a `.gitignore` file:
```bash
touch .gitignore
```

4. Add Python-specific ignores:
```bash
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo ".env" >> .gitignore
echo ".python-version" >> .gitignore
```

💡 **Python Files Explained**:
- `venv/`: Like `node_modules/`, contains project-specific dependencies
- `__pycache__/`: Python's compiled bytecode files (like JavaScript's `.js.map` files)
- `.env`: Same as Node.js - your environment variables
- `.python-version`: Like `.nvmrc`, tells pyenv which Python version to use

## Part 2: Python Setup

5. Check if you have Python (don't worry if you don't!):
```bash
python3 --version
```
Any result (or even an error) is fine - we'll set up the right version next.

6. Install `pyenv` using Homebrew:
```bash
brew install pyenv
```

7. Add pyenv configuration to your shell (one line at a time):
```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
```

8. Load your new configuration:
```bash
source ~/.zshrc
```

9. Install xz (required for Python installation):
```bash
brew install xz
```

10. Install Python 3.11:
```bash
pyenv install 3.11
```
You should see output ending with:
```
Installed Python-3.11.11 to /Users/[username]/.pyenv/versions/3.11.11
```

11. Set Python 3.11 for your project:
```bash
pyenv local 3.11
```

## Part 3: Virtual Environment Setup

12. Create a virtual environment:
```bash
python -m venv venv
```

13. Activate the virtual environment:
```bash
source venv/bin/activate
```
Your prompt should change to show `(aptos-agent)` at the beginning.

💡 **Virtual Environment Tip**: When you're done working on your project, you can exit the virtual environment by typing `deactivate` in your terminal. This returns your terminal to its normal state.


## Part 4: Installing Dependencies

14. Upgrade pip (Python's package manager):
```bash
python -m pip install --upgrade pip
```

15. Install required packages:
```bash
pip install python-dotenv requests requests-oauthlib aptos-sdk
```

16. Save your dependencies:
```bash
pip freeze > requirements.txt
```

## Part 5: Creating Basic Agent Files

17. Create the main entry file:
```bash
touch main.py
```

18. Add test code to `main.py`:
```python
if __name__ == "__main__":
    print("Aptos Agent Test Mode")
    try:
        from agents import aptos_agent
        print(f"Agent name: {aptos_agent['name']}")
        print(f"Test balance: {aptos_agent['get_balance']()}")
    except Exception as e:
        print(f"Setup error: {e}")
```

19. Create the agents file:
```bash
touch agents.py
```

20. Add test code to `agents.py`:
```python
import os
from dotenv import load_dotenv

# Test configuration
def get_balance_in_apt_sync():
    return "1.0 APT (test mode)"

aptos_agent = {
    "name": "Aptos Agent",
    "get_balance": get_balance_in_apt_sync
}
```

21. Create the SDK wrapper:
```bash
touch aptos_sdk_wrapper.py
```

22. Add placeholder to `aptos_sdk_wrapper.py`:
```python
print("Aptos SDK wrapper loaded in test mode")
```

23. Test your setup:
```bash
python main.py
```
You should see:
```
Aptos Agent Test Mode
Agent name: Aptos Agent
Test balance: 1.0 APT (test mode)
```

24. Save your working setup:
```bash
git add .
git commit -m "Initial setup with test mode"
```

Congratulations! You now have a working Python environment and basic agent structure. In Part 2, we'll:
1. Add real Aptos SDK integration
2. Configure environment variables for API keys
3. Add blockchain interaction functions

⚠️ **Remember**: Whenever you open a new terminal to work on this project:
```bash
cd aptos-agent
source venv/bin/activate
```
