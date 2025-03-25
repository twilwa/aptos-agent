from requests.models import Response
from typing import Any
from aptos_sdk.type_tag import TypeTag

print("Aptos SDK wrapper loaded in test mode")
import requests
import aiohttp
from aptos_sdk.account import Account
from aptos_sdk.account_address import AccountAddress
from aptos_sdk.async_client import FaucetClient, RestClient
from aptos_sdk.transactions import EntryFunction, SignedTransaction, TransactionArgument, TransactionPayload
from aptos_sdk.bcs import Serializer

# Initialize clients for devnet (changed from testnet)
NODE_URL: str = "https://api.devnet.aptoslabs.com/v1"
rest_client: RestClient = RestClient(base_url=NODE_URL)
faucet_client: FaucetClient = FaucetClient(base_url="https://faucet.devnet.aptoslabs.com", rest_client=rest_client)

async def get_account_modules(address: str, limit: int = 10) -> dict[str, Any]:
    """
    Fetch the published modules for a specific account,
    capping the results at 'limit' to avoid large gpt-4o prompts.
    """
    # Add '?limit={limit}' for server-side pagination.
    # Then if the account has more than 'limit' modules, the server might
    # provide an "X-Aptos-Cursor" header for further pages (if needed).
    url: str = f"{NODE_URL}/accounts/{address}/modules?limit={limit}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                modules = await response.json()
                
        if not modules:
            return {"error": "No modules found for this account"}

        # Summarize or truncate large data fields inside each module
        summarized_modules: list[dict[str, Any]] = []
        for m in modules:
            # We might remove or shorten 'bytecode' if it's huge
            if "bytecode" in m and isinstance(m["bytecode"], (str, bytes, list)):
                byte_len: int = len(m["bytecode"])
                
                if byte_len > 300:
                    if isinstance(m["bytecode"], str):
                        m["bytecode"] = m["bytecode"][:300] + f"...(truncated {byte_len-300} chars)"
                    elif isinstance(m["bytecode"], bytes):
                        m["bytecode"] = m["bytecode"][:300] + b"...(truncated)"
                    else:
                        # For lists, truncate to first 300 items
                        m["bytecode"] = m["bytecode"][:300] + ["...(truncated)"]

            # Possibly parse 'abi' and only keep minimal info
            # to prevent huge text from each function signature
            if "abi" in m:
                abi = m["abi"]
                # Example: remove generics if you don't need them
                if "exposed_functions" in abi:
                    for fn in abi["exposed_functions"]:
                        # Remove or shorten params if super large

                        if "params" in fn and isinstance(fn["params"], list) and len(fn["params"]) > 5:
                            fn["params"] = fn["params"][:300] + ["...truncated"]
            
            summarized_modules.append(m)

        # If the server truncated results to 'limit' behind the scenes,
        # you might want to add a note. You can glean if there's more from
        # the "X-Aptos-Cursor" header, but let's keep it simple:
        return {
            "modules": summarized_modules,
            "note": (
                f"Requested up to {limit} modules. "
                "Large fields were truncated to prevent large gpt-4o prompts."
            )
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Error getting account modules: {str(e)}"}

async def execute_view_function(function_id: str, type_args: list[str], args: list[Any]) -> dict[str, Any]:
    """
    Executes a Move view function asynchronously.
    Args:
        function_id: The full function ID (e.g., '0x1::coin::balance').
        type_args: A list of type arguments for the function.
        args: A list of arguments to pass to the function.
    Returns:
        The result of the view function execution.
    """
    url: str = f"{NODE_URL}/view"
    headers: dict[str, str] = {"Content-Type": "application/json"}
    body: dict[str, Any] = {
        "function": function_id,
        "type_arguments": type_args,
        "arguments": args,
    }

    try:
        response: Response = requests.post(url=url, json=body, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Error executing view function: {str(e)}"}

async def fund_wallet(wallet_address: str | AccountAddress, amount: int) -> AccountAddress:
    """Funds a wallet with a specified amount of APT."""
    print(f"Funding wallet: {wallet_address} with {amount} APT")
    amount = int(amount)
    if amount > 1000:
        raise ValueError(
            "Amount too large. Please specify an amount less than 1000 APT")
    octas: int = amount * 10**8  # Convert APT to octas
    account_address: AccountAddress
    if isinstance(wallet_address, str):
        account_address = AccountAddress.from_str(address=wallet_address)
    else:
        account_address = wallet_address
    txn_hash: Any = await faucet_client.fund_account(address=account_address, amount=octas)
    print(f"Transaction hash: {txn_hash}\nFunded wallet: {wallet_address}")
    return account_address

async def get_balance(wallet_address: str | AccountAddress) -> int:
    """Retrieves the balance of a specified wallet."""
    print(f"Getting balance for wallet: {wallet_address}")
    address_obj: AccountAddress
    if isinstance(wallet_address, str):
        address_obj = AccountAddress.from_str(address=wallet_address)
    else:
        address_obj = wallet_address
    balance: int = await rest_client.account_balance(account_address=address_obj)
    balance_in_apt: float = balance / 10**8  # Convert octas to APT
    print(f"Wallet balance: {balance_in_apt:.2f} APT")
    return balance

async def transfer(sender: Account, receiver: str | AccountAddress, amount: int) -> str:
    """Transfers a specified amount from sender to receiver."""
    target_address: AccountAddress
    if isinstance(receiver, str):
        target_address = AccountAddress.from_str(address=receiver)
    else:
        target_address = receiver
    txn_hash: Any = await rest_client.bcs_transfer(sender=sender, recipient=target_address, amount=amount)
    print(f"Transaction hash: {txn_hash} and receiver: {receiver}")
    return txn_hash

async def get_transaction(txn_hash: str) -> dict[str, Any]:
    """Gets details about a specific transaction."""
    try:
        result: dict[str, Any] = await rest_client.transaction_by_hash(txn_hash=txn_hash)
        return result
    except Exception as e:
        print(f"Full error: {str(e)}")
        return {"error": f"Error getting transaction: {str(e)}"}

async def get_account_resources(address: str) -> list[dict[str, Any]]:
    """Gets all resources associated with an account using direct API call."""
    node_url = "https://api.devnet.aptoslabs.com/v1"  # Update for the correct network
    try:
        # Use direct API call to fetch resources
        url: str = f"{node_url}/accounts/{address}/resources"
        response: Response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        resources = response.json()
        if not resources:
            return [{"error": "No resources found for this account"}]
        return resources
    except requests.exceptions.RequestException as e:
        return [{"error": f"Error getting account resources: {str(e)}"}]

async def get_token_balance(address: str | AccountAddress, creator_address: str, collection_name: str, token_name: str) -> dict[str, Any]:
    """Gets the token balance for a specific token."""
    try:
        address_obj: AccountAddress
        if isinstance(address, str):
            address_obj = AccountAddress.from_str(address)
        else:
            address_obj = address
        
        # Use account_resources instead of get_account_resources
        resources: list[dict[str, Any]] = await rest_client.account_resources(address_obj)
        for resource in resources:
            if resource['type'] == '0x3::token::TokenStore':
                # Parse token data to find specific token balance
                tokens: Any = resource['data']['tokens']
                token_id: str = f"{creator_address}::{collection_name}::{token_name}"
                if token_id in tokens:
                    return tokens[token_id]
        return {"status": "Token not found"}
    except Exception as e:
        return {"error": f"Error getting token balance: {str(e)}"}

# TODO: Find out from Brian if there's a deployed version of this contract on Devnet, or if we need to compile and deploy this as well in the tutorial...
async def create_token(sender: Account, name: str, symbol: str, icon_uri: str,
                       project_uri: str) -> str:
    """Creates a token with specified attributes."""
    print(
        f"Creating FA with name: {name}, symbol: {symbol}, icon_uri: {icon_uri}, project_uri: {project_uri}"
    )
    payload: EntryFunction = EntryFunction.natural(
        module="0xe522476ab48374606d11cc8e7a360e229e37fd84fb533fcde63e091090c62149::launchpad",
        function="create_fa_simple",
        ty_args=[],
        args=[
            TransactionArgument(value=name, encoder=Serializer.str),
            TransactionArgument(value=symbol, encoder=Serializer.str),
            TransactionArgument(value=icon_uri, encoder=Serializer.str),
            TransactionArgument(value=project_uri, encoder=Serializer.str),
        ])
    signed_transaction: SignedTransaction = await rest_client.create_bcs_signed_transaction(
        sender, payload=TransactionPayload(payload))
    txn_hash: str = await rest_client.submit_bcs_transaction(signed_transaction)
    print(f"Transaction hash: {txn_hash}")
    return txn_hash

async def execute_entry_function(
    sender: Account, 
    function_id: str, 
    type_args: list[str], 
    args: list[Any], 
    abi_cache: list[dict[str, Any]] | None = None, 
    optional_fetch_abi: bool = False
) -> dict[str, str]:
    """
    Dynamically executes a Move entry function by analyzing its ABI.

    Args:
        sender: The account executing the function.
        function_id: The full function ID (e.g., '0x1::coin::transfer').
        type_args: A list of type arguments for the function (if any).
        args: A list of arguments to pass to the function (excluding `&signer`).
        abi_cache: (Optional) A cached ABI from a previous `get_account_modules` call.
        optional_fetch_abi: (Bool) If True, fetches the ABI if not already cached.

    Returns:
        The transaction hash of the submitted entry function.
    """

    try:
        # Extract the module address and module name
        module_path, function_name = function_id.rsplit(sep="::", maxsplit=1)
        module_address, module_name = module_path.split(sep="::", maxsplit=1)

        if not type_args:
            type_args = []
        
        # ✅ Step 1: Check if ABI is available in cache
        function_abi = None
        if abi_cache is not None:
            print(f"Using cached ABI for module: {module_address}::{module_name}")
            for module in abi_cache:
                if "abi" in module and isinstance(module["abi"], dict):
                    module_abi = module["abi"]
                    if "name" in module_abi and module_abi["name"] == module_name and ("exposed_functions" in module_abi and isinstance(module_abi["exposed_functions"], list)):
                        for func in module_abi["exposed_functions"]:
                            if "name" in func and func["name"] == function_name:
                                function_abi = func
                                break


        # ✅ Step 2: If ABI is not cached, decide whether to fetch
        if not function_abi and optional_fetch_abi:
            print(f"Fetching ABI for module: {module_address}::{module_name}")
            abi_data = await get_account_modules(address=module_address)

            if "modules" in abi_data and isinstance(abi_data["modules"], list):
                # Cache ABI for future calls
                module_list = abi_data["modules"]
                
                # Find function in the new ABI data
                for module in module_list:
                    if "abi" in module and isinstance(module["abi"], dict):
                        module_abi = module["abi"]
                        if "name" in module_abi and module_abi["name"] == module_name and ("exposed_functions" in module_abi and isinstance(module_abi["exposed_functions"], list)):
                            for func in module_abi["exposed_functions"]:
                                if "name" in func and func["name"] == function_name:
                                    function_abi = func
                                    break


        # If we still don't have function ABI, return an error
        if not function_abi:
            return {"error": f"Function `{function_id}` not found in ABI"}

        # ✅ Step 3: Extract generic type parameters (if required)
        expected_type_args = []
        if isinstance(function_abi, dict) and "generic_type_params" in function_abi and "generic_type_params" in function_abi:
            params = function_abi["generic_type_params"]
            if isinstance(params, list):
                expected_type_args = params

            
        if expected_type_args and not type_args:
            return {"error": f"Missing required type arguments for `{function_id}`"}

        print(f"Expected Type Arguments: {expected_type_args}")
        print(f"Provided Type Arguments: {type_args}")

        # ✅ Step 4: Extract required parameters from ABI
        expected_params = get_expected_params(function_abi)

        print(f"Expected Parameters: {expected_params}")
        print(f"Args: {args}")

        # ✅ Step 5: Validate the number of arguments
        # if len(args) != len(expected_params):
        #     return {"error": f"Argument mismatch: expected {len(expected_params)}, got {len(args)}"}

        # ✅ Step 6: Serialize arguments correctly based on ABI types
        serialized_args = []
        for i, arg in enumerate(args):
            # don't go above the expected parameters
            if i >= len(expected_params):
                break
            param_type = expected_params[i]

            if param_type == "u64":
                serialized_args.append(TransactionArgument(value=int(arg), encoder=Serializer.u64))
            elif param_type.startswith("0x"):  # Assume it's an address
                serialized_args.append(TransactionArgument(value=arg, encoder=Serializer.str))
            elif param_type == "bool":
                serialized_args.append(TransactionArgument(value=bool(arg), encoder=Serializer.bool))
            elif param_type.startswith("vector<"):  # Handle vector types
                if not isinstance(arg, list):
                    return {"error": f"Expected a list for `{param_type}` but got {type(arg).__name__}"}
                # Use a single encoder for vectors rather than a list of encoders
                serialized_args.append(TransactionArgument(value=arg, encoder=Serializer.str))
            else:
                serialized_args.append(TransactionArgument(value=arg, encoder=Serializer.str))

        print(f"Serialized Arguments: {serialized_args}")  # Debugging output

        # ✅ Step 7: Execute the function with the dynamically determined shape
        # Convert type_args to the expected TypeTag objects
        converted_type_args = [TypeTag(t) for t in type_args]
        
        payload = EntryFunction.natural(
            module_path,
            function_name,
            converted_type_args,  # Correctly determined type arguments
            serialized_args,  # Correctly formatted function parameters
        )

        # ✅ Create and sign the transaction correctly
        signed_transaction = await rest_client.create_bcs_signed_transaction(
            sender, payload=TransactionPayload(payload)
        )

        # ✅ Submit the transaction and return txn hash
        txn_hash = await rest_client.submit_bcs_transaction(signed_transaction)
        print(f"Transaction submitted successfully! Txn Hash: {txn_hash}")
        return {"txn_hash": txn_hash}

    except Exception as e:
        print(f"Error Details: {e}")  # Debugging output
        return {"error": f"Error executing entry function: {str(e)}"}

def get_expected_params(function_abi: dict[str, Any]) -> list[str]:
    """
    Extract expected parameters from function ABI.
    
    Args:
        function_abi: Function ABI dictionary
        
    Returns:
        List of expected parameter types
    """
    expected_params: list[str] = []
    if isinstance(function_abi, dict) and "params" in function_abi:
        params: Any = function_abi["params"]
        if isinstance(params, list):
            expected_params = params
    
    # Ensure the signer (`&signer`) is NOT included in expected params
    if expected_params and len(expected_params) > 0 and expected_params[0] == "&signer":
        expected_params = expected_params[1:]  # Remove signer from expected params
        print("Automatically handling signer argument")
    
    return expected_params
