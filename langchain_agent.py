"""
LangChain agent for interacting with the Aptos blockchain.
"""
from asyncio.events import AbstractEventLoop

from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.base import RunnableSerializable
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_openai.chat_models.base import ChatOpenAI

from langchain.agents.agent import AgentExecutor
import os
import asyncio
from typing import Any, Dict, List, Optional, Union, Type
from dotenv import load_dotenv
import pydantic
from pydantic import BaseModel, Field, create_model

# LangChain imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool, Tool
from langchain_core.tools.base import ArgsSchema
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import MessagesPlaceholder

# Aptos SDK imports
from aptos_sdk.account import Account
from aptos_sdk.account_address import AccountAddress
from pydantic import SecretStr

# Import Aptos SDK wrapper functions
# The actual implementations will be available at runtime
from aptos_sdk_wrapper import (
    get_balance, fund_wallet, transfer, get_transaction, 
    get_account_resources, execute_view_function, get_account_modules
)

# Load environment variables
load_dotenv()

# Initialize the agent's wallet
agent_wallet: Account = Account.generate()
agent_address: str = str(agent_wallet.address())

# Helper function to build schema models dynamically
def build_schema(name: str, **field_definitions) -> Type[BaseModel]:
    """
    Dynamically creates a Pydantic model with the given name and field definitions.
    
    Args:
        name: The name of the model to create
        field_definitions: Field definitions as keyword arguments
        
    Returns:
        A new Pydantic model class
    """
    return create_model(name, **field_definitions)

# Dynamically create schema models
GetBalanceSchema = build_schema(
    "GetBalanceSchema",
    address=(Optional[str], Field(None, description="The wallet address to check balance for"))
)

FundWalletSchema = build_schema(
    "FundWalletSchema",
    amount=(int, Field(..., description="Amount of APT to fund (maximum 1000)")),
    address=(Optional[str], Field(None, description="The wallet address to fund"))
)

TransferSchema = build_schema(
    "TransferSchema",
    receiver=(str, Field(..., description="The wallet address to send to")),
    amount=(int, Field(..., description="Amount in octas (1 APT = 10^8 octas)"))
)

GetTransactionSchema = build_schema(
    "GetTransactionSchema",
    txn_hash=(str, Field(..., description="The transaction hash to lookup"))
)

GetResourcesSchema = build_schema(
    "GetResourcesSchema",
    address=(Optional[str], Field(None, description="The account address to get resources for"))
)

GetModulesSchema = build_schema(
    "GetModulesSchema",
    address=(Optional[str], Field(None, description="The account address to get modules for")),
    limit=(int, Field(10, description="Maximum number of modules to return"))
)

# Define empty list factories
def empty_str_list() -> List[str]:
    return []

def empty_any_list() -> List[Any]:
    return []

ExecuteViewFunctionSchema = build_schema(
    "ExecuteViewFunctionSchema",
    function_id=(str, Field(..., description="The full function ID (e.g., '0x1::coin::balance')")),
    type_args=(List[str], Field(default_factory=empty_str_list, description="List of type arguments for the function")),
    args=(List[Any], Field(default_factory=empty_any_list, description="List of arguments to pass to the function"))
)

class GetBalanceTool(BaseTool):
    """Tool for getting the balance of an Aptos wallet."""
    name: str = "get_balance"
    description: str = "Get the balance of an Aptos wallet"
    args_schema: Optional[ArgsSchema] = GetBalanceSchema
    
    def _run(self, address: Optional[str] = None) -> str:
        """Run the tool synchronously."""
        loop: AbstractEventLoop = asyncio.get_event_loop()
        return loop.run_until_complete(future=self._arun(address))
    
    async def _arun(self, address: Optional[str] = None) -> str:
        """Run the tool asynchronously."""
        target_address: str = address or agent_address
        try:
            balance: int = await get_balance(wallet_address=target_address)
            return f"Balance for {target_address}: {balance/10**8} APT"
        except Exception as e:
            return f"Error getting balance: {str(e)}"

class FundWalletTool(BaseTool):
    """Tool for funding an Aptos wallet."""
    name: str = "fund_wallet"
    description: str = "Fund an Aptos wallet with a specified amount of APT"
    args_schema: Optional[ArgsSchema] = FundWalletSchema
    
    def _run(self, amount: int, address: Optional[str] = None) -> str:
        """Run the tool synchronously."""
        loop: AbstractEventLoop = asyncio.get_event_loop()
        return loop.run_until_complete(future=self._arun(amount, address))
    
    async def _arun(self, amount: int, address: Optional[str] = None) -> str:
        """Run the tool asynchronously."""
        target_address: str = address or agent_address
        try:
            if amount > 1000:
                return "Error: Cannot fund more than 1000 APT at once"
            await fund_wallet(wallet_address=target_address, amount=amount)
            return f"Successfully funded {target_address} with {amount} APT"
        except Exception as e:
            return f"Error funding wallet: {str(e)}"

