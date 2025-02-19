# KiteAI Bot

An automated interaction bot for the Kite AI testnet platform that simulates human-like behavior while managing API interactions with various AI agents.

## Features

- Automated interaction with multiple Kite AI agents
- Human-like behavior simulation with natural typing and response patterns
- Daily interaction limit management (20 interactions per day)
- Sophisticated anti-detection mechanisms
- Robust error handling and session management
- Detailed interaction logging and statistics
- Cross-platform support (Windows, macOS, Linux, Termux)

## Prerequisites

- Python 3.7 or higher
- Required Python packages:
  - requests
  - urllib3
  - platform
  - uuid

## Installation

1. Clone the repository or download the source code
2. Install the required dependencies:
```bash
pip install requests urllib3
```
3. Configure your settings in `config.py` (see Configuration section)

## Configuration

Before running the bot, make sure to set up your configuration in `config.py`:

- `DEFAULT_WALLET`: Your default wallet address
- `BASE_URLS`: API endpoint URLs
- `AI_ENDPOINTS`: Available AI agents and their configurations
- `SECURITY`: Security and timing settings
- `TIMEOUT_SETTINGS`: Request timeout configurations
- `BROWSERS`: Browser configurations for request headers

## Usage

1. Run the script:
```bash
python main.py
```

2. Enter your wallet address when prompted (or press Enter to use the default wallet)

3. The bot will automatically:
   - Generate a unique session ID and device fingerprint
   - Manage daily interaction limits
   - Rotate between different AI agents
   - Report usage statistics
   - Handle errors and retries

## Security Features

- Random user agent rotation
- Device fingerprinting
- Session management
- Natural typing simulation
- Random delays between actions
- Automatic retry handling
- Request header randomization

## Monitoring and Statistics

The bot provides real-time information about:
- Current interaction count
- Remaining daily interactions
- Session duration
- Success/failure rates
- Next reset time
- Detailed response logging

## Error Handling

The bot includes comprehensive error handling for:
- Network issues
- API rate limits
- Invalid responses
- Session timeouts
- Daily limit exceedance

## Important Notes

1. Daily Limit: The bot is limited to 20 interactions per day (UTC)
2. Rate Limiting: Includes built-in delays to prevent rate limiting
3. Session Management: Automatically handles session resets and cooldowns
4. Anti-Detection: Implements various measures to avoid detection

## Termination

- Use Ctrl+C to safely terminate the bot
- The bot will display final statistics upon termination
- Session data will be preserved for the next run

## Troubleshooting

If you encounter issues:

1. Check your wallet address format
2. Verify network connectivity
3. Ensure correct configuration in `config.py`
4. Check console output for error messages
5. Verify API endpoint availability

## Contributing

Contributions are welcome! Please feel free to submit pull requests or create issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This bot is intended for testing purposes on the Kite AI testnet. Please use responsibly and in accordance with the platform's terms of service.