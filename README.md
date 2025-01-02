# Setting Up Your First Aptos Agent

The Aptos blockchain allows developers to interact with Move modules (smart contracts) through various SDKs. This tutorial will help you set up an AI-powered Aptos Agent that can interact with the blockchain, similar to how you might use ethers.js or web3.js with Ethereum.

Think of an AI blockchain agent like a new employee at a bank. They need two things to do their job:
1. Knowledge of banking procedures (that's our AI's instructions)
2. Access to the actual banking systems (that's our blockchain integration)

You'll learn how to:
1. Set up a Python development environment for blockchain interaction
2. Create a virtual environment for isolated dependencies
3. Create a basic Aptos Agent that can:
   - Check wallet balances
   - Fund wallets with test tokens
   - Transfer assets
   - Create custom tokens

> [!NOTE]
> This tutorial is inspired by [Brian Wong's](https://x.com/briannwongg/status/1867716033659965672) Aptos Agent Template ([on Replit](https://replit.com/@brianwww/Aptos-Agent)). We've expanded it with additional explanations and features.

## Setup

Before we can create our AI blockchain agent, we need to set up our Python development environment. If you're coming from Node.js/JavaScript, you'll find many parallels in how we structure our project.

### Prerequisites
1. Basic understanding of terminal/command line usage
2. OpenAI API key (from platform.openai.com)
3. Familiarity with Python (basic knowledge is sufficient)

### Project Creation Steps

1. Create your project directory:
```bash
mkdir aptos-agent
cd aptos-agent
```

2. Initialize git to track your changes:
```bash
git init
```

3. Create a `.gitignore` file:
```bash
touch .gitignore
```

4. Add Python-specific files to ignore:
```bash
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo ".env" >> .gitignore
echo ".python-version" >> .gitignore
```

> [!NOTE]
> Let's break down what each ignored file does:
> - `venv/`: Like `node_modules/`, contains project-specific dependencies
> - `__pycache__/`: Python's compiled bytecode files (like JavaScript's `.js.map` files)
> - `.env`: Same as Node.js - your environment variables
> - `.python-version`: Like `.nvmrc`, tells pyenv which Python version to use

### Python Environment Setup

1. First, check if you have Python installed:
```bash
python3 --version
```

2. Install `pyenv` using Homebrew (macOS):
```bash
brew install pyenv
```

For Windows users, visit [pyenv-win](https://github.com/pyenv-win/pyenv-win) for installation instructions.

3. Configure pyenv (macOS/Linux users):
```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
```

4. Load your new configuration:
```bash
source ~/.zshrc
```

5. Install required system packages (macOS):
```bash
brew install xz
```

6. Install Python 3.11:
```bash
pyenv install 3.11
```

7. Set Python 3.11 as your project's Python version:
```bash
pyenv local 3.11
```

### Virtual Environment Setup

Virtual environments in Python are similar to having different `package.json` files for different Node.js projects. They help isolate dependencies.

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate  # On macOS/Linux
# or
.\venv\Scripts\activate  # On Windows
```

Your prompt should now show `(venv)` at the beginning.

3. Upgrade pip (Python's package manager):
```bash
python -m pip install --upgrade pip
```

4. Install required packages:
```bash
pip install python-dotenv==1.0.1 requests==2.32.3 requests-oauthlib==2.0.0 aptos-sdk==0.10.0 aiohttp==3.11.11 websockets==14.1
```

5. Save your dependencies:
```bash
pip freeze > requirements.txt
```

## Creating the Aptos SDK Wrapper

Now that our environment is set up, let's create the code that will interact with the Aptos blockchain. We'll start with the SDK wrapper that handles basic blockchain operations.

1. Create the SDK wrapper file:
```bash
touch aptos_sdk_wrapper.py
```

2. Add the following code to `aptos_sdk_wrapper.py`:
```python
import os
from aptos_sdk.account import Account
from aptos_sdk.account_address import AccountAddress
from aptos_sdk.aptos_token_client import AptosTokenClient
from aptos_sdk.async_client import FaucetClient, RestClient
from aptos_sdk.transactions import EntryFunction, TransactionArgument, TransactionPayload
from aptos_sdk.bcs import Serializer

# Initialize additional clients
rest_client = RestClient("https://api.testnet.aptoslabs.com/v1")
faucet_client = FaucetClient("https://faucet.testnet.aptoslabs.com", rest_client)
token_client = AptosTokenClient(rest_client)

async def fund_wallet(wallet_address, amount):
    """Funds a wallet with test tokens from the faucet."""
    print(f"Funding wallet: {wallet_address} with {amount} APT")
    amount = int(amount)
    if amount > 1000:
        raise ValueError("Amount too large. Please specify an amount less than 1000 APT")
    octas = amount * 10**8  # Convert APT to octas (smallest unit)
    if isinstance(wallet_address, str):
        wallet_address = AccountAddress.from_str(wallet_address)
    txn_hash = await faucet_client.fund_account(wallet_address, octas, True)
    print(f"Transaction hash: {txn_hash}")
    return wallet_address

async def get_balance(wallet_address):
    """Gets the balance of a wallet in APT."""
    print(f"Getting balance for wallet: {wallet_address}")
    if isinstance(wallet_address, str):
        wallet_address = AccountAddress.from_str(wallet_address)
    balance = await rest_client.account_balance(wallet_address)
    balance_in_apt = balance / 10**8
    print(f"Balance: {balance_in_apt:.2f} APT")
    return balance_in_apt

async def transfer(sender: Account, receiver, amount):
    """Transfers APT from sender to receiver."""
    if isinstance(receiver, str):
        receiver = AccountAddress.from_str(receiver)
    txn_hash = await rest_client.bcs_transfer(sender, receiver, amount)
    print(f"Transfer complete. Hash: {txn_hash}")
    return txn_hash
```

> [!NOTE]
> This wrapper provides three main functions:
> - `fund_wallet`: Gets test tokens from the faucet
> - `get_balance`: Checks wallet balance
> - `transfer`: Sends tokens between accounts
>
> We're using testnet endpoints, but you could modify these for mainnet later.

## Creating the Agent

Now let's create the AI agent that will use our SDK wrapper. This combines OpenAI's language models with our blockchain functionality.

1. Create the agents file:
```bash
touch agents.py
```

2. Create your `.env` file:
```bash
touch .env
```

3. Add your OpenAI API key to `.env`:
```bash
echo "OPENAI_API_KEY=your-key-here" >> .env
```

4. Add the following code to `agents.py`:
```python
import os
import json
import asyncio
from dotenv import load_dotenv
from aptos_sdk.account import Account
from aptos_sdk_wrapper import get_balance, fund_wallet, transfer

# Load environment variables
load_dotenv()

# Initialize event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Initialize test wallet (you would manage this differently in production)
wallet = Account.generate()
address = str(wallet.address())

def get_balance_sync():
    """Synchronous wrapper for getting balance."""
    try:
        return loop.run_until_complete(get_balance(address))
    except Exception as e:
        return f"Error getting balance: {str(e)}"

def fund_wallet_sync(amount: int):
    """Synchronous wrapper for funding wallet."""
    try:
        return loop.run_until_complete(fund_wallet(address, amount))
    except Exception as e:
        return f"Error funding wallet: {str(e)}"

def transfer_sync(receiver, amount: int):
    """Synchronous wrapper for transfers."""
    try:
        return loop.run_until_complete(transfer(wallet, receiver, amount))
    except Exception as e:
        return f"Error transferring funds: {str(e)}"

# Initialize the agent using the Agent class from swarm
aptos_agent = Agent(
    name="Aptos Agent",
    model="gpt-4o",
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
        fund_wallet_in_apt_sync,
        get_balance_in_apt_sync,
        transfer_in_octa_sync,
        create_token_sync,
        post_tweet  # Additional social media functionality
    ],
)
```

## Creating the Entry Point

Finally, let's create the main program that ties everything together.

1. Create `main.py`:
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
        # Run the interactive demo loop with streaming enabled
        asyncio.run(run_demo_loop(aptos_agent, stream=True))
    finally:
        # Ensure proper cleanup of event loop
        close_event_loop()
```

## Additional Features

### Token Creation
The agent can create custom tokens on Aptos. Add this code to your `aptos_sdk_wrapper.py`:

```python
async def create_token(sender: Account, name: str, symbol: str, icon_uri: str, project_uri: str):
    """Creates a token with specified attributes."""
    print(f"Creating FA with name: {name}, symbol: {symbol}, icon_uri: {icon_uri}, project_uri: {project_uri}")
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

### Social Media Integration
The agent can post updates to Twitter. Add this to your `agents.py`:

```python
def post_tweet(tweet_text: str):
    """Posts a tweet using Twitter API v2."""
    url = "https://api.twitter.com/2/tweets"
    
    auth = OAuth1(
        os.environ.get("TWITTER_API_KEY"),
        os.environ.get("TWITTER_API_SECRET"),
        os.environ.get("TWITTER_ACCESS_TOKEN"),
        os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
    )
    payload = {"text": tweet_text}
    
    try:
        response = requests.post(url, auth=auth, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Error posting tweet: {str(e)}"
```

> [!NOTE]
> To use Twitter integration, you'll need to add your Twitter API credentials to your `.env` file:
> ```bash
> TWITTER_API_KEY=your_api_key
> TWITTER_API_SECRET=your_api_secret
> TWITTER_ACCESS_TOKEN=your_access_token
> TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
> ```

## Testing Your Agent

1. Make sure your virtual environment is activated:
```bash
source venv/bin/activate  # On macOS/Linux
# or
.\venv\Scripts\activate  # On Windows
```

2. Run the main program:
```bash
python main.py
```

You should see output showing your agent's wallet address and current balance.

3. Try funding your wallet:
```python
aptos_agent['functions']['fund_wallet'](1)  # Fund with 1 APT
```

## Next Steps

Congratulations! You've successfully:
1. Set up a Python development environment for blockchain
2. Created a wrapper for the Aptos SDK
3. Implemented basic blockchain operations
4. Created an Aptos Agent that can interact with the blockchain

Here are some suggested next steps:
1. Add more complex blockchain interactions like deploying Move modules
2. Implement error handling and retry logic
3. Add state management for the agent
4. Explore the [Aptos documentation](https://aptos.dev) for more features

Remember to deactivate your virtual environment when you're done:
```bash
deactivate
```

> [!IMPORTANT]
> Never share your private keys or API keys. The test wallet we created is for development only. In production, you would need proper key management and security measures.