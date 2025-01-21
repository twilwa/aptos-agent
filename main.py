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