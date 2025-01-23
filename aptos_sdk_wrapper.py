print("Aptos SDK wrapper loaded in test mode")
import os
from aptos_sdk.account import Account, AccountAddress
from aptos_sdk.async_client import FaucetClient, RestClient
from aptos_sdk.transactions import EntryFunction, TransactionArgument, TransactionPayload
from aptos_sdk.bcs import Serializer

# Initialize clients for devnet (changed from testnet)
NODE_URL = "https://api.devnet.aptoslabs.com/v1"
rest_client = RestClient(NODE_URL)
faucet_client = FaucetClient("https://faucet.devnet.aptoslabs.com", rest_client)

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

async def get_transaction(txn_hash: str):
    """Gets details about a specific transaction."""
    try:
        result = await rest_client.transaction_by_hash(txn_hash)
        return result
    except Exception as e:
        print(f"Full error: {str(e)}")
        return f"Error getting transaction: {str(e)}"

async def get_account_resources(address: str):
    """Gets all resources associated with an account."""
    try:
        if isinstance(address, str):
            address = AccountAddress.from_str(address)
        return await rest_client.get_account_resources(address)
    except Exception as e:
        return f"Error getting account resources: {str(e)}"

async def get_token_balance(address: str, creator_address: str, collection_name: str, token_name: str):
    """Gets the token balance for a specific token."""
    try:
        if isinstance(address, str):
            address = AccountAddress.from_str(address)
        resources = await rest_client.get_account_resources(address)
        for resource in resources:
            if resource['type'] == '0x3::token::TokenStore':
                # Parse token data to find specific token balance
                tokens = resource['data']['tokens']
                token_id = f"{creator_address}::{collection_name}::{token_name}"
                if token_id in tokens:
                    return tokens[token_id]
        return "Token not found"
    except Exception as e:
        return f"Error getting token balance: {str(e)}"

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