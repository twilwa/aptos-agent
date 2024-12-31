if __name__ == "__main__":
    print("Aptos Agent Test Mode")
    try:
        from agents import aptos_agent
        print(f"Agent name: {aptos_agent['name']}")
        print(f"Test balance: {aptos_agent['get_balance']()}")
    except Exception as e:
        print(f"Setup error: {e}")
