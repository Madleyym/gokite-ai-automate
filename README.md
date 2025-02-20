# KiteAI Bot

An automated interaction bot for the Kite AI testnet platform that uses a single EVM wallet address. For multi-wallet functionality, please check the `/Multi-Wallet` directory.

## Features

- Single EVM wallet support (non-proxy)
- Automated interaction with Kite AI agents
- Human-like behavior simulation
- Daily interaction limit management (20 interactions per day)
- Anti-detection mechanisms
- Detailed interaction logging
- Cross-platform support (Windows, macOS, Linux, Termux)

## Prerequisites

- Python 3.7 or higher
- Required packages:
  - requests
  - urllib3
  - platform
  - uuid

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install requests urllib3
```

## Configuration

Edit `config.py` and set your wallet address:
```python
DEFAULT_WALLET = "YOUR_WALLET_ADDRESS"  # Required: Set your EVM wallet address
```

## Usage

1. Run the bot:
```bash
python main.py
```

2. Bot will automatically:
   - Use your configured wallet address
   - Manage daily interaction limits
   - Handle errors and retries
   - Report statistics

## Important Notes

1. This version supports ONE wallet address only
2. Daily limit: 20 interactions per day
3. For multi-wallet setup, see `/Multi-Wallet` directory
4. No proxy required for single wallet usage

## Troubleshooting

1. Check wallet address format in config.py
2. Verify network connectivity
3. Check console for error messages

## License

MIT License - see LICENSE file for details.

## Disclaimer

For testnet use only. Use responsibly and in accordance with platform terms.