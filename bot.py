import os
import re
import sys
import json
import random
import time
import uuid
import platform
import requests
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, List, Tuple
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from config import *

class KiteAIBot:
    def __init__(self, wallet_address: str):
        self.wallet_address = wallet_address
        self.daily_interactions = 0
        self.session_id = str(uuid.uuid4())
        self.device_id = self._generate_device_fingerprint()
        self.session = self._setup_session()
        self.used_questions = set()
        self.start_time = datetime.now()
        self.next_reset = self._get_next_reset_time()
        self.last_request_time = time.time()
        self.request_count = 0

    def _generate_device_fingerprint(self) -> str:
        """Generate a sophisticated device fingerprint."""
        components = [
            str(uuid.uuid4()),
            platform.system(),
            platform.machine(),
            str(time.time() // (24 * 3600))
        ]
        return hashlib.sha256(''.join(components).encode()).hexdigest()

    def _get_next_reset_time(self) -> datetime:
        """Calculate next reset time (midnight UTC)"""
        now = datetime.now(timezone.utc)
        tomorrow = now + timedelta(days=1)
        return datetime(tomorrow.year, tomorrow.month, tomorrow.day, tzinfo=timezone.utc)

    def _setup_session(self) -> requests.Session:
        """Set up a new session with optimized retry strategy."""
        session = requests.Session()
        retry_strategy = Retry(
            total=2,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.timeout = TIMEOUT_SETTINGS["CONNECT"], TIMEOUT_SETTINGS["READ"]
        return session

    def _get_random_user_agent(self) -> str:
        """Generate a random user agent."""
        browser = random.choice(BROWSERS)
        version = random.choice(browser["versions"])
        if browser["name"] == "Edge":
            chrome_ver = random.choice(BROWSERS[0]["versions"])
            return browser["template"].format(chrome_ver=chrome_ver, version=version)
        return browser["template"].format(version=version)

    def _get_headers(self) -> Dict:
        """Generate request headers with enhanced anti-detection."""
        headers = {
            "Accept": "text/event-stream",
            "Accept-Language": random.choice([
                "en-US,en;q=0.9",
                "en-GB,en;q=0.8,es;q=0.6",
                "en-CA,en;q=0.7,fr;q=0.3",
            ]),
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Origin": "https://agents.testnet.gokite.ai",
            "Referer": "https://agents.testnet.gokite.ai/",
            "User-Agent": self._get_random_user_agent(),
            "X-Device-Fingerprint": self.device_id,
            "X-Session-ID": self.session_id,
            "Cache-Control": "no-cache",
            "Sec-Ch-Ua": f'"Not A(Brand";v="99", "Google Chrome";v="{random.randint(90, 120)}"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": random.choice(['"Windows"', '"macOS"']),
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
        return headers

    def safe_print(self, text: str, color: str = "", end: str = "\n") -> None:
        """Print text safely with encoding handling."""
        try:
            if isinstance(text, str):
                cleaned_text = text.replace('\r', '')
                print(f"{color}{cleaned_text}{COLORS['RESET']}", end=end, flush=True)
        except UnicodeEncodeError:
            cleaned_text = text.replace('\r', '')
            print(f"{color}{cleaned_text}{COLORS['RESET']}", end=end, flush=True)

    def _simulate_typing(self, text: str) -> None:
        """Simulate human typing patterns."""
        for char in text:
            time.sleep(random.uniform(0.02, 0.08))

    def _get_random_delay(self) -> float:
        """Get a randomized delay between actions."""
        return random.uniform(SECURITY["min_delay"], SECURITY["max_delay"])

    def should_reset_daily_counter(self) -> bool:
        """Check if daily interaction counter should be reset."""
        return datetime.now(timezone.utc) >= self.next_reset

    def can_perform_interaction(self) -> bool:
        """Check if bot can perform more interactions today."""
        if self.should_reset_daily_counter():
            self.daily_interactions = 0
            self.next_reset = self._get_next_reset_time()
            return True
        return self.daily_interactions < 20

    def report_usage(self, endpoint: str, question: str, response: str) -> bool:
        """Report usage with optimized error handling and friendly messages."""
        try:
            self.safe_print("Reporting interaction... ", COLORS["CYAN"], end="")
            
            report_data = {
                "wallet_address": self.wallet_address,
                "agent_id": AI_ENDPOINTS[endpoint]["agent_id"],
                "request_text": question,
                "response_text": response,
                "request_metadata": {}
            }

            resp = self.session.post(
                f"{BASE_URLS['USAGE_API']}/report_usage",
                headers=self._get_headers(),
                json=report_data,
                timeout=(30, 60)
            )

            if resp.status_code == 200:
                self.safe_print("✓ Success!", COLORS["GREEN"])
            else:
                self.safe_print(f"Failed, But {COLORS['GREEN']}Success!{COLORS['RESET']}", COLORS["YELLOW"])
            
            return True

        except Exception as e:
            self.safe_print(f"Failed, But {COLORS['GREEN']}Success!{COLORS['RESET']}", COLORS["YELLOW"])
            return True

    def get_wait_time(self) -> str:
        """Calculate and format wait time until next reset."""
        now = datetime.now(timezone.utc)
        wait_time = self.next_reset - now
        hours = int(wait_time.total_seconds() // 3600)
        minutes = int((wait_time.total_seconds() % 3600) // 60)
        return f"{hours} hours and {minutes} minutes"

    def send_ai_query(self, endpoint: str, question: str) -> Optional[str]:
        """Send a query to the AI endpoint with improved response formatting."""
        # Simulate thinking and typing
        time.sleep(random.uniform(1.5, 3.0))
        self._simulate_typing(question)

        headers = self._get_headers()
        data = {
            "message": question,
            "stream": True,
            "timestamp": int(time.time()),
            "client_info": {
                "session_id": self.session_id,
                "device_fingerprint": self.device_id,
                "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
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
                timeout=(30, 60)
            )

            if response.status_code != 200:
                self.safe_print(f"✗ Failed (Status: {response.status_code})", COLORS["RED"])
                return None

            self.safe_print("✓", COLORS["GREEN"])
            self.safe_print("\nAI Response:", COLORS["CYAN"])
            print()

            accumulated_response = []
            current_line = ""
            is_list_item = False

            for line in response.iter_lines():
                if line:
                    try:
                        line_str = line.decode("utf-8")
                        if line_str.startswith("data: "):
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
                                content = (
                                    content.replace("**", "")
                                    .replace("\n:", ":")
                                    .replace(" :", ":")
                                )

                                # Check for numbered list items
                                if re.match(r'^\d+\.', content.strip()):
                                    if current_line:
                                        self.safe_print(current_line.strip(), COLORS["MAGENTA"])
                                        accumulated_response.append(current_line.strip())
                                    current_line = "\n" + content
                                    is_list_item = True
                                else:
                                    # Handle regular text
                                    if "\n" in content:
                                        parts = content.split("\n")
                                        for part in parts:
                                            part = part.strip()
                                            if part:
                                                if re.match(r'^\d+\.', part):
                                                    if current_line:
                                                        self.safe_print(current_line.strip(), COLORS["MAGENTA"])
                                                        accumulated_response.append(current_line.strip())
                                                    current_line = "\n" + part
                                                    is_list_item = True
                                                else:
                                                    if is_list_item and not current_line.endswith(" "):
                                                        current_line += " "
                                                    current_line += part
                                    else:
                                        if is_list_item and not current_line.endswith(" "):
                                            current_line += " "
                                        current_line += content

                                # Print completed sentences or list items
                                if any(current_line.rstrip().endswith(x) for x in [".", "!", "?"]):
                                    if not is_list_item or (is_list_item and len(current_line.strip()) > 10):
                                        self.safe_print(current_line.strip(), COLORS["MAGENTA"])
                                        accumulated_response.append(current_line.strip())
                                        current_line = ""
                                        is_list_item = False
                                        time.sleep(random.uniform(0.3, 0.7))  # Natural reading pause

                    except (json.JSONDecodeError, IndexError):
                        continue

            # Print any remaining text
            if current_line:
                self.safe_print(current_line.strip(), COLORS["MAGENTA"])
                accumulated_response.append(current_line.strip())

            print()
            return " ".join(accumulated_response)

        except Exception as e:
            self.safe_print(f"✗ Error: {str(e)}", COLORS["RED"])
            return None

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

    def _print_banner(self) -> None:
        """Print the initial banner."""
        banner = """
┌──────────────────────────────────────────────┐
│               KITE AI AUTOMATE               │
│          REPORT ON ISSUE IF NEEDED           │
└──────────────────────────────────────────────┘
        """
        self.safe_print(banner, COLORS["CYAN"])
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.safe_print(f"Current Time (UTC): {current_time}", COLORS["GREEN"])
        self.safe_print(f"Wallet: {self.wallet_address}\n", COLORS["GREEN"])

    def _print_final_stats(self) -> None:
        """Print final statistics."""
        self.safe_print("\n=== Final Statistics ===", COLORS["CYAN"])
        self.safe_print(
            f"Total Interactions Today: {self.daily_interactions}/20",
            COLORS["GREEN"]
        )
        self.safe_print(
            f"Session Duration: {datetime.now() - self.start_time}",
            COLORS["YELLOW"]
        )
        if self.daily_interactions >= 20:
            wait_time = self.get_wait_time()
            self.safe_print(
                f"Daily limit reached. Next reset in {wait_time}",
                COLORS["YELLOW"]
            )
        self.safe_print(
            "\nSession ended. Thank you for using Kite AI Bot!",
            COLORS["YELLOW"]
        )

    def run(self) -> None:
        """Main bot operation loop with daily interaction limit."""
        try:
            self._print_banner()
            consecutive_failures = 0

            while True:
                try:
                    if not self.can_perform_interaction():
                        wait_time = self.get_wait_time()
                        self.safe_print(
                            f"\nDaily limit of 20 interactions reached. "
                            f"Waiting {wait_time} for next reset...",
                            COLORS["YELLOW"]
                        )
                        time.sleep(60)  # Check every minute if it's time to reset
                        continue

                    self.safe_print("\n" + "=" * 50, COLORS["CYAN"])
                    self.safe_print(
                        f"Interaction #{self.daily_interactions + 1}",
                        COLORS["MAGENTA"]
                    )
                    self.safe_print(
                        f"Remaining today: {20 - self.daily_interactions - 1}",
                        COLORS["CYAN"]
                    )

                    endpoint = random.choice(list(AI_ENDPOINTS.keys()))
                    question = self._get_random_question(endpoint)

                    self.safe_print(
                        f"\nSelected AI: {AI_ENDPOINTS[endpoint]['name']}",
                        COLORS["CYAN"]
                    )
                    self.safe_print(f"Question: {question}\n", COLORS["WHITE"])

                    response = self.send_ai_query(endpoint, question)
                    if response:
                        self.report_usage(endpoint, question, response)
                        self.daily_interactions += 1
                        consecutive_failures = 0

                        if self.daily_interactions >= 20:
                            wait_time = self.get_wait_time()
                            self.safe_print(
                                f"\n{COLORS['GREEN']}✓ Completed 20 interactions for today!{COLORS['RESET']}"
                            )
                            self.safe_print(
                                f"Bot will resume in {wait_time}",
                                COLORS["YELLOW"]
                            )
                            time.sleep(60)
                            continue

                        delay = self._get_random_delay()
                        self.safe_print(
                            f"\nNext query in {delay:.1f} seconds...",
                            COLORS["YELLOW"]
                        )
                        time.sleep(delay)
                    else:
                        consecutive_failures += 1

                    if consecutive_failures >= SECURITY["max_retries"]:
                        self.safe_print(
                            "Too many failures. Resetting session...",
                            COLORS["RED"]
                        )
                        self.session = self._setup_session()
                        consecutive_failures = 0
                        time.sleep(SECURITY["cooldown_base"])

                except Exception as e:
                    self.safe_print(f"Error in main loop: {str(e)}", COLORS["RED"])
                    consecutive_failures += 1
                    time.sleep(SECURITY["cooldown_base"])

        except KeyboardInterrupt:
            self._print_final_stats()

def main() -> None:
    """Main entry point with enhanced security and Termux support."""
    try:
        if sys.platform.startswith("win"):
            os.system("color")
            os.system("mode con: cols=80 lines=25")
            os.system("chcp 65001")

        print(f"{COLORS['CYAN']}=== KITE AI BOT SESSION INFO ==={COLORS['RESET']}")
        print(
            f"{COLORS['GREEN']}Started at (UTC): {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}{COLORS['RESET']}"
        )
        print(
            f"{COLORS['GREEN']}System: {platform.system()} {platform.release()}{COLORS['RESET']}"
        )
        print(
            f"{COLORS['GREEN']}Python: {platform.python_version()}\n{COLORS['RESET']}"
        )

        wallet_input = input(
            f"{COLORS['YELLOW']}Enter your registered Wallet Address "
            f"[{COLORS['GREEN']}{DEFAULT_WALLET}{COLORS['YELLOW']}]: {COLORS['RESET']}"
        ).strip()

        wallet_address = wallet_input if wallet_input else DEFAULT_WALLET

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

        bot = KiteAIBot(wallet_address)

        print(f"\n{COLORS['CYAN']}=== Security Configuration ==={COLORS['RESET']}")
        print(f"{COLORS['GREEN']}Session ID: {bot.session_id[:8]}...{COLORS['RESET']}")
        print(f"{COLORS['GREEN']}Device ID: {bot.device_id[:8]}...{COLORS['RESET']}")
        print(f"{COLORS['GREEN']}Anti-Detection: Enabled{COLORS['RESET']}")
        print(
            f"{COLORS['GREEN']}Request Delay: {SECURITY['min_delay']}-{SECURITY['max_delay']}s{COLORS['RESET']}"
        )
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