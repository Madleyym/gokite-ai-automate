import platform
import random
from datetime import datetime, timedelta

# Core configuration
MAX_DAILY_POINTS = 200
POINTS_PER_INTERACTION = 10

# Multi-wallet configurations
# Example configuration template
# Author: Madleyym

# Multi-wallet configurations example
WALLET_CONFIGS = [
    {
        "wallet": "0x0000000000000000000000000000000000000001",  # Example wallet 1
        "proxy": "http://user:pass@host:port",  # Replace with actual proxy
        "enabled": True
    },
    {
        "wallet": "0x0000000000000000000000000000000000000002",  # Example wallet 2
        "proxy": None,  # Example without proxy
        "enabled": False
    },
    {
        "wallet": "0x0000000000000000000000000000000000000003",  # Example wallet 3
        "proxy": "http://user:pass@host:port",  # Replace with actual proxy
        "enabled": True
    }
]

# Security and timing settings
SECURITY = {
    "min_delay": 5.0,
    "max_delay": 12.0,
    "typing_speed": 0.05,
    "max_retries": 3,
    "session_timeout": 3600,
    "cooldown_base": 30,
    "request_spacing": {
        "min": 10,
        "max": 20
    }
}

# Terminal colors
COLORS = {
    "GREEN": "\033[38;2;0;255;0m",
    "RED": "\033[38;2;255;0;0m",
    "YELLOW": "\033[38;2;255;255;0m",
    "BLUE": "\033[38;2;0;150;255m",
    "MAGENTA": "\033[38;2;255;0;255m",
    "CYAN": "\033[38;2;0;255;255m",
    "WHITE": "\033[38;2;255;255;255m",
    "RESET": "\033[0m"
}

# API Base URLs
BASE_URLS = {
    "USAGE_API": "https://quests-usage-dev.prod.zettablock.com/api",
    "STATS_API": "https://quests-usage-dev.prod.zettablock.com/api/user"
}

# AI Endpoints configuration
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
            "What are the latest updates in Kite AI?"
        ]
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
            "Latest price trends in major cryptocurrencies"
        ]
    }
}

# Browser configurations
BROWSERS = [
    {
        "name": "Chrome",
        "weight": 70,
        "versions": ["108.0.0.0", "109.0.0.0", "110.0.0.0", "111.0.0.0"],
        "platforms": [
            "Windows NT 10.0; Win64; x64",
            "Macintosh; Intel Mac OS X 10_15_7",
            "X11; Linux x86_64"
        ],
        "template": "Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"
    },
    {
        "name": "Edge",
        "weight": 30,
        "versions": ["108.0.1462.76", "109.0.1518.78", "110.0.1587.57"],
        "platforms": [
            "Windows NT 10.0; Win64; x64",
            "Macintosh; Intel Mac OS X 10_15_7"
        ],
        "template": "Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36 Edg/{version}"
    }
]

# Timeout settings
TIMEOUT_SETTINGS = {
    "CONNECT": 60,
    "READ": 120,
    "MAX_RETRIES": 3,
    "RETRY_DELAY": 1.0
}