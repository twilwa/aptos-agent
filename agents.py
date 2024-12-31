import os
from dotenv import load_dotenv

# Test configuration
def get_balance_in_apt_sync():
    return "1.0 APT (test mode)"

aptos_agent = {
    "name": "Aptos Agent",
    "get_balance": get_balance_in_apt_sync
}
