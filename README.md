# Building Your AI-Powered Aptos Agent with Python

The Aptos blockchain allows developers to interact with Move modules (smart contracts) through various SDKs. This tutorial, inspired by [Brian Wong's](https://x.com/briannwongg/status/1867716033659965672) Aptos Agent Template ([on Replit](https://replit.com/@brianwww/Aptos-Agent)), will help you create your own AI-powered blockchain assistant.

You'll learn how to:
1. Set up a Python development environment for blockchain development
2. Create a virtual environment for project dependency management
3. Build an AI agent that can interact with the Aptos blockchain using the Aptos Python SDK
4. Test your agent with real blockchain interactions

> [!NOTE]  
> For Node.js Developers: Throughout this tutorial, we'll provide analogies to Node.js/JavaScript concepts to help you understand Python's approach.

Imagine our Aptos Agent as a new employee at a bank. They need two things to do their job: knowledge of banking procedures (that's our AI's instructions) and access to the actual banking systems (that's our blockchain integration). We'll set up both components step by step.

> [!NOTE]  
> This tutorial is written for Mac / Linux, so Windows users will need to modify some commands.
>
> Asking [ChatGPT](chat.openai.com) for the Windows version can be a quick way to get the right command!

## Part 0: Getting Your OpenAI API Key
To create an AI Agent, you will need an API key for the AI. This agent was written to work with ChatGPT 4o, so before we dive into the details of how to run the agent’s code, you will need to create an OpenAI account. 

> [!NOTE]  
> This will require loading at least $5 into your account, but the actual tutorial should cost only a couple pennies to interact with your AI Agent!

**If you already have an OpenAI account:**

1. Go to https://platform.openai.com/api-keys.
2. Login.
3. Copy your API key for later (we will use it in the .env file).
4. Ensure that your account has funds.
5. Skip to **Part 1** below!

**Otherwise, if you do NOT have an OpenAI account:** follow the below instructions to “Get an API Key From Scratch”!

### Get a Funded API Key From Scratch

1. Go to [platform.openai.com](https://platform.openai.com/).
2. Click “Start Building” in the top right corner.

   <img width="281" alt="Step2" src="https://github.com/user-attachments/assets/20b8d877-1c74-4d19-a935-1f348121237b" />
    
3. Name your organization.

<img width="387" alt="Step3" src="https://github.com/user-attachments/assets/5fc083ac-3649-4458-8861-3de4ef4c93d3" />

4. Click “I’ll invite my team later”
   
<img width="387" alt="Step4" src="https://github.com/user-attachments/assets/50ba66d8-7f1c-48c9-8132-04c82752754f" />

5. Name your API key and project (see below for an example):

<img width="387" alt="Step5" src="https://github.com/user-attachments/assets/66d24fde-d4d7-4b85-8f33-014b990ecaca" />

6. Click “Copy” on your newly generated API key.
   
<img width="521" alt="Step6" src="https://github.com/user-attachments/assets/1ce14a6b-f631-4a5d-a775-baeb8bb6b09b" />

7. Paste this into a text file for later (We will eventually move this into the .env file for this project)
8. Click “Continue”

<img width="378" alt="Step8" src="https://github.com/user-attachments/assets/a400213b-a58a-44ca-a9d0-d1f06fdfd53a" />

9. Add at least $5 dollars in credit (this tutorial should only cost pennies!)

<img width="378" alt="Step9" src="https://github.com/user-attachments/assets/612b29db-dff1-41a5-9bb3-a13960e08375" />

10. Click “Purchase Credits”.
    
<img width="370" alt="Step10" src="https://github.com/user-attachments/assets/94c5e5d8-b024-4d44-9533-8f10326e5976" />
    
11. Add a payment method.

<img width="499" alt="Step11" src="https://github.com/user-attachments/assets/8ca807de-f8d5-4d06-8722-ddb7e89adaf2" />

12. Click “Add payment method” in the bottom right corner.

<img width="171" alt="Step12" src="https://github.com/user-attachments/assets/2c753532-468a-4e00-b3bc-26d3411c818a" />

13. Use the payment method to purchase the $5 of credits.

> [!NOTE]  
> You should now have a funded API key that you've stored in a text file (temporarily).
>
> It may take a few minutes for this API key to work after funding.

## Part 1: Getting Ready To Run Your Aptos Agent

Before we write any code, we need to set up our development environment. That means downloading the code, choosing the right version of Python, and installing our dependencies.

1. Open your terminal.

2. Create your project directory:
```bash
git clone https://github.com/tippi-fifestarr/aptos-agent-local.git aptos-agent
cd aptos-agent
```

3. Copy `.env-example` into a new file named `.env` by running:
```bash
cp .env-example .env
```

4. Edit `.env` and add your Open API key in quotes:

It should look something like:
```
OPENAI_API_KEY='sk-proj-ABcdeafefa...'
```

> [!NOTE]
> Remember to save!
   
5. Check if you have Python installed:
```bash
python3 --version
```

> [!NOTE]
> We will need python version 3.10 or higher to work with the AI Agent library `swarm`.
> `pyenv` will help us choose which version of python we are using.

6. Ensure you have `pyenv` installed by running `pyenv --version`.

If you do not have `pyenv` installed, you can download it using Homebrew:
```bash
brew install pyenv
```

> [!NOTE]  
> If you don't have Homebrew installed, visit [brew.sh](https://brew.sh) and follow the installation instructions.

7. Add pyenv configuration to your shell:
```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
```

8. Load your new configuration:
```bash
source ~/.zshrc
```

9. Install Python 3.11 (this will take a minute or so):
```bash
pyenv install 3.11
```

> [!NOTE]  
> Now might be a good time to have a little coffee or something while that downloads.

> [!WARNING]  
> You might see warnings about missing tkinter during installation. This is normal and won't affect our project. The installation will still complete successfully.

10. Set Python 3.11 for your project:
```bash
pyenv local 3.11
```

> [!NOTE]  
> Using `pyenv` to pick a specific version of `python` requires us to use `python` instead of `python3` for commands going forward.

11. Create a virtual environment:
```bash
python -m venv venv
```

A virtual environment keeps your project's dependencies isolated, similar to how each Node.js project has its own `node_modules` folder.

This command does several things:

- Creates a new folder called `venv`
- Sets up a fresh Python installation inside it
- Isolates our project's dependencies from other Python projects

12. Activate the virtual environment:
```bash
source venv/bin/activate
```
Your prompt should now show `(venv)` or `(aptos-agent)` at the beginning.

> [!NOTE] 
> The purpose of activating the virtual environment is to keep your project dependencies isolated. This ensures different projects don't interfere with each other's required packages.
>
> The next time you open a terminal, you'll need to activate your virtual environment again by:
> 1. Navigating to your project directory
> 2. Running `source venv/bin/activate`

13. Upgrade pip (Python's package manager):
```bash
python -m pip install --upgrade pip
```

14. Install Swarm, OpenAI and all our other dependencies by running:

`pip install -r requirements.txt`

> [!NOTE]  
> Let's understand what each package does:
> - `swarm`: OpenAI's framework for creating AI agents that can use tools and make decisions
> - `openai`: Connects to OpenAI's API for the language model
> - `python-dotenv`: Loads environment variables (like your API keys)
> - `requests` & `requests-oauthlib`: Handles HTTP requests and OAuth authentication
> - `aptos-sdk`: Interfaces with the Aptos blockchain

## Part 2: Running Your AI Agent

Now that our environment is set up, we'll create the files that will power our AI agent. Each file has a specific purpose in making our blockchain assistant work.

5. Create an environment file for your API key:
```bash
touch .env
```

6. Open .env in your preferred editor and add:
```
OPENAI_API_KEY=<YOUR-KEY-HERE>
```

7. Replace `<YOUR-KEY-HERE>` with your OpenAI API key.

> [!NOTE]  
> Remember to save the file.

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

2. Try some test commands such as:

- User: What can you do?

- User: Create a token called "Test Token" with symbol "TEST"

- User: Check my wallet balance

- User: Aptos has great docs! Aptos Docs Token plz.

> [!NOTE]  
> Your agent should respond intelligently to each command, explaining what it's doing and providing blockchain transaction details when relevant. You'll want to check everything deployed correctly using the indexer or explorer. You can exit the conversation with your agent by typing `cmd+z` on Mac.

![Screenshot 2025-01-16 at 2 23 03 PM](https://github.com/user-attachments/assets/11318b9b-4afd-4357-a8ab-93d7e60e9a40)

Let's verify our new token:

3. Visit the [Aptos Explorer](https://explorer.aptoslabs.com/?network=testnet).

4. Switch to "Testnet" network if not already selected.

5. Paste your transaction hash and select it from the dropdown that loads.

6. Click the "Payload" tab to see your token details.

![Screenshot 2025-01-16 at 2 29 27 PM](https://github.com/user-attachments/assets/4ff96e5f-b0f0-45b2-aba1-f9866db3fb71)

## What's Next?

Your AI agent can now:
- Understand and respond to blockchain questions
- Execute Aptos transactions
- Help users interact with the blockchain
- Create and verify tokens on testnet

In the next tutorial, we'll improve the agent with:
- A setup wizard for configuration
- Optional social media features
- Better test mode capabilities

Here are some ideas for next steps:
1. Learn more about Move smart contracts with the [Your First Move Module Guide at aptos.dev](https://aptos.dev/en/build/guides/first-move-module), perhaps build a custom Move modules to interact with?
2. Explore the [Aptos SDK documentation](https://aptos.dev/en/build/sdks), perhaps try building an agent in a different language and contribute to this open source project?
3. Join the [Aptos Discord](https://discord.gg/aptoslabs) to connect with other developers.
4. Let us know you enjoyed this content, tag us and post your experience and thoughts on social media!
