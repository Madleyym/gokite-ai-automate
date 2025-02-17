import os
import sys
import json
import random
import time
import uuid
import platform
import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from config import *

class KiteAIBot:
    def __init__(self, wallet_address: str):
        self.wallet_address = wallet_address
        self.daily_points = 0
        self.session_id = str(uuid.uuid4())
        self.device_id = self._generate_device_id()
        self.session = self._setup_session()
        self.used_questions = set()
        self.start_time = datetime.now()
        self.next_reset = self.start_time + timedelta(hours=24)

    def _generate_device_id(self) -> str:
        """Generate a unique device ID."""
        components = [
            platform.system(),
            platform.machine(),
            str(uuid.getnode())
        ]
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, "-".join(components)))

    def _get_random_user_agent(self) -> str:
        """Generate a random user agent."""
        browser = random.choice(BROWSERS)
        version = random.choice(browser["versions"])
        if browser["name"] == "Edge":
            chrome_ver = random.choice(BROWSERS[0]["versions"])
            return browser["template"].format(chrome_ver=chrome_ver, version=version)
        return browser["template"].format(version=version)

    def _setup_session(self) -> requests.Session:
        """Set up a new session with retry strategy."""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _get_headers(self) -> Dict:
        """Generate request headers with anti-detection measures."""
        return {
            "Accept": "text/event-stream",
            "Accept-Language": random.choice([
                "en-US,en;q=0.9",
                "en-GB,en;q=0.8",
                "en-CA,en;q=0.7"
            ]),
            "Connection": random.choice(["keep-alive", "close"]),
            "Content-Type": "application/json",
            "Origin": "https://agents.testnet.gokite.ai",
            "Referer": "https://agents.testnet.gokite.ai/",
            "User-Agent": self._get_random_user_agent(),
            "X-Device-Fingerprint": self.device_id,
            "X-Session-ID": self.session_id
        }

    def _natural_print(self, text: str, color: str = COLORS["WHITE"]) -> None:
        """Print text with natural typing simulation."""
        for char in text:
            print(f"{color}{char}{COLORS['RESET']}", end="", flush=True)
            time.sleep(random.uniform(0.02, 0.08))
        print()

    def _get_random_delay(self) -> float:
        """Get a randomized delay between actions."""
        base_delay = random.uniform(SECURITY["min_delay"], SECURITY["max_delay"])
        jitter = random.uniform(-0.5, 0.5)
        return max(1, base_delay + jitter)

    def send_ai_query(self, endpoint: str, question: str) -> Optional[str]:
        """Send a query to the AI endpoint with anti-detection measures."""
        headers = self._get_headers()
        data = {
            "message": question,
            "stream": True,
            "timestamp": int(time.time()),
            "client_info": {
                "session_id": self.session_id,
                "device_fingerprint": self.device_id
            }
        }

        try:
            time.sleep(self._get_random_delay())
            response = self.session.post(
                endpoint,
                headers=headers,
                json=data,
                stream=True,
                timeout=(10, 30)
            )

            if response.status_code != 200:
                print(f"{COLORS['RED']}Error: Status code {response.status_code}{COLORS['RESET']}")
                return None

            accumulated_response = ""
            print(f"{COLORS['CYAN']}AI Response: {COLORS['RESET']}", end="", flush=True)

            for line in response.iter_lines():
                if line:
                    line_str = line.decode("utf-8")
                    if line_str.startswith("data: "):
                        try:
                            json_str = line_str[6:]
                            if json_str == "[DONE]":
                                break

                            json_data = json.loads(json_str)
                            content = (
                                json_data.get("choices", [{}])[0]
                                .get("delta", {})
                                .get("content", "")
                            )
                            if content:
                                accumulated_response += content
                                print(f"{COLORS['MAGENTA']}{content}{COLORS['RESET']}", end="", flush=True)
                        except json.JSONDecodeError:
                            continue

            print()
            return accumulated_response.strip()

        except Exception as e:
            print(f"{COLORS['RED']}Error in AI query: {str(e)}{COLORS['RESET']}")
            return None

    def report_usage(self, endpoint: str, question: str, response: str) -> bool:
        """Report usage with anti-detection measures."""
        try:
            time.sleep(random.uniform(1, 3))
            resp = self.session.post(
                f"{BASE_URLS['USAGE_API']}/api/report_usage",
                headers=self._get_headers(),
                json={
                    "wallet_address": self.wallet_address,
                    "agent_id": AI_ENDPOINTS[endpoint]["agent_id"],
                    "request_text": question,
                    "response_text": response,
                    "request_metadata": {
                        "timestamp": int(time.time()),
                        "session_id": self.session_id,
                        "device_fingerprint": self.device_id
                    }
                }
            )
            return resp.status_code == 200
        except Exception:
            return False

    def run(self) -> None:
        """Main bot operation loop with security measures."""
        try:
            self._print_banner()
            interaction_count = 0
            consecutive_failures = 0

            while True:
                try:
                    if self.should_reset_daily_points():
                        self.daily_points = 0
                        self.next_reset = datetime.now() + timedelta(hours=24)

                    if self.daily_points >= MAX_DAILY_POINTS:
                        wait_time = (self.next_reset - datetime.now()).total_seconds()
                        print(f"{COLORS['YELLOW']}Daily limit reached. Waiting for reset...{COLORS['RESET']}")
                        time.sleep(wait_time)
                        continue

                    if consecutive_failures > 0:
                        cooldown = SECURITY["cooldown_base"] * (2 ** consecutive_failures)
                        print(f"{COLORS['YELLOW']}Cooling down for {cooldown} seconds...{COLORS['RESET']}")
                        time.sleep(cooldown)

                    self._print_interaction_header(interaction_count + 1)

                    endpoint = random.choice(list(AI_ENDPOINTS.keys()))
                    question = self._get_random_question(endpoint)

                    print(f"\n{COLORS['CYAN']}Selected AI: {AI_ENDPOINTS[endpoint]['name']}")
                    print(f"Question: {COLORS['WHITE']}{question}{COLORS['RESET']}\n")

                    response = self.send_ai_query(endpoint, question)
                    if response:
                        if self.report_usage(endpoint, question, response):
                            self.daily_points += POINTS_PER_INTERACTION
                            interaction_count += 1
                            consecutive_failures = 0

                            delay = self._get_random_delay()
                            print(f"\n{COLORS['YELLOW']}Next query in {delay:.1f} seconds...{COLORS['RESET']}")
                            time.sleep(delay)
                            continue

                    consecutive_failures += 1
                    if consecutive_failures >= SECURITY["max_retries"]:
                        print(f"{COLORS['RED']}Too many failures. Resetting session...{COLORS['RESET']}")
                        self.session = self._setup_session()
                        consecutive_failures = 0
                        time.sleep(SECURITY["cooldown_base"])

                except Exception as e:
                    print(f"{COLORS['RED']}Error: {str(e)}{COLORS['RESET']}")
                    consecutive_failures += 1
                    time.sleep(SECURITY["cooldown_base"])

        except KeyboardInterrupt:
            self._print_final_stats(interaction_count)

    def _print_banner(self) -> None:
        """Print the initial banner."""
        banner = """
╔══════════════════════════════════════════════╗
║               KITE AI AUTOMATE               ║
║          REPORT ON ISSUE IF NEEDED           ║
╚══════════════════════════════════════════════╝
        """
        print(f"{COLORS['CYAN']}{banner}{COLORS['RESET']}")
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(f"Current Time (UTC): {COLORS['GREEN']}{current_time}{COLORS['RESET']}\n")
        print(f"Wallet: {COLORS['GREEN']}{self.wallet_address}{COLORS['RESET']}\n")

    def _print_interaction_header(self, count: int) -> None:
        """Print the interaction header."""
        print(f"\n{COLORS['CYAN']}{'='*50}{COLORS['RESET']}")
        print(f"{COLORS['MAGENTA']}Interaction #{count}{COLORS['RESET']}")
        print(f"{COLORS['CYAN']}Points: {self.daily_points} ({count * 10} Expected){COLORS['RESET']}")

    def _get_random_question(self, endpoint: str) -> str:
        """Get a random unused question."""
        available_questions = [
            q for q in AI_ENDPOINTS[endpoint]["questions"]
            if q not in self.used_questions
        ]
        if not available_questions:
            self.used_questions.clear()
            available_questions = AI_ENDPOINTS[endpoint]["questions"]

        question = random.choice(available_questions)
        self.used_questions.add(question)
        return question

    def should_reset_daily_points(self) -> bool:
        """Check if daily points should be reset."""
        return datetime.now() >= self.next_reset

    def _print_final_stats(self, interaction_count: int) -> None:
        """Print final statistics."""
        print(f"\n{COLORS['CYAN']}=== Final Statistics ==={COLORS['RESET']}")
        print(
            f"Total Interactions: {COLORS['GREEN']}{interaction_count}{COLORS['RESET']}"
        )
        print(f"Total Points: {COLORS['GREEN']}{self.daily_points}{COLORS['RESET']}")
        print(
            f"Session Duration: {COLORS['YELLOW']}{datetime.now() - self.start_time}{COLORS['RESET']}"
        )
        print(
            f"\n{COLORS['YELLOW']}Session ended. Thank you for using Kite AI Bot!{COLORS['RESET']}"
        )


