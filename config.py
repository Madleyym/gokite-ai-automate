import platform
import uuid
from datetime import datetime, timedelta

# Core configuration
MAX_DAILY_POINTS = 200
POINTS_PER_INTERACTION = 10
DEFAULT_WALLET = "YOUR_WALLET_ADDRESS"

# Security and timing settings
SECURITY = {
    "min_delay": 5.0,
    "max_delay": 12.0,
    "typing_speed": 0.05,
    "max_retries": 3,
    "session_timeout": 3600,
    "cooldown_base": 30,
}

# Terminal colors with RGB values
COLORS = {
    "GREEN": "\033[38;2;0;255;0m",
    "RED": "\033[38;2;255;0;0m",
    "YELLOW": "\033[38;2;255;255;0m",
    "BLUE": "\033[38;2;0;150;255m",
    "MAGENTA": "\033[38;2;255;0;255m",
    "CYAN": "\033[38;2;0;255;255m",
    "WHITE": "\033[38;2;255;255;255m",
    "RESET": "\033[0m",
}

# Updated Base URLs
BASE_URLS = {
    "USAGE_API": "https://quests-usage-dev.prod.zettablock.com/api",  
    "STATS_API": "https://quests-usage-dev.prod.zettablock.com/api/user"
}

# Updated AI Endpoints with new endpoints and questions
AI_ENDPOINTS = {
    "https://deployment-hp4y88pxnqxwlmpxllicjzzn.stag-vxzy.zettablock.com/main": {
        "agent_id": "deployment_Hp4Y88pxNQXwLMPxlLICJZzN",
        "name": "Kite AI Assistant",
        "questions": [
            "What is Kite AI and how does it work?",
            "Can you explain the main features of Kite AI?",
            "How can developers benefit from using Kite AI?",
            "What makes Kite AI different from other platforms?",
            "Tell me about Kite AI's blockchain integration",
            "How does Kite AI help with smart contract analysis?",
            "What are the key advantages of Kite AI?",
            "Explain Kite AI's approach to blockchain data",
            "How does Kite AI ensure security?",
            "What are the latest updates in Kite AI?",
        ],
    },
    "https://deployment-nc3y3k7zy6gekszmcsordhu7.stag-vxzy.zettablock.com/main": {
        "agent_id": "deployment_nC3y3k7zy6gekSZMCSordHu7",
        "name": "Crypto Price Assistant",
        "questions": [
            "What's the current price of Bitcoin?",
            "Show me Ethereum's current market status",
            "How is the crypto market performing today?",
            "Tell me about BNB's current price",
            "What's happening with Solana right now?",
            "Current market analysis for MATIC",
            "Give me an update on DOT's price",
            "What's the latest on AVAX?",
            "Current crypto market overview",
            "Latest price trends in major cryptocurrencies",
        ],
    },
}

# Updated Browser configurations
BROWSERS = [
    {
        "name": "Chrome",
        "versions": ["108.0.0.0", "109.0.0.0", "110.0.0.0", "111.0.0.0"],
        "template": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
    },
    {
        "name": "Edge",
        "versions": ["108.0.1462.76", "109.0.1518.78", "110.0.1587.57"],
        "template": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36 Edg/{version}",
    },
]

# Add TIMEOUT_SETTINGS
TIMEOUT_SETTINGS = {"CONNECT": 60, "READ": 120}