class TransferTool(BaseTool):
    """Tool for transferring APT between wallets."""
    name: str = "transfer"
    description: str = "Transfer APT from the agent's wallet to another wallet"
    args_schema: Optional[ArgsSchema] = TransferSchema
    
    def _run(self, receiver: str, amount: int) -> str:
        """Run the tool synchronously."""
        loop: AbstractEventLoop = asyncio.get_event_loop()
        return loop.run_until_complete(future=self._arun(receiver, amount))
    
    async def _arun(self, receiver: str, amount: int) -> str:
        """Run the tool asynchronously."""
        try:
            octas: int = amount * 10**8  # Convert from APT to octas
            txn_hash: str = await transfer(sender=agent_wallet, receiver=receiver, amount=octas)
            return f"Successfully transferred {amount} APT to {receiver}\nTransaction hash: {txn_hash}"
        except Exception as e:
            return f"Error transferring funds: {str(e)}"

class GetTransactionTool(BaseTool):
    """Tool for getting details about a transaction."""
    name: str = "get_transaction"
    description: str = "Get details about a transaction using its hash"
    args_schema: Optional[ArgsSchema] = GetTransactionSchema
    
    def _run(self, txn_hash: str) -> str:
        """Run the tool synchronously."""
        loop: AbstractEventLoop = asyncio.get_event_loop()
        return loop.run_until_complete(future=self._arun(txn_hash))
    
    async def _arun(self, txn_hash: str) -> str:
        """Run the tool asynchronously."""
        try:
            result = await get_transaction(txn_hash)
            return f"Transaction details: {result}"
        except Exception as e:
            return f"Error getting transaction: {str(e)}"

class GetResourcesTool(BaseTool):
    """Tool for getting account resources."""
    name: str = "get_resources"
    description: str = "Get the resources associated with an Aptos account"
    args_schema: Optional[ArgsSchema] = GetResourcesSchema
    
    def _run(self, address: Optional[str] = None) -> str:
        """Run the tool synchronously."""
        loop: AbstractEventLoop = asyncio.get_event_loop()
        return loop.run_until_complete(future=self._arun(address))
    
    async def _arun(self, address: Optional[str] = None) -> str:
        """Run the tool asynchronously."""
        target_address: str = address or agent_address
        try:
            resources: List[Dict[str, Any]] = await get_account_resources(address=target_address)
            # Format for better readability - just show types
            resource_types: list[Any] = [res['type'] for res in resources if 'type' in res]
            summary: str = f"Account {target_address} has {len(resource_types)} resources:\n"
            for i, res_type in enumerate(resource_types[:10]):
                summary += f"{i+1}. {res_type}\n"
            if len(resource_types) > 10:
                summary += f"... and {len(resource_types) - 10} more"
            return summary
        except Exception as e:
            return f"Error getting account resources: {str(e)}"

class GetModulesTool(BaseTool):
    """Tool for getting account modules."""
    name: str = "get_modules"
    description: str = "Get the modules published by an Aptos account"
    args_schema: Optional[ArgsSchema] = GetModulesSchema
    
    def _run(self, address: Optional[str] = None, limit: int = 10) -> str:
        """Run the tool synchronously."""
        loop: AbstractEventLoop = asyncio.get_event_loop()
        return loop.run_until_complete(future=self._arun(address, limit))
    
    async def _arun(self, address: Optional[str] = None, limit: int = 10) -> str:
        """Run the tool asynchronously."""
        target_address: str = address or agent_address
        try:
            result: dict[str, Any] = await get_account_modules(address=target_address, limit=limit)
            if "error" in result:
                return f"Error: {result['error']}"
            
            modules: list[dict[str, Any]] = result.get("modules", [])
            if not modules:
                return f"Account {target_address} has no published modules."
            
            summary: str = f"Account {target_address} has {len(modules)} modules:\n"
            for i, module in enumerate(modules):
                if "abi" in module and "name" in module["abi"]:
                    name: str = module["abi"]["name"]
                    summary += f"{i+1}. {name}\n"
                    
                    # Add exposed function names
                    if "abi" in module and "exposed_functions" in module["abi"]:
                        functions: list[Any] = module["abi"]["exposed_functions"]
                        for j, func in enumerate(functions[:5]):
                            if "name" in func:
                                summary += f"   - {func['name']}\n"
                        if len(functions) > 5:
                            summary += f"   - ... and {len(functions) - 5} more functions\n"
            
            return summary
        except Exception as e:
            return f"Error getting account modules: {str(e)}"

