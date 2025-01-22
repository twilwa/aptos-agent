import os
import json
import asyncio
import requests
from dotenv import load_dotenv
from requests_oauthlib import OAuth1
from aptos_sdk.account import Account
# from aptos_sdk_wrapper import get_balance, fund_wallet, transfer, create_token
from aptos_sdk_wrapper import (
    get_balance, fund_wallet, transfer, create_token,
    get_transaction, get_account_resources, get_token_balance
)
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

def get_transaction_sync(txn_hash: str):
    """Synchronous wrapper for getting transaction details."""
    try:
        return loop.run_until_complete(get_transaction(txn_hash))
    except Exception as e:
        return f"Error getting transaction: {str(e)}"

def get_account_resources_sync(address: str):
    """Synchronous wrapper for getting account resources."""
    try:
        return loop.run_until_complete(get_account_resources(address))
    except Exception as e:
        return f"Error getting account resources: {str(e)}"

def get_token_balance_sync(address: str, creator_address: str, collection_name: str, token_name: str):
    """Synchronous wrapper for getting token balance."""
    try:
        return loop.run_until_complete(
            get_token_balance(address, creator_address, collection_name, token_name))
    except Exception as e:
        return f"Error getting token balance: {str(e)}"

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
        "After deploying a token, you can provide them a clickable link to a url like this but with the (transaction hash) placed in there 'https://explorer.aptoslabs.com/txn/(transaction hash)/payload?network=testnet', where they can see it on the explorer for themselves and then you can also offer to look up the hash to confirm if they want to stay with you. "
        "You can also offer to help them implement it by writing the function and instructing them to add it to the agents.py file."
    ),
    functions=[
        fund_wallet_in_apt_sync, get_balance_in_apt_sync,
        transfer_in_octa_sync, create_token_sync, get_transaction_sync, get_account_resources_sync, get_token_balance_sync
    ],
)