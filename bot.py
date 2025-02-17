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

    def safe_print(self, text: str, color: str = "", end: str = "\n") -> None:
        """Print text safely with encoding handling."""
        try:
            print(f"{color}{text}{COLORS['RESET']}", end=end, flush=True)
        except UnicodeEncodeError:
            ascii_text = text.encode('ascii', 'replace').decode()
            print(f"{color}{ascii_text}{COLORS['RESET']}", end=end, flush=True)

    def _get_random_delay(self) -> float:
        """Get a randomized delay between actions."""
        base_delay = random.uniform(SECURITY["min_delay"], SECURITY["max_delay"])
        jitter = random.uniform(-0.5, 0.5)
        return max(1, base_delay + jitter)

    def _get_current_utc(self) -> str:
        """Get current UTC timestamp."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def report_usage(self, endpoint: str, question: str, response: str) -> bool:
        """Report usage with enhanced feedback and retry mechanism."""
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                self.safe_print("Reporting interaction... ", COLORS["CYAN"], end="")
                time.sleep(random.uniform(1, 2))

                report_data = {
                    "wallet_address": self.wallet_address,
                    "agent_id": AI_ENDPOINTS[endpoint]["agent_id"],
                    "request_text": question,
                    "response_text": response,
                    "request_metadata": {
                        "timestamp": int(time.time()),
                        "session_id": self.session_id,
                        "device_fingerprint": self.device_id,
                        "timestamp_utc": self._get_current_utc()
                    }
                }

                resp = self.session.post(
                    f"{BASE_URLS['USAGE_API']}/api/report_usage",
                    headers=self._get_headers(),
                    json=report_data,
                    timeout=(10, 30)
                )

                if resp.status_code == 200:
                    self.safe_print("✓ Success!", COLORS["GREEN"])
                    return True
                else:
                    self.safe_print(f"✗ Failed (Status: {resp.status_code})", COLORS["RED"])
                    try:
                        error_detail = resp.json()
                        self.safe_print(f"Error detail: {error_detail}", COLORS["RED"])
                    except:
                        pass

            except requests.exceptions.Timeout:
                self.safe_print("✗ Timeout", COLORS["RED"])
            except requests.exceptions.ConnectionError:
                self.safe_print("✗ Connection Error", COLORS["RED"])
            except Exception as e:
                self.safe_print(f"✗ Error: {str(e)}", COLORS["RED"])

            retry_count += 1
            if retry_count < max_retries:
                wait_time = 2 ** retry_count
                self.safe_print(f"Retrying in {wait_time} seconds... (Attempt {retry_count + 1}/{max_retries})", COLORS["YELLOW"])
                time.sleep(wait_time)

        return False

    def send_ai_query(self, endpoint: str, question: str) -> Optional[str]:
        """Send a query to the AI endpoint with enhanced feedback."""
        headers = self._get_headers()
        data = {
            "message": question,
            "stream": True,
            "timestamp": int(time.time()),
            "client_info": {
                "session_id": self.session_id,
                "device_fingerprint": self.device_id,
                "timestamp_utc": self._get_current_utc()
            }
        }

        self.safe_print("Sending query... ", COLORS["CYAN"], end="")
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
                self.safe_print(f"✗ Failed (Status: {response.status_code})", COLORS["RED"])
                return None

            self.safe_print("✓", COLORS["GREEN"])
            self.safe_print("\nAI Response: ", COLORS["CYAN"], end="")

            accumulated_response = ""
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
                                self.safe_print(content, COLORS["MAGENTA"], end="")
                        except json.JSONDecodeError:
                            continue

            print()
            return accumulated_response.strip()

        except requests.exceptions.Timeout:
            self.safe_print("✗ Request Timeout", COLORS["RED"])
        except requests.exceptions.ConnectionError:
            self.safe_print("✗ Connection Error", COLORS["RED"])
        except Exception as e:
            self.safe_print(f"✗ Error: {str(e)}", COLORS["RED"])

        return None

    def _print_banner(self) -> None:
        """Print the initial banner."""
        banner = """
