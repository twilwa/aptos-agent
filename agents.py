import os
import json
import asyncio
import requests
from dotenv import load_dotenv
from requests_oauthlib import OAuth1
from aptos_sdk.account import Account
from aptos_sdk_wrapper import (
    get_balance, fund_wallet, transfer, create_token,
    get_transaction, get_account_resources, get_token_balance, execute_view_function
)
from swarm import Agent
from typing import List

# Load environment variables first!
load_dotenv()

# Initialize the event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Initialize test wallet
wallet = Account.load_key(
    "0x63ae44a3e39c934a7ae8064711b8bac0699ece6864f4d4d5292b050ab77b4f6b")
address = str(wallet.address())

# Load user wallet address from environment
user_wallet = os.getenv('DEVNET_WALLET_ADDRESS')
print(f"Loaded user wallet address: {user_wallet}")  # Debugging output

def get_balance_in_apt_sync(address=None):
    """Get balance for an address or default to user's or agent's address."""
    try:
        target_address = address if address else user_wallet or str(wallet.address())
        return loop.run_until_complete(get_balance(target_address))
    except Exception as e:
        return f"Error getting balance: {str(e)}"

def fund_wallet_in_apt_sync(amount: int, target_address=None):
    """Fund a wallet with APT, defaults to user's or agent's wallet."""
    try:
        if amount is None:
            return "Error: Please specify an amount of APT to fund (maximum 1000 APT)"
        wallet_to_fund = target_address if target_address else user_wallet or str(wallet.address())
        return loop.run_until_complete(fund_wallet(wallet_to_fund, amount))
    except Exception as e:
        return f"Error funding wallet: {str(e)}"
    
def transfer_in_octa_sync(receiver, amount: int, sender=None):
    """Transfer APT, defaults to sending from agent's wallet."""
    try:
        sender_account = sender if sender else wallet
        return loop.run_until_complete(transfer(sender_account, receiver, amount))
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

def get_account_resources_sync(address=None):
    """Get resources for an address or default to agent's address."""
    try:
        target_address = address if address else str(wallet.address())
        return loop.run_until_complete(get_account_resources(target_address))
    except Exception as e:
        return f"Error getting account resources: {str(e)}"

def get_token_balance_sync(address: str, creator_address: str, collection_name: str, token_name: str):
    """Synchronous wrapper for getting token balance."""
    try:
        return loop.run_until_complete(
            get_token_balance(address, creator_address, collection_name, token_name))
    except Exception as e:
        return f"Error getting token balance: {str(e)}"

def execute_view_function_sync(
    function_id: str,
    type_args: List[str],  # Specify that this is an array of strings
    args: List[str]        # Specify that this is an array of strings
) -> dict:
    """Synchronous wrapper for executing a Move view function.
    
    Args:
        function_id: The full function ID (e.g. '0x1::coin::balance')
        type_args: List of type arguments for generic functions
        args: List of arguments to pass to the function
    
    Returns:
        dict: The result of the view function execution
    """
    try:
        return loop.run_until_complete(execute_view_function(function_id, type_args, args))
    except Exception as e:
        return f"Error in synchronous view function call: {str(e)}"

def close_event_loop():
    loop.close()

# Initialize the agent with OpenAI integration
aptos_agent = Agent(
    name="Aptos Agent",
    model="gpt-4",
    api_key=os.getenv('OPENAI_API_KEY'),
    instructions=(
        "You are a helpful agent that can interact on-chain on the Aptos Layer 1 blockchain using the Aptos Python SDK. "
        "You can create custom Move modules or teach the user how, and can transfer your assets to the user, you probably have their address, check your variables for user_wallet. "
        "When funding wallets, you must specify an amount in APT (maximum 1000 APT). For example: fund_wallet_in_apt_sync(100). "
        "After funding a wallet or doing a transaction always report back as much as you can, and be sure to provide a transaction hash beginning with 0x... "
        "Currently you can't perform token swaps. If you ever need to know your address, it is "
        f"{str(wallet.address())}. "
        "If the user asks for their wallet address, check if 'user_wallet' is set. If it is, provide it by saying: "
        f"'Your wallet address is {user_wallet}'. "
        "If 'user_wallet' is not set, inform the user that you don't have access to their wallet address and suggest they provide it. "
        "When looking up transaction details, you can consult the previous message you sent, perhaps reporting on a status, and ensure you use the correct transaction hash. "
        "If you mistakenly use a wallet address instead of a transaction hash, apologize and try scanning the conversation for the appropriate transaction hash and see what you used instead. "
        "If you can't find the transaction hash the user wants, apologize and ask for it. "
        "If something is wrong with funding your or their account, the user can request them from the Aptos Devnet Faucet or use the Aptos CLI. "
        "You, as an AI Agent, have the ability to execute view functions on chain if you know what the shape of the function is. "
        "You can also deploy your own Move-based tokens, NFTs, and interact with them although you don't have those functions. After it fails, give the error message and suggest they keep building or let us know they love this tutorial"
        "If someone asks you to do something you can't do, you can say so and encourage them to implement it themselves using the Aptos SDK. "
        "Recommend they visit aptos.dev for more information. You share links just as a url which may be clickable depending on the users terminal. "
        "After deploying a token, you can provide them a clickable link to a url like this but with the (transaction hash) placed in there "
        "'https://explorer.aptoslabs.com/txn/(transaction_hash)/payload?network=devnet', where they can see it on the explorer for themselves "
        "and then you can also offer to look up the hash to confirm if they want to stay with you. "
        "You can also offer to help them implement it by writing the function and instructing them to add it to the agents.py file."
        "Your normal responses are not formatted in markdown or anything"
    ),
    functions=[
        fund_wallet_in_apt_sync, get_balance_in_apt_sync,
        transfer_in_octa_sync, create_token_sync, get_transaction_sync, get_account_resources_sync, get_token_balance_sync,
        execute_view_function_sync
    ],
)