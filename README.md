# Kite AI Bot

An automated interaction bot for the Kite AI platform that helps users engage with AI agents while respecting daily limits and implementing security best practices.

## Features

- Automated interactions with multiple Kite AI agents
- Daily interaction limit management (20 interactions per day)
- Anti-detection measures with rotating user agents
- Secure session handling and error recovery
- Real-time interaction tracking and statistics
- Colorized console output for better visibility
- Cross-platform support (Windows, Linux, MacOS)

## Requirements

- Python 3.7+
- Required packages:
  - requests
  - urllib3
  - typing
  - json
  - datetime

## Installation

1. Clone this repository or download the source code
2. Install the required dependencies:
```bash
pip install requests urllib3
```

## Configuration

### Setting Up config.py

1. Create a `config.py` file in the project directory
2. Configure your EVM (Ethereum Virtual Machine) wallet address:
```python
DEFAULT_WALLET = "YOUR_EVM_WALLET_ADDRESS"  # Replace with your EVM wallet address
```

Important: Your wallet address must:
- Start with "0x"
- Be 42 characters long
- Be a valid EVM-compatible address

Other configuration parameters in `config.py`:
- `MAX_DAILY_POINTS`: Maximum daily points (200)
- `POINTS_PER_INTERACTION`: Points earned per interaction (10)
- Security settings:
  - `min_delay`: Minimum delay between requests (5.0s)
  - `max_delay`: Maximum delay between requests (12.0s)
  - `max_retries`: Maximum retry attempts (3)
  - `cooldown_base`: Base cooldown period (30s)

## Usage

1. Run the script:
```bash
python bot.py
```

2. Enter your wallet address when prompted (or press Enter to use the default wallet)

3. The bot will automatically:
   - Manage daily interaction limits
   - Rotate between different AI agents
   - Use random questions from predefined sets
   - Report usage and track points
   - Handle errors and maintain session security

## Known Behaviors

### Report Interaction Messages

You may see messages like:
```
Reporting interaction... ✗ Status: XXX (Points still counted)
```
or
```
Reporting interaction... ✗ Error: [error message] (Points still counted)
```

These messages are **normal** and **non-critical**. The bot will:
- Continue running normally
- Still count the interaction towards your daily total
- Still earn points for the interaction
- No action is required from your side

## Features in Detail

### Security Measures

- Random delays between requests
- Rotating user agents
- Session management
- Device fingerprinting
- Error handling and retry mechanisms

### Anti-Detection

- Multiple browser profiles
- Random user agent rotation
- Varied request delays
- Session ID management
- Device ID generation

### Interaction Management

- Tracks daily interaction limits
- Manages interaction cooldowns
- Rotates questions to avoid repetition
- Reports usage to API endpoints
- Provides real-time statistics

## Console Output

The bot provides detailed console output with color coding:
- Green: Success messages
- Yellow: Warnings and notifications (including non-critical report errors)
- Red: Errors and failures
- Cyan: Information and statistics
- Magenta: AI responses and interaction numbers
- White: Questions and general text

## Error Handling

The bot implements comprehensive error handling:
- Automatic session reset after multiple failures
- Configurable retry strategy
- Graceful shutdown on interruption
- Session timeout handling
- Network error recovery
- Non-critical report errors are handled gracefully

## Statistics and Tracking

Provides real-time statistics including:
- Total daily interactions
- Remaining interactions
- Session duration
- Success/failure rates
- Next reset time

## Security Notice

This bot implements security best practices but should be used responsibly and in accordance with Kite AI's terms of service. Always ensure you have permission to use automated tools with any service.

## Disclaimer

This bot is provided as-is without any guarantees. Users are responsible for ensuring their use of the bot complies with Kite AI's terms of service and usage policies.