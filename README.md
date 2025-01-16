# Building Your AI-Powered Aptos Agent with Python

The Aptos blockchain allows developers to interact with Move modules (smart contracts) through various SDKs. This tutorial, inspired by [Brian Wong's](https://x.com/briannwongg/status/1867716033659965672) Aptos Agent Template ([on Replit](https://replit.com/@brianwww/Aptos-Agent)), will help you create your own AI-powered blockchain assistant.

You'll learn how to:
1. Set up a Python development environment for blockchain development
2. Create a virtual environment for project dependency management
3. Build an AI agent that can interact with the Aptos blockchain
4. Test your agent with real blockchain interactions

> [!NOTE]  
> For Node.js Developers: Throughout this tutorial, we'll provide analogies to Node.js/JavaScript concepts to help you understand Python's approach.

Imagine our Aptos Agent as a new employee at a bank. They need two things to do their job: knowledge of banking procedures (that's our AI's instructions) and access to the actual banking systems (that's our blockchain integration). We'll set up both components step by step.

## Prerequisites

1. Basic understanding of terminal/command line usage
2. Familiarity with Python (helpful but not required)
3. Mac or Linux environment (Windows users will need to modify some commands)
4. OpenAI API key (we'll help you get this)

## Part 1: Setting Up Your Development Environment

Before we write any code, we need to set up our Python environment. Think of this like setting up Node.js and npm for a JavaScript project.

1. Open your terminal

2. Create your project directory:
```bash
mkdir aptos-agent
cd aptos-agent
```

3. Check if you have Python installed:
```bash
python3 --version
```
Any result (or even an error) is fine - we'll set up the right version next.

4. Install `pyenv` using Homebrew:
```bash
brew install pyenv
```

> [!NOTE]  
> If you don't have Homebrew installed, visit [brew.sh](https://brew.sh) and follow the installation instructions.

5. Add pyenv configuration to your shell:
```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
```

6. Load your new configuration:
```bash
source ~/.zshrc
```

7. Install Python 3.11:
```bash
pyenv install 3.11
```

> [!WARNING]  
> You might see warnings about missing tkinter during installation. This is normal and won't affect our project. The installation will still complete successfully.

8. Set Python 3.11 for your project:
```bash
pyenv local 3.11
```

## Part 2: Virtual Environment and Dependencies

A virtual environment keeps your project's dependencies isolated, similar to how each Node.js project has its own `node_modules` folder.

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate
```
Your prompt should now show `(venv)` or `(aptos-agent)` at the beginning.

3. Upgrade pip (Python's package manager):
```bash
python -m pip install --upgrade pip
```

4. Let's get your OpenAI API key set up:
   - Visit [platform.openai.com](https://platform.openai.com)
   - Sign up or log in
   - Navigate to "API Keys"
   - Create a new key (note that API usage has associated costs, but it's under $5)

5. Create an environment file for your API key:
```bash
touch .env
```

6. Open .env in your preferred editor and add:
```
OPENAI_API_KEY=<YOUR-KEY-HERE>
```

7. Replace <YOUR-KEY-HERE> with your OpenAI API key.

> [!NOTE]  
> Remember to save the file.

8. Install Swarm, OpenAI and other dependencies:
```bash
pip install git+https://github.com/openai/swarm.git openai python-dotenv requests requests-oauthlib aptos-sdk
```

> [!NOTE]  
> Let's understand what each package does:
> - `swarm`: OpenAI's framework for creating AI agents that can use tools and make decisions
> - `openai`: Connects to OpenAI's API for the language model
> - `python-dotenv`: Loads environment variables (like your API keys)
> - `requests` & `requests-oauthlib`: Handles HTTP requests and OAuth authentication
> - `aptos-sdk`: Interfaces with the Aptos blockchain

9. Save your dependencies list:
```bash
pip freeze > requirements.txt
```

> [!NOTE]  
> Think of `requirements.txt` like `package.json` + `package-lock.json` combined. It lists your project's dependencies with exact versions.

## Part 3: Building Your AI Agent

Now that our environment is set up, we'll create the files that will power our AI agent. Each file has a specific purpose in making our blockchain assistant work.

1. Create the main entry file:
```bash
touch main.py
```

2. Add this code to `main.py`:
```python
from dotenv import load_dotenv
from swarm.repl import run_demo_loop
from agents import close_event_loop, aptos_agent
import asyncio

if __name__ == "__main__":
    try:
        load_dotenv()
        asyncio.run(run_demo_loop(aptos_agent, stream=True))
    finally:
        close_event_loop()
```
> [!NOTE]  
> Remember to save the file.

> [!NOTE]  
> This code creates the interactive environment where you'll talk to your AI agent. It loads your API key, starts the agent, and handles cleanup when you're done.

3. Create the agents file:
```bash
touch agents.py
```

4. Add the agent configuration to `agents.py`:
```python
import os
import json
import asyncio
import requests
from dotenv import load_dotenv
from requests_oauthlib import OAuth1
from aptos_sdk.account import Account
from aptos_sdk_wrapper import get_balance, fund_wallet, transfer, create_token
from swarm import Agent

# Load environment variables first!
load_dotenv()

# Initialize the event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Initialize test wallet
wallet = Account.load_key(
    "0x63ae44a3e39c934a7ae8064711b8bac0699ece6864f4d4d5292b050ab77b4f6b")
address = str(wallet.address())

def get_balance_in_apt_sync():
    try:
        return loop.run_until_complete(get_balance(address))
    except Exception as e:
        return f"Error getting balance: {str(e)}"

def fund_wallet_in_apt_sync(amount: int):
    try:
        return loop.run_until_complete(fund_wallet(address, amount))
    except Exception as e:
        return f"Error funding wallet: {str(e)}"

def transfer_in_octa_sync(sender, receiver, amount: int):
    try:
        return loop.run_until_complete(transfer(sender, receiver, amount))
    except Exception as e:
        return f"Error transferring funds: {str(e)}"

def create_token_sync(sender, name: str, symbol: str, icon_uri: str,
                      project_uri: str):
    try:
        return loop.run_until_complete(
            create_token(wallet, name, symbol, icon_uri, project_uri))
    except Exception as e:
        return f"Error creating token: {str(e)}"

def close_event_loop():
    loop.close()

# Initialize the agent with OpenAI integration
aptos_agent = Agent(
    name="Aptos Agent",
    model="gpt-4",
    api_key=os.getenv('OPENAI_API_KEY'),
    instructions=(
        "You are a helpful agent that can interact on-chain on the Aptos Layer 1 blockchain using the Aptos SDK. "
        "You can create custom Move modules, transfer assets, "
        "and perform token swaps. If you ever need to know your address, it is {address}. "
        "If you ever need test funds, you can request them from the Aptos Testnet Faucet. "
        "You can also deploy your own Move-based tokens, NFTs, and interact with them. "
        "If someone asks you to do something you can't do, you can say so and encourage them to implement it themselves using the Aptos SDK. "
        "Recommend they visit aptos.dev for more information. "
        "You can also offer to help them implement it by writing the function and instructing them to add it to the agents.py file."
    ),
    functions=[
        fund_wallet_in_apt_sync, get_balance_in_apt_sync,
        transfer_in_octa_sync, create_token_sync
    ],
)
```
> [!NOTE]  
> Remember to save the file.

> [!NOTE]  
> This file defines what your AI agent can do and how it should behave. The functions allow it to interact with the blockchain, while the instructions tell it how to communicate with users.

5. Create the SDK wrapper:
```bash
touch aptos_sdk_wrapper.py
```

6. Add the Aptos integration code to `aptos_sdk_wrapper.py`:
```python
import os
from aptos_sdk.account import Account, AccountAddress
from aptos_sdk.async_client import FaucetClient, RestClient
from aptos_sdk.transactions import EntryFunction, TransactionArgument, TransactionPayload
from aptos_sdk.bcs import Serializer

# Initialize clients for testnet
rest_client = RestClient("https://api.testnet.aptoslabs.com/v1")
faucet_client = FaucetClient("https://faucet.testnet.aptoslabs.com",
                             rest_client)

async def fund_wallet(wallet_address, amount):
    """Funds a wallet with a specified amount of APT."""
    print(f"Funding wallet: {wallet_address} with {amount} APT")
    amount = int(amount)
    if amount > 1000:
        raise ValueError(
            "Amount too large. Please specify an amount less than 1000 APT")
    octas = amount * 10**8  # Convert APT to octas
    if isinstance(wallet_address, str):
        wallet_address = AccountAddress.from_str(wallet_address)
    txn_hash = await faucet_client.fund_account(wallet_address, octas, True)
    print(f"Transaction hash: {txn_hash}\nFunded wallet: {wallet_address}")
    return wallet_address

async def get_balance(wallet_address):
    """Retrieves the balance of a specified wallet."""
    print(f"Getting balance for wallet: {wallet_address}")
    if isinstance(wallet_address, str):
        wallet_address = AccountAddress.from_str(wallet_address)
    balance = await rest_client.account_balance(wallet_address)
    balance_in_apt = balance / 10**8  # Convert octas to APT
    print(f"Wallet balance: {balance_in_apt:.2f} APT")
    return balance

async def transfer(sender: Account, receiver, amount):
    """Transfers a specified amount from sender to receiver."""
    if isinstance(receiver, str):
        receiver = AccountAddress.from_str(receiver)
    txn_hash = await rest_client.bcs_transfer(sender, receiver, amount)
    print(f"Transaction hash: {txn_hash} and receiver: {receiver}")
    return txn_hash

async def create_token(sender: Account, name: str, symbol: str, icon_uri: str,
                       project_uri: str):
    """Creates a token with specified attributes."""
    print(
        f"Creating FA with name: {name}, symbol: {symbol}, icon_uri: {icon_uri}, project_uri: {project_uri}"
    )
    payload = EntryFunction.natural(
        "0xe522476ab48374606d11cc8e7a360e229e37fd84fb533fcde63e091090c62149::launchpad",
        "create_fa_simple",
        [],
        [
            TransactionArgument(name, Serializer.str),
            TransactionArgument(symbol, Serializer.str),
            TransactionArgument(icon_uri, Serializer.str),
            TransactionArgument(project_uri, Serializer.str),
        ])
    signed_transaction = await rest_client.create_bcs_signed_transaction(
        sender, TransactionPayload(payload))
    txn_hash = await rest_client.submit_bcs_transaction(signed_transaction)
    print(f"Transaction hash: {txn_hash}")
    return txn_hash
```
> [!NOTE]  
> Remember to save the file.

> [!NOTE]  
> This wrapper handles all the low-level blockchain interactions. It converts our simple function calls into proper Aptos transactions.

## Part 4: Testing Your Agent

Let's make sure everything is working correctly.

1. Start your agent:
```bash
python main.py
```

You should see:
```
Starting Swarm CLI 🐝
User: 
```

2. Try some test commands:
```
User: What can you do?

User: Create a token called "Test Token" with symbol "TEST"

User: Check my wallet balance
```

> [!NOTE]  
> Your agent should respond intelligently to each command, explaining what it's doing and providing blockchain transaction details when relevant.

## What's Next?

Your AI agent can now:
- Understand and respond to blockchain questions
- Execute Aptos transactions
- Help users interact with the blockchain
- Create and verify tokens on testnet

Here are some ideas for next steps:
1. Learn more about Move smart contracts with the [Your First Move Module Guide at aptos.dev](https://aptos.dev/en/build/guides/first-move-module), perhaps build a custom Move modules to interact with?
2. Explore the [Aptos SDK documentation](https://aptos.dev/en/build/sdks), perhaps try building an agent in a different language and contribute to this open source project?
3. Join the [Aptos Discord](https://discord.gg/aptoslabs) to connect with other developers.
4. Let us know you enjoyed this content, tag us and post your experience and thoughts on social media!

> [!NOTE] 
> Remember to close your terminal or run `deactivate` when you're done working on the project. The next time you want to work on it, you'll need to:
> 1. Open your terminal
> 2. Navigate to your project directory
> 3. Run `source venv/bin/activate`
> 
> The purpose of activating the virtual environment is to keep your project dependencies isolated. This ensures different projects don't interfere with each other's required packages.