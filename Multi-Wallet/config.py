import platform
import random
from datetime import datetime, timedelta

# Core configuration
MAX_DAILY_POINTS = 200
POINTS_PER_INTERACTION = 10

# Multi-wallet configurations
WALLET_CONFIGS = [
    {
        "wallet": "0x0000000000000000000000000000000000000001",  # Example wallet 1
        "proxy": "http://user:pass@host:port",  # Replace with actual proxy
        "enabled": True,
    },
    {
        "wallet": "0x0000000000000000000000000000000000000002",  # Example wallet 2
        "proxy": None,  # Example without proxy
        "enabled": False,
    },
    {
        "wallet": "0x0000000000000000000000000000000000000003",  # Example wallet 3
        "proxy": "http://user:pass@host:port",  # Replace with actual proxy
        "enabled": True,
    },
]

# Security and timing settings
SECURITY = {
    "min_delay": 5.0,
    "max_delay": 12.0,
    "typing_speed": 0.05,
    "max_retries": 3,
    "session_timeout": 7200,  # Ditingkatkan ke 2 jam
    "cooldown_base": 30,
    "request_spacing": {"day": {"min": 10, "max": 20}, "night": {"min": 15, "max": 25}},
}

# Rate limiting configuration
RATE_LIMIT = {
    "hourly_limit": 20,
    "daily_reset": "00:00:00 UTC",
    "cooldown_period": 300,
    "max_requests_per_minute": 6,
    "max_consecutive_requests": 3,
}

# Time-based security settings
TIME_SECURITY = {
    "max_session_duration": 14400,  # 4 jam
    "force_reset_time": "00:00:00 UTC",
    "min_interval_between_requests": {"day": 5, "night": 8},
    "peak_hours": {
        "start": "08:00:00 UTC",
        "end": "20:00:00 UTC",
        "increased_delay": 1.5,  # Multiply normal delay during peak hours
    },
}

# Session management
SESSION_MANAGEMENT = {
    "rotation_interval": 3600,  # Rotate session every 1 hour
    "max_session_age": 7200,  # Maximum 2 hours per session
    "force_rotation_times": ["00:00", "12:00"],  # Force rotation at these times
    "session_cooldown": 300,  # 5 minutes cooldown between sessions
}

# Error handling configuration
ERROR_HANDLING = {
    "max_consecutive_failures": 5,
    "backoff_multiplier": 1.5,
    "max_backoff_time": 300,
    "reset_after_success_duration": 1800,
    "critical_error_cooldown": 900,
}

# Logging configuration
LOGGING = {
    "enabled": True,
    "log_level": "INFO",
    "log_format": "%(asctime)s UTC - %(levelname)s: %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "log_file": f"kite_bot_{datetime.now().strftime('%Y%m%d')}.log",
    "rotate_logs": True,
    "max_log_size": 10485760,  # 10MB
    "backup_count": 5,
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
    "RESET": "\033[0m",
}

# API Base URLs
BASE_URLS = {
    "USAGE_API": "https://quests-usage-dev.prod.zettablock.com/api",
    "STATS_API": "https://quests-usage-dev.prod.zettablock.com/api/user",
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
            "What are the latest updates in Kite AI?",
        ],
        "weight": 50,  # Equal weight with crypto questions
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
        "weight": 50,  # Equal weight with AI questions
    },
}

# Browser configurations
BROWSERS = [
    {
        "name": "Chrome",
        "weight": 70,
        "versions": ["120.0.0.0", "121.0.0.0", "122.0.0.0"],  # Updated to 2025 versions
        "platforms": [
            "Windows NT 10.0; Win64; x64",
            "Macintosh; Intel Mac OS X 10_15_7",
            "X11; Linux x86_64",
        ],
        "template": "Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
    },
    {
        "name": "Edge",
        "weight": 30,
        "versions": [
            "120.0.2210.77",
            "121.0.2277.98",
            "122.0.2345.66",
        ],  # Updated versions
        "platforms": [
            "Windows NT 10.0; Win64; x64",
            "Macintosh; Intel Mac OS X 10_15_7",
        ],
        "template": "Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36 Edg/{version}",
    },
]

# Timeout and connection settings
TIMEOUT_SETTINGS = {
    "CONNECT": 60,
    "READ": 120,
    "MAX_RETRIES": 3,
    "RETRY_DELAY": 1.0,
    "BACKOFF_FACTOR": 1.5,
    "CONNECTION_TIMEOUT": 30,
    "POOL_MAXSIZE": 10,
    "POOL_CONNECTIONS": 10,
}

# Recovery and backup settings
RECOVERY = {
    "enabled": True,
    "backup_interval": 900,  # 15 minutes
    "max_backup_files": 5,
    "auto_restore": True,
    "restore_on_crash": True,
}
