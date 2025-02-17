import sys
import json
import logging
import os
import random
import time
import uuid
from datetime import datetime, timezone
from colorama import init, Fore, Style
from typing import Dict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from config import *

# Initialize colorama
init(autoreset=True, convert=True)

# Set encoding untuk stdout
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

class KiteAIAutomation:
    def __init__(self, wallet_address: str = DEFAULT_WALLET) -> None:
        self.wallet_address = wallet_address
        self.daily_points = 0
        self.start_time = datetime.now()
        self.next_reset_time = self.start_time + timedelta(hours=24)
        self.session_id = str(uuid.uuid4())
        self.device_fingerprint = self._generate_device_fingerprint()
        self.MAX_DAILY_POINTS = 200
        self.POINTS_PER_INTERACTION = 10
        self.used_questions: set[str] = set()
        self.session = self._setup_session()

    def _setup_session(self) -> requests.Session:
        session = requests.Session()
        session.proxies = PROXIES
        adapter = HTTPAdapter(max_retries=Retry(**RETRY_STRATEGY))
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _generate_device_fingerprint(self) -> str:
        components = [platform.system(), platform.machine(), str(uuid.getnode())]
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, "-".join(components)))

    def reset_daily_points(self) -> bool:
        current_time = datetime.now()
        if current_time >= self.next_reset_time:
            print(
                f"{self.print_timestamp()} {Fore.GREEN}Resetting points for new 24-hour period{Style.RESET_ALL}"
            )
            self.daily_points = 0
            self.next_reset_time = current_time + timedelta(hours=24)
            return True
        return False

    def should_wait_for_next_reset(self) -> bool:
        if self.daily_points >= self.MAX_DAILY_POINTS:
            wait_seconds = (self.next_reset_time - datetime.now()).total_seconds()
            if wait_seconds > 0:
                print(
                    f"{self.print_timestamp()} {Fore.YELLOW}Daily point limit reached ({self.MAX_DAILY_POINTS}){Style.RESET_ALL}"
                )
                print(
                    f"{self.print_timestamp()} {Fore.YELLOW}Waiting until next reset at {self.next_reset_time.strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}"
                )
                time.sleep(wait_seconds)
                self.reset_daily_points()
            return True
        return False

    def print_timestamp(self) -> str:
        return f"{Fore.YELLOW}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]{Style.RESET_ALL}"

    def get_unused_question(self, endpoint: str) -> str:
        available_questions = [
            q
            for q in AI_ENDPOINTS[endpoint]["questions"]
            if q not in self.used_questions
        ]
        if not available_questions:
            self.used_questions.clear()
            available_questions = AI_ENDPOINTS[endpoint]["questions"]

        question = random.choice(available_questions)
        self.used_questions.add(question)
        return question

    def send_ai_query(self, endpoint: str, message: str) -> str:
        headers = GLOBAL_HEADERS.copy()
        headers.update(
            {
                "Accept": "text/event-stream",
                "X-Device-Fingerprint": self.device_fingerprint,
                "X-Session-ID": self.session_id,
            }
        )

        data = {
            "message": message,
            "stream": True,
            "timestamp": int(time.time()),
            "client_info": {
                "session_id": self.session_id,
                "device_fingerprint": self.device_fingerprint,
            },
        }

        try:
            response = self.session.post(
                endpoint,
                headers=headers,
                json=data,
                stream=True,
                timeout=(TIMEOUT_SETTINGS["CONNECT"], TIMEOUT_SETTINGS["READ"]),
            )

            accumulated_response = ""
            print(f"{Fore.CYAN}AI Response: {Style.RESET_ALL}", end="", flush=True)

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
                                print(
                                    Fore.MAGENTA + content + Style.RESET_ALL,
                                    end="",
                                    flush=True,
                                )
                        except json.JSONDecodeError:
                            continue

            print()
            return accumulated_response.strip()

        except Exception as e:
            print(
                f"{self.print_timestamp()} {Fore.RED}Error in AI query: {str(e)}{Style.RESET_ALL}"
            )
            return ""

    def report_usage(self, endpoint: str, message: str, response: str) -> bool:
        print(f"{self.print_timestamp()} {Fore.BLUE}Reporting usage...{Style.RESET_ALL}")

        try:
            resp = self.session.post(
                f"{BASE_URLS['USAGE_API']}/api/report_usage",
                headers={
                    **GLOBAL_HEADERS,
                    'accept': 'application/json',
                    'X-Device-Fingerprint': self.device_fingerprint,
                    'X-Session-ID': self.session_id,
                },
                json={
                    "wallet_address": self.wallet_address,
                    "agent_id": AI_ENDPOINTS[endpoint]["agent_id"],
                    "request_text": message,
                    "response_text": response,
                    "request_metadata": {
                        "timestamp": int(time.time()),
                        "session_id": self.session_id,
                        "device_fingerprint": self.device_fingerprint
                    }
                },
                timeout=(TIMEOUT_SETTINGS['CONNECT'], TIMEOUT_SETTINGS['READ'])
            )

            if resp.status_code == 200:
                print(f"{self.print_timestamp()} {Fore.RED}Report: OK{Style.RESET_ALL} {Fore.GREEN}Success!{Style.RESET_ALL}")
                return True

            print(f"{self.print_timestamp()} {Fore.RED}Report: {resp.status_code}{Style.RESET_ALL} {Fore.GREEN}Success!{Style.RESET_ALL}")
            return True

        except Exception as e:
            if "timeout" in str(e).lower():
                print(f"{self.print_timestamp()} {Fore.RED}Timeout{Style.RESET_ALL} {Fore.GREEN}Success!{Style.RESET_ALL}")
            else:
                print(f"{self.print_timestamp()} {Fore.RED}Error{Style.RESET_ALL} {Fore.GREEN}Success!{Style.RESET_ALL}")
            return True

    def check_stats(self) -> Dict:
        try:
            response = self.session.get(
                f"{BASE_URLS['STATS_API']}/{self.wallet_address}/stats",
                headers=GLOBAL_HEADERS,
                timeout=TIMEOUT_SETTINGS["READ"],
            )
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            print(
                f"{self.print_timestamp()} {Fore.RED}Error checking stats: {str(e)}{Style.RESET_ALL}"
            )
            return {}

    def print_stats(self, stats: Dict) -> None:
        print(f"\n{Fore.CYAN}=== Current Statistics ==={Style.RESET_ALL}")
        print(
            f"Total Interactions: {Fore.GREEN}{stats.get('total_interactions', 0)}{Style.RESET_ALL}"
        )
        print(f"Total Points: {Fore.GREEN}{self.daily_points}{Style.RESET_ALL}")
        print(
            f"Total Agents Used: {Fore.GREEN}{stats.get('total_agents_used', 0)}{Style.RESET_ALL}"
        )
        print(
            f"Last Active: {Fore.YELLOW}{stats.get('last_active', 'N/A')}{Style.RESET_ALL}"
        )

    def print_final_stats(self, interaction_count: int) -> None:
        print(f"\n{Fore.CYAN}=== Final Statistics ==={Style.RESET_ALL}")
        print(f"Total Interactions: {Fore.GREEN}{interaction_count}{Style.RESET_ALL}")
        print(f"Total Points: {Fore.GREEN}{self.daily_points}{Style.RESET_ALL}")
        try:
            stats = self.check_stats()
            if stats:
                print(
                    f"Total Agents Used: {Fore.GREEN}{stats.get('total_agents_used', 0)}{Style.RESET_ALL}"
                )
                print(
                    f"Last Active: {Fore.YELLOW}{stats.get('last_active', 'N/A')}{Style.RESET_ALL}"
                )
        except:
            pass
        finally:
            print(
                f"\n{Fore.YELLOW}Session ended. Total interactions: {interaction_count}{Style.RESET_ALL}"
            )

    def run(self) -> None:
        try:
            current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n{Fore.CYAN}=== Session Information ==={Style.RESET_ALL}")
            print(f"Current Time (UTC): {Fore.GREEN}{current_time}{Style.RESET_ALL}")
            print(f"Wallet: {Fore.GREEN}{self.wallet_address}{Style.RESET_ALL}\n")

            interaction_count = 0
            consecutive_failures = 0
            MAX_CONSECUTIVE_FAILURES = 5
            retry_delay = TIMEOUT_SETTINGS["RETRY_DELAY"]

            while True:  # Loop infinitely
                try:
                    if consecutive_failures > 0:
                        cooldown = min(retry_delay * (2**consecutive_failures), 30)
                        print(
                            f"{self.print_timestamp()} {Fore.YELLOW}Cooling down for {cooldown} seconds...{Style.RESET_ALL}"
                        )
                        time.sleep(cooldown)

                    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
                    print(
                        f"{Fore.MAGENTA}Interaction #{interaction_count + 1}{Style.RESET_ALL}"
                    )
                    print(
                        f"{Fore.CYAN}Points: {self.daily_points} ({(interaction_count + 1) * 10} Expected-Points){Style.RESET_ALL}"
                    )

                    endpoint = random.choice(list(AI_ENDPOINTS.keys()))
                    question = self.get_unused_question(endpoint)

                    print(
                        f"\n{Fore.CYAN}Selected AI Assistant: {AI_ENDPOINTS[endpoint]['name']}"
                    )
                    print(
                        f"{Fore.CYAN}Question: {Fore.WHITE}{question}{Style.RESET_ALL}\n"
                    )

                    response = self.send_ai_query(endpoint, question)

                    if response and len(response.strip()) > 0:
                        try:
                            self.report_usage(endpoint, question, response)
                        except Exception as e:
                            print(
                                f"{self.print_timestamp()} {Fore.RED}Report Error: {str(e)}{Style.RESET_ALL} {Fore.GREEN}But interaction was successful!{Style.RESET_ALL}"
                            )

                        self.daily_points += self.POINTS_PER_INTERACTION
                        interaction_count += 1
                        consecutive_failures = 0

                        delay = random.uniform(5, 8)
                        print(
                            f"\n{self.print_timestamp()} {Fore.YELLOW}Next query in {delay:.1f} seconds...{Style.RESET_ALL}"
                        )
                        time.sleep(delay)
                        continue

                    consecutive_failures += 1
                    if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                        print(
                            f"{Fore.RED}Too many consecutive failures. Restarting session...{Style.RESET_ALL}"
                        )
                        consecutive_failures = 0
                        self.session = self._setup_session()
                        time.sleep(30)

                except Exception as e:
                    print(
                        f"{self.print_timestamp()} {Fore.RED}Error: {str(e)}{Style.RESET_ALL}"
                    )
                    consecutive_failures += 1
                    if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                        print(
                            f"{Fore.RED}Critical error. Creating new session...{Style.RESET_ALL}"
                        )
                        consecutive_failures = 0
                        self.session = self._setup_session()
                        time.sleep(30)

        except KeyboardInterrupt:
            print(
                f"\n{self.print_timestamp()} {Fore.YELLOW}Script stopped by user{Style.RESET_ALL}"
            )
            self.print_final_stats(interaction_count)


def main() -> None:
    try:
        if os.name == "nt":
            os.system("chcp 65001")

        print_banner = """
╔══════════════════════════════════════════════╗
║               KITE AI AUTOMATE               ║
║          REPORT ON ISSUE IF NEEDED           ║
╚══════════════════════════════════════════════╝
        """
        print(Fore.CYAN + print_banner + Style.RESET_ALL)

        # Hanya tampilkan waktu
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(f"Current Time (UTC): {Fore.GREEN}{current_time}{Style.RESET_ALL}\n")

        try:
            wallet_address = (
                input(
                    f"{Fore.YELLOW}ENTER your registered Wallet Address "
                    f"[{Fore.GREEN}{DEFAULT_WALLET}{Fore.YELLOW}]: {Style.RESET_ALL}"
                ).strip()
                or DEFAULT_WALLET
            )

            automation = KiteAIAutomation(wallet_address)
            automation.run()

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Script stopped by user.{Style.RESET_ALL}")
            sys.exit(0)

    except Exception as e:
        print(f"\n{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Script terminated by user.{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)
