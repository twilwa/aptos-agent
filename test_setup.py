import os
from dotenv import load_dotenv
import openai
import asyncio

load_dotenv()

def test_openai_connection():
    """Test OpenAI API connection"""
    try:
        openai.api_key = os.getenv('OPENAI_API_KEY')
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello!"}]
        )
        print("OpenAI Connection Test:", response.choices[0].message.content)
        return True
    except Exception as e:
        print(f"OpenAI Connection Error: {str(e)}")
        return False

async def test_aptos_connection_async():
    """Test Aptos connection asynchronously"""
    from aptos_sdk_wrapper import get_balance
    from aptos_sdk.account import Account
    
    try:
        # Generate a test account
        test_account = Account.generate()
        address = str(test_account.address())
        
        # Try to get balance
        balance = await get_balance(wallet_address=address)
        print(f"Aptos Connection Test - Balance: {balance/10**8} APT")
        return True
    except Exception as e:
        print(f"Aptos Connection Error: {str(e)}")
        return False

def test_aptos_connection():
    """Test Aptos connection (synchronous wrapper)"""
    return asyncio.run(test_aptos_connection_async())

def test_langchain_setup():
    """Test LangChain setup"""
    try:
        from langchain_openai import ChatOpenAI
        from langchain.agents import AgentExecutor
        from langchain_agent import create_aptos_agent
        
        # Just test imports, don't actually create the agent
        print("LangChain imports successful")
        return True
    except Exception as e:
        print(f"LangChain Setup Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing connections...")
    openai_ok = test_openai_connection()
    aptos_ok = test_aptos_connection()
    langchain_ok = test_langchain_setup()
    
    if openai_ok and aptos_ok and langchain_ok:
        print("\n✅ All connections successful!")
    else:
        print("\n❌ Some connections failed. Check errors above.")