┌──────────────────────────────────────────────┐
│               KITE AI AUTOMATE               │
│          REPORT ON ISSUE IF NEEDED           │
└──────────────────────────────────────────────┘
        """
        self.safe_print(banner, COLORS["CYAN"])
        current_time = self._get_current_utc()
        self.safe_print(f"Current Time (UTC): {current_time}", COLORS["GREEN"])
        self.safe_print(f"Wallet: {self.wallet_address}\n", COLORS["GREEN"])

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
        self.safe_print("\n=== Final Statistics ===", COLORS["CYAN"])
        self.safe_print(f"Total Interactions: {interaction_count}", COLORS["GREEN"])
        self.safe_print(f"Total Points: {self.daily_points}", COLORS["GREEN"])
        self.safe_print(f"Session Duration: {datetime.now() - self.start_time}", COLORS["YELLOW"])
        self.safe_print("\nSession ended. Thank you for using Kite AI Bot!", COLORS["YELLOW"])

    # ... (lanjutan kode sebelumnya)

    def run(self) -> None:
        """Main bot operation loop with enhanced feedback."""
        try:
            self._print_banner()
            interaction_count = 0
            consecutive_failures = 0

            while True:
                try:
                    if self.should_reset_daily_points():
                        self.daily_points = 0
                        self.next_reset = datetime.now() + timedelta(hours=24)
                        self.safe_print("Daily points reset!", COLORS["GREEN"])

                    if self.daily_points >= MAX_DAILY_POINTS:
                        wait_time = (self.next_reset - datetime.now()).total_seconds()
                        self.safe_print(
                            "Daily limit reached. Waiting for reset...",
                            COLORS["YELLOW"],
                        )
                        time.sleep(wait_time)
                        continue

                    if consecutive_failures > 0:
                        cooldown = SECURITY["cooldown_base"] * (2**consecutive_failures)
                        self.safe_print(
                            f"Cooling down for {cooldown} seconds...", COLORS["YELLOW"]
                        )
                        for i in range(int(cooldown), 0, -1):
                            self.safe_print(
                                f"Resuming in {i} seconds...",
                                COLORS["YELLOW"],
                                end="\r",
                            )
                            time.sleep(1)
                        print()  # Clear the line

                    self.safe_print("\n" + "=" * 50, COLORS["CYAN"])
                    self.safe_print(
                        f"Interaction #{interaction_count + 1}", COLORS["MAGENTA"]
                    )
                    self.safe_print(
                        f"Points: {self.daily_points} ({(interaction_count + 1) * 10} Expected)",
                        COLORS["CYAN"],
                    )

                    endpoint = random.choice(list(AI_ENDPOINTS.keys()))
                    question = self._get_random_question(endpoint)

                    self.safe_print(
                        f"\nSelected AI: {AI_ENDPOINTS[endpoint]['name']}",
                        COLORS["CYAN"],
                    )
                    self.safe_print(f"Question: {question}\n", COLORS["WHITE"])

                    response = self.send_ai_query(endpoint, question)
                    if response:
                        self.safe_print(
                            "\nProcessing response... ", COLORS["CYAN"], end=""
                        )
                        time.sleep(random.uniform(0.5, 1.5))

                        if self.report_usage(endpoint, question, response):
                            self.safe_print("✓ Complete!", COLORS["GREEN"])
                            self.daily_points += POINTS_PER_INTERACTION
                            interaction_count += 1
                            consecutive_failures = 0

                            delay = self._get_random_delay()
                            self.safe_print(
                                f"\nNext query in {delay:.1f} seconds...",
                                COLORS["YELLOW"],
                            )
                            for i in range(int(delay), 0, -1):
                                self.safe_print(
                                    f"Starting in {i} seconds...",
                                    COLORS["YELLOW"],
                                    end="\r",
                                )
                                time.sleep(1)
                            print()  # Clear the line
                            continue
                        else:
                            self.safe_print("✗ Report failed", COLORS["RED"])

                    consecutive_failures += 1
                    if consecutive_failures >= SECURITY["max_retries"]:
                        self.safe_print(
                            "Too many failures. Resetting session...", COLORS["RED"]
                        )
                        self.session = self._setup_session()
                        consecutive_failures = 0
                        time.sleep(SECURITY["cooldown_base"])

                except Exception as e:
                    self.safe_print(f"Error: {str(e)}", COLORS["RED"])
                    consecutive_failures += 1
                    time.sleep(SECURITY["cooldown_base"])

        except KeyboardInterrupt:
            self._print_final_stats(interaction_count)


def main() -> None:
    """Main entry point with enhanced security and Termux support."""
    try:
        # Set console mode for Windows
        if sys.platform.startswith("win"):
            os.system("color")
            os.system("mode con: cols=80 lines=25")
            # Enable Windows UTF-8 support
            os.system("chcp 65001")

        # Print session information safely
        bot = KiteAIBot(DEFAULT_WALLET)
        bot.safe_print("=== KITE AI BOT SESSION INFO ===", COLORS["CYAN"])
        bot.safe_print(
            f"Started at (UTC): {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}",
            COLORS["GREEN"],
        )
        bot.safe_print(
            f"System: {platform.system()} {platform.release()}", COLORS["GREEN"]
        )
        bot.safe_print(f"Python: {platform.python_version()}\n", COLORS["GREEN"])

        # Get wallet address
        wallet_input = input(
            f"{COLORS['YELLOW']}Enter your registered Wallet Address "
            f"[{COLORS['GREEN']}{DEFAULT_WALLET}{COLORS['YELLOW']}]: {COLORS['RESET']}"
        ).strip()

        wallet_address = wallet_input if wallet_input else DEFAULT_WALLET

        # Validate wallet address format
        if not wallet_address.startswith("0x") or len(wallet_address) != 42:
            bot.safe_print(
                "Warning: Wallet address format may be invalid", COLORS["RED"]
            )
            confirm = input(
                f"{COLORS['YELLOW']}Continue anyway? (y/n): {COLORS['RESET']}"
            ).lower()
            if confirm != "y":
                bot.safe_print("Exiting...", COLORS["RED"])
                sys.exit(0)

        # Initialize bot with provided wallet
        bot = KiteAIBot(wallet_address)

        # Print security configuration
        bot.safe_print("\n=== Security Configuration ===", COLORS["CYAN"])
        bot.safe_print(f"Session ID: {bot.session_id[:8]}...", COLORS["GREEN"])
        bot.safe_print(f"Device ID: {bot.device_id[:8]}...", COLORS["GREEN"])
        bot.safe_print("Anti-Detection: Enabled", COLORS["GREEN"])
        bot.safe_print(
            f"Request Delay: {SECURITY['min_delay']}-{SECURITY['max_delay']}s",
            COLORS["GREEN"],
        )

        # Add confirmation before starting
        bot.safe_print("\nPress Enter to start or Ctrl+C to exit...", COLORS["YELLOW"])
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
