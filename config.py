from __future__ import annotations
import platform
import uuid
from datetime import datetime, timedelta

# Konfigurasi utama
MAX_DAILY_POINTS = 200
POINTS_PER_INTERACTION = 10
DEFAULT_WALLET = "YOUR_WALLET_ADDRESS"  # Replace with your EVM wallet address

# Proxy configuration
PROXIES = {"YOUR_PROXY_URL"}  # Add your proxy URL if using one"

# Global Headers
GLOBAL_HEADERS = {
    "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8,id;q=0.7",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Origin": "https://agents.testnet.gokite.ai",
    "Referer": "https://agents.testnet.gokite.ai/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

BASE_URLS = {
    "USAGE_API": "https://quests-usage-dev.prod.zettablock.com",
    "STATS_API": "https://quests-usage-dev.prod.zettablock.com/api/user",
}

TIMEOUT_SETTINGS = {"CONNECT": 10, "READ": 15, "RETRY_DELAY": 3}

# Update session settings
SESSION_SETTINGS = {
    "MAX_RETRIES": 3,
    "BACKOFF_FACTOR": 1,
    "STATUS_FORCELIST": [408, 429, 500, 502, 503, 504],
}

RETRY_STRATEGY = {
    "total": 3,
    "backoff_factor": 0.5,
    "status_forcelist": [429, 500, 502, 503, 504],
}

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
            "How does Kite AI handle large-scale data processing?",
            "What types of blockchain networks does Kite AI support?",
            "Can you explain Kite AI's machine learning capabilities?",
            "What are the best practices for using Kite AI in development?",
            "How does Kite AI compare to other blockchain analysis tools?",
            "What kind of API integration does Kite AI offer?",
            "How can Kite AI help in detecting blockchain vulnerabilities?",
            "What are the performance metrics of Kite AI?",
            "How does Kite AI handle real-time blockchain data?",
            "What are the future development plans for Kite AI?",
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
            "What's the trading volume of Bitcoin in the last 24 hours?",
            "How has ETH performed against BTC this week?",
            "What are the top gainers in the crypto market today?",
            "Can you analyze the current market sentiment?",
            "What's the market cap distribution among top 10 coins?",
            "How are DeFi tokens performing in the current market?",
            "What's the current gas price on Ethereum network?",
            "Which cryptocurrencies show strong momentum today?",
            "What's the current fear and greed index in crypto?",
            "How are layer-2 tokens performing in the market?",
        ],
    },
}
