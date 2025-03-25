from typing import Any, Dict, List, Optional, Union


from langchain.agents.agent import AgentExecutor


import os
from dotenv import load_dotenv, set_key
from aptos_sdk.account import Account
import asyncio
from langchain_agent import create_aptos_agent, agent_address
from pydantic import BaseModel

def check_and_update_env() -> str:
    """Check and update environment variables required for the application."""
    # Load existing environment variables
    load_dotenv()

    # Check for OpenAI API key
    api_key: Optional[str] = os.getenv('OPENAI_API_KEY')
    if not api_key:
        api_key = input("Enter your OpenAI API key: ").strip()
        set_key(dotenv_path='.env', key_to_set='OPENAI_API_KEY', value_to_set=api_key)
    else:
        print(f"Found OpenAI API key: {api_key[:5]}...{api_key[-5:]}")

    # Check for Devnet wallet address
    wallet_address: Optional[str] = os.getenv('DEVNET_WALLET_ADDRESS')
    if not wallet_address:
        wallet_address = input("Enter your Devnet wallet address (Optional - Press enter to automatically generate one): ").strip()
        if not wallet_address:
            wallet_address = str(Account.generate().address)
            print("Generated user wallet:", wallet_address)
        set_key(dotenv_path='.env', key_to_set='DEVNET_WALLET_ADDRESS', value_to_set=wallet_address)
    else:
        print(f"Found Devnet wallet address: {wallet_address}")
    
    return api_key if api_key else ""

async def run_langchain_agent(api_key: Optional[str] = None) -> None:
    """Run the Aptos LangChain agent."""
    # Create the agent executor
    agent_executor: AgentExecutor = create_aptos_agent(api_key)
    
    print("Aptos LangChain Agent")
    print(f"Agent wallet address: {agent_address}")
    print("Type 'exit' to quit.")
    
    user_wallet: Optional[str] = os.getenv('DEVNET_WALLET_ADDRESS')
    if user_wallet:
        print(f"User wallet address: {user_wallet}")
        # Initialize the agent with user wallet context
        print("\nSetting up initial context for the agent...")
        initial_response = await agent_executor.ainvoke(input={"input": "Hello! Please confirm you can see my wallet address."})
        print(f"\nAgent: {initial_response['output']}")
        
        # Test memory with a follow-up question
        print("\nTesting agent memory...")
        second_response = await agent_executor.ainvoke(input={"input": "What was my previous question about?"})
        print(f"\nAgent: {second_response['output']}")
    else:
        print("No user wallet address found in environment variables.")
    
    while True:
        try:
            user_input: str = input("\nEnter your message (or 'exit' to quit): ").strip()
            if user_input.lower() in ["exit", "quit", "q"]:
                break
                
            # The response is a dictionary containing the output
            response: Dict[str, Any] = await agent_executor.ainvoke(input={"input": user_input})
            print(f"\nAgent response: {response['output']}")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    try:
        api_key: str = check_and_update_env()
        
        # Run the LangChain agent
        asyncio.run(run_langchain_agent(api_key))
    except Exception as e:
        print(f"Error: {str(e)}")