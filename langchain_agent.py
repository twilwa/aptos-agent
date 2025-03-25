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
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# LangChain imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain_core.utils.function_calling import convert_to_openai_function

# Aptos SDK imports
from aptos_sdk.account import Account
from pydantic import SecretStr
from aptos_sdk_wrapper import (
    get_balance, fund_wallet, transfer, get_transaction, get_account_resources, execute_view_function, get_account_modules
)

# Load environment variables
load_dotenv()

# Initialize the agent's wallet
agent_wallet: Account = Account.generate()
agent_address: str = str(agent_wallet.address())

class GetBalanceTool(BaseTool):
    """Tool for getting the balance of an Aptos wallet."""
    name = "get_balance"
    description = "Get the balance of an Aptos wallet"
    
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
    name = "fund_wallet"
    description = "Fund an Aptos wallet with a specified amount of APT"
    
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
    name = "transfer"
    description = "Transfer APT from the agent's wallet to another wallet"
    
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
    name = "get_transaction"
    description = "Get details about a transaction using its hash"
    
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
    name = "get_resources"
    description = "Get the resources associated with an Aptos account"
    
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
    name = "get_modules"
    description = "Get the modules published by an Aptos account"
    
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
    name = "execute_view_function"
    description = "Execute a Move view function on the Aptos blockchain"
    
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
    
    # Convert tools to OpenAI functions
    openai_functions: list[dict[str, Any]] = [convert_to_openai_function(function=t) for t in tools]
    
    # Create prompt
    system_message: str = f"""You are an AI assistant that helps users interact with the Aptos blockchain.
    
Your wallet address is {agent_address}. You can fund your wallet with APT, check balances, transfer APT, and interact with Aptos smart contracts.

When users ask about blockchain concepts, explain them clearly.
When users want to interact with the blockchain, use the appropriate tools.
Always provide clear and helpful responses.

Devnet Explorer: https://explorer.aptoslabs.com/?network=devnet
Aptos Documentation: https://aptos.dev
"""
    
    prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(messages=[
        ("system", system_message),
        ("human", "{input}"),
        ("ai", "{agent_scratchpad}")
    ])
    # Instead of:
# runnable | OpenAIFunctionsAgentOutputParser()
    # Create the agent
    agent: RunnableSerializable[Any, AgentAction | AgentFinish] = (
        RunnablePassthrough.assign(
            input=lambda x: x["input"],
            agent_scratchpad=lambda x: format_to_openai_function_messages(intermediate_steps=x["intermediate_steps"])
        )
        | prompt
        | llm.bind(functions=openai_functions)
        | OpenAIFunctionsAgentOutputParser()
    )
    # Create the agent executor
    agent_executor: AgentExecutor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
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