def main() -> None:
    """Main entry point with enhanced security and Termux support."""
    try:
        # Set UTF-8 encoding for Windows
        if os.name == "nt":
            os.system("chcp 65001")

        # Current time and user information
        current_time = "2025-02-17 10:33:03"  # Using provided UTC time
        current_user = "Madleyym"  # Using provided user login

        # Print detailed session information
        print(f"{COLORS['CYAN']}=== KITE AI BOT SESSION INFO ==={COLORS['RESET']}")
        print(f"Started at (UTC): {COLORS['GREEN']}{current_time}{COLORS['RESET']}")
        print(f"User: {COLORS['GREEN']}{current_user}{COLORS['RESET']}")
        print(
            f"System: {COLORS['GREEN']}{platform.system()} {platform.release()}{COLORS['RESET']}"
        )
        print(
            f"Python: {COLORS['GREEN']}{platform.python_version()}{COLORS['RESET']}\n"
        )

        # Get wallet address with default value
        wallet_input = input(
            f"{COLORS['YELLOW']}Enter your registered Wallet Address "
            f"[{COLORS['GREEN']}{DEFAULT_WALLET}{COLORS['YELLOW']}]: {COLORS['RESET']}"
        ).strip()

        wallet_address = wallet_input if wallet_input else DEFAULT_WALLET

        # Validate wallet address format (basic check)
        if not wallet_address.startswith("0x") or len(wallet_address) != 42:
            print(
                f"{COLORS['RED']}Warning: Wallet address format may be invalid{COLORS['RESET']}"
            )
            confirm = input(
                f"{COLORS['YELLOW']}Continue anyway? (y/n): {COLORS['RESET']}"
            ).lower()
            if confirm != "y":
                print(f"{COLORS['RED']}Exiting...{COLORS['RESET']}")
                sys.exit(0)

        # Initialize and run bot with security measures
        bot = KiteAIBot(wallet_address)

        # Add session security info
        print(f"\n{COLORS['CYAN']}=== Security Configuration ==={COLORS['RESET']}")
        print(f"Session ID: {COLORS['GREEN']}{bot.session_id[:8]}...{COLORS['RESET']}")
        print(f"Device ID: {COLORS['GREEN']}{bot.device_id[:8]}...{COLORS['RESET']}")
        print(f"Anti-Detection: {COLORS['GREEN']}Enabled{COLORS['RESET']}")
        print(
            f"Request Delay: {COLORS['GREEN']}{SECURITY['min_delay']}-{SECURITY['max_delay']}s{COLORS['RESET']}"
        )

        # Add confirmation before starting
        print(
            f"\n{COLORS['YELLOW']}Press Enter to start or Ctrl+C to exit...{COLORS['RESET']}"
        )
        input()

        bot.run()

    except KeyboardInterrupt:
        print(f"\n{COLORS['YELLOW']}Script terminated by user.{COLORS['RESET']}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{COLORS['RED']}Fatal error: {str(e)}{COLORS['RESET']}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{COLORS['YELLOW']}Script terminated by user.{COLORS['RESET']}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{COLORS['RED']}Unexpected error: {str(e)}{COLORS['RESET']}")
        sys.exit(1)