class ExecuteViewFunctionTool(BaseTool):
    """Tool for executing a view function."""
    name: str = "execute_view_function"
    description: str = "Execute a Move view function on the Aptos blockchain"
    args_schema: Optional[ArgsSchema] = ExecuteViewFunctionSchema
    
    def _run(self, function_id: str, type_args: Optional[List[str]] = None, args: Optional[List[Any]] = None) -> str:
        """Run the tool synchronously."""
        loop: AbstractEventLoop = asyncio.get_event_loop()
        # Initialize empty lists if None is passed
        _type_args = type_args if type_args is not None else []
        _args = args if args is not None else []
        return loop.run_until_complete(future=self._arun(function_id, _type_args, _args))
    
    async def _arun(self, function_id: str, type_args: List[str], args: List[Any]) -> str:
        """Run the tool asynchronously."""
        try:
            result: dict[str, Any] = await execute_view_function(function_id=function_id, type_args=type_args, args=args)
            return f"View function result: {result}"
        except Exception as e:
            return f"Error executing view function: {str(e)}"

def create_aptos_agent(api_key: str | None = None) -> AgentExecutor:
    """Create a LangChain agent that can interact with Aptos blockchain."""
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found. Please provide it as an argument or set OPENAI_API_KEY environment variable.")
    
    # Initialize language model
    llm: ChatOpenAI = ChatOpenAI(temperature=0, model="gpt-4o", api_key=SecretStr(secret_value=api_key))
    
    # Create tools
    tools: list[BaseTool] = [
        GetBalanceTool(),
        FundWalletTool(),
        TransferTool(),
        GetTransactionTool(),
        GetResourcesTool(),
        GetModulesTool(),
        ExecuteViewFunctionTool()
    ]
    
    # Get user wallet address from environment if available
    user_wallet_address: Optional[str] = os.getenv("DEVNET_WALLET_ADDRESS")
    user_wallet_info = f"\nThe user's wallet address is {user_wallet_address}" if user_wallet_address else ""
    
    # Convert tools to OpenAI functions
    openai_functions: list[dict[str, Any]] = [convert_to_openai_function(function=t) for t in tools]
    
    # Create prompt with memory
    system_message: str = f"""You are an AI assistant that helps users interact with the Aptos blockchain.
    
Your wallet address is {agent_address}. You can fund your wallet with APT, check balances, transfer APT, and interact with Aptos smart contracts.{user_wallet_info}

When users ask about blockchain concepts, explain them clearly.
When users want to interact with the blockchain, use the appropriate tools.
When users refer to "my wallet" or "my account", they are referring to their own wallet.
When a user asks to see their balance, use their wallet address, not yours.
Always provide clear and helpful responses.

You have memory and can remember previous parts of the conversation. When users refer to previous questions or interactions, use your memory to provide context-aware responses.

Devnet Explorer: https://explorer.aptoslabs.com/?network=devnet
Aptos Documentation: https://aptos.dev
"""
    
    # Initialize memory with return_messages=True for proper handling in the prompt
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
    )
    
    # Create prompt template with chat history
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create the agent
    agent: Any = (
        {
            "input": lambda x: x["input"],
            "chat_history": lambda x: x.get("chat_history", []),
            "agent_scratchpad": lambda x: format_to_openai_function_messages(x["intermediate_steps"]),
        }
        | prompt
        | llm.bind(functions=openai_functions)
        | OpenAIFunctionsAgentOutputParser()
    )
    
    # Create agent executor with memory
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        return_intermediate_steps=True,
    )
    
    return agent_executor

async def main() -> None:
    """Run the Aptos LangChain agent."""
    agent_executor: AgentExecutor = create_aptos_agent()
    
    print("Aptos LangChain Agent")
    print(f"Agent wallet address: {agent_address}")
    print("Type 'exit' to quit.")
    
    while True:
        user_input: str = input("\nEnter your message: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        try:
            # The response is a dictionary containing the output
            response = await agent_executor.ainvoke(input={"input": user_input})
            print(f"\nAgent response: {response['output']}")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 