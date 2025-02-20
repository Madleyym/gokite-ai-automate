# KiteAI Bot - Multi-Wallet Configuration

This directory contains the multi-wallet version of the KiteAI Bot that requires proxy configuration for each wallet address.

## Configuration Requirements

Each wallet must have its own proxy configuration in the `config.py` file. The configuration uses the following format:

```python
WALLET_CONFIGS = [
    {
        "wallet": "YOUR_WALLET_ADDRESS",
        "proxy": "YOUR_PROXY_URL",
        "enabled": True
    },
    # Add more wallet configurations as needed
]
```

### Example Configuration:
```python
WALLET_CONFIGS = [
    {
        "wallet": "YOUR_WALLET_ADDRESS",
        "proxy": "YOUR_PROXY_URL",
        "enabled": True
    },
    {
        "wallet": "YOUR_WALLET_ADDRESS",
        "proxy": "YOUR_PROXY_URL",
        "enabled": True
    }
]
```

## Important Rules

1. Each wallet MUST have its own unique proxy
2. The `enabled` field controls whether a wallet is active
3. Proxy URLs must be complete and properly formatted
4. Wallet addresses must be valid EVM addresses

## Features

- Multiple wallet support with proxy integration
- Individual wallet enable/disable control
- Session management for each wallet
- Separate interaction tracking per wallet
- Built-in proxy validation
- Error handling for proxy issues

## Usage

1. Configure your wallets and proxies in `config.py`
2. Run the multi-wallet bot:
```bash
python multi_wallet.py
```

## Daily Limits

- Each wallet is limited to 20 interactions per day
- Limits are tracked separately per wallet
- Reset times are based on UTC

## Proxy Requirements

- HTTP/HTTPS proxies supported
- Authentication must be included in proxy URL
- Stable connection required
- Session-based proxies recommended

## Error Handling

The bot will:
- Verify proxy connectivity before starting
- Skip disabled wallet configurations
- Log proxy-related errors separately
- Attempt reconnection on proxy failures

## Troubleshooting

1. Verify wallet address format
2. Test proxy connections independently
3. Check proxy authentication details
4. Ensure unique proxies for each wallet
5. Verify proxy session duration

## Security Notes

- Keep proxy URLs confidential
- Regularly rotate proxy credentials
- Monitor proxy usage and limits
- Don't share wallet configurations

## Disclaimer

Use at your own risk. Ensure compliance with:
- Platform terms of service
- Proxy provider terms
- Network requirements

For single wallet usage without proxy, refer to the main directory.