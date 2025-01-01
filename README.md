# Setting Up Your First Aptos Agent - Part 2: Building Your AI Blockchain Assistant

Think of an AI blockchain agent like a new employee at a bank. They need two things to do their job: knowledge of banking procedures (that's our AI's instructions) and access to the actual banking systems (that's our blockchain integration). In Part 1, we set up our development environment. Now, we'll create an AI assistant that can actually interact with the Aptos blockchain - giving it both the knowledge and the tools it needs to help users.

This tutorial continues from [Part 1](https://github.com/tippi-fifestarr/aptos-agent-local/tree/setup), where we set up our Python environment. You'll learn how to:
1. Connect your agent to OpenAI's GPT models for intelligent responses
2. Set up Aptos blockchain interactions
3. Create a working chat interface that can execute blockchain commands

## Prerequisites
- Completed [Part 1 setup](https://github.com/tippi-fifestarr/aptos-agent-local/tree/setup)
- OpenAI API key (from platform.openai.com)
- In your activated virtual environment (`source venv/bin/activate`)
- Python 3.11 configured (check with `python --version`)

## 1. Environment Configuration

1. First, ensure you're in your project directory with the virtual environment activated:
```bash
cd aptos-agent
source venv/bin/activate
```
You should see `(aptos-agent)` in your prompt.

2. Create your `.env` file:
```bash
touch .env
```

3. Add your OpenAI API key:
```bash
echo "OPENAI_API_KEY=your-key-here" >> .env
```

💡 **Security Note**: Replace `your-key-here` with your actual OpenAI API key. Never commit this file to git!

## 2. Setting Up the Aptos SDK Wrapper

4. Create `aptos_sdk_wrapper.py`:
```bash
touch aptos_sdk_wrapper.py
```

5. Add the complete Aptos SDK integration code:
```python
import os
from aptos_sdk.account import Account, AccountAddress
from aptos_sdk.async_client import FaucetClient, RestClient
from aptos_sdk.transactions import EntryFunction, TransactionArgument, TransactionPayload
from aptos_sdk.bcs import Serializer

# Initialize clients
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

💡 **What's Happening Here**: This file acts like a translation layer between our AI agent and the Aptos blockchain. Each function handles a specific blockchain operation:
- `fund_wallet`: Gets test tokens from the faucet
- `get_balance`: Checks wallet balance
- `transfer`: Sends tokens between accounts
- `create_token`: Creates new tokens on Aptos

## 3. Creating the Agent

6. Create `agents.py`:
```bash
touch agents.py
```

7. Add the complete agent configuration:
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
        fund_wallet_in_apt_sync, get_balance_in_apt_sync,
        transfer_in_octa_sync, create_token_sync
    ],
)
```

💡 **What's Happening Here**: This file:
1. Sets up our AI agent with OpenAI
2. Gives it instructions about Aptos
3. Connects it to blockchain functions
4. Handles asynchronous operations

## 4. Creating the Main Entry Point

8. Create `main.py`:
```bash
touch main.py
```

9. Add the main program code:
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

💡 **What's Happening Here**: This creates an interactive chat interface where users can talk to your AI agent.

## 5. Testing Your Agent

10. Start your agent:
```bash
python main.py
```

You should see:
```
Starting Swarm CLI 🐝
User: 
```

11. Try these test commands:
```
What can you help me with?
Check my wallet balance
What is Aptos?
```

💡 **Control Tips**:
- To exit the chat: Press `Ctrl+Z` (Mac/Linux) or `Ctrl+C` (Windows)
- The agent will keep running until you explicitly exit
- Don't worry if you need to press the key combination a couple times

💡 **Successful Setup Signs**:
- You see the Swarm CLI start message
- The agent responds intelligently about Aptos
- You can check wallet balance
- No OpenAI API key errors

⚠️ **Common Issues**:
- If you see OpenAI API errors, check your `.env` file
- If you see Python version errors, verify you're using 3.11+
- The AIP-80 compliance warning is normal for test environments

## What's Next?

Congratulations! You now have a working AI agent that can:
- Understand and respond to blockchain questions
- Execute Aptos transactions
- Help users interact with the blockchain

In Part 3, we'll:
- Add more blockchain capabilities
- Implement social media features
- Create custom commands

Remember to deactivate your virtual environment when you're done:
```bash
deactivate
```