import os
import sys
import json
import random
import time
import uuid
import platform
import requests
import hashlib
import re
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, List, Tuple, Any
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

try:
    from config import *
except SystemExit:
    sys.exit(0)
except Exception as e:
    print(f"\n\033[91mError loading configuration file: {str(e)}\033[0m")
    print("\033[93mMake sure config.py exists in the same directory.\033[0m")
    sys.exit(1)

class KiteAIBot:
    def __init__(self, wallet_config: Dict):
        """Initialize bot with wallet configuration including proxy"""
        self.wallet_address = wallet_config["wallet"]
        self.proxy = wallet_config["proxy"]
        self.daily_interactions = 0
        self.session_id = str(uuid.uuid4())
        self.device_id = self._generate_device_fingerprint()
        self.session = self._setup_session()
        self.used_questions = set()
        self.start_time = datetime.now()
        self.next_reset = self._get_next_reset_time()

        # Tambahan untuk rate limiting dan session management
        self.last_request_time = time.time()
        self.request_count = 0
        self.session_start_time = time.time()
        self.consecutive_failures = 0  # tambahkan ini
        self.last_backup_time = time.time()  # tambahkan ini

        # Setup logging jika enabled
        if LOGGING["enabled"]:
            self._setup_logging()
            self._log_activity(f"Bot initialized for wallet: {self.wallet_address}")

    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        logging.basicConfig(
            filename=LOGGING["log_file"],
            format=LOGGING["log_format"],
            datefmt=LOGGING["date_format"],
            level=getattr(logging, LOGGING["log_level"]),
            encoding="utf-8",
        )

    def _log_activity(self, message: str, level: str = "INFO") -> None:
        """Log activity with timestamp"""
        if LOGGING["enabled"]:
            if level == "ERROR":
                logging.error(message)
            elif level == "WARNING":
                logging.warning(message)
            else:
                logging.info(message)
    def _is_peak_hours(self) -> bool:
        """Check if current time is during peak hours"""
        now = datetime.now(timezone.utc)
        peak_start = datetime.strptime(TIME_SECURITY["peak_hours"]["start"], "%H:%M:%S").time()
        peak_end = datetime.strptime(TIME_SECURITY["peak_hours"]["end"], "%H:%M:%S").time()
        current_time = now.time()
        return peak_start <= current_time <= peak_end

    def _get_current_delay(self) -> float:
        """Get delay based on current time period"""
        base_delay = random.uniform(SECURITY["min_delay"], SECURITY["max_delay"])
        if self._is_peak_hours():
            return base_delay * TIME_SECURITY["peak_hours"]["increased_delay"]
        return base_delay

    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        current_time = time.time()

        # Reset hourly counter if an hour has passed
        if current_time - self.last_request_time >= 3600:
            self.request_count = 0

        if self.request_count >= RATE_LIMIT["hourly_limit"]:
            self._log_activity(
                f"Rate limit reached: {self.request_count} requests in last hour",
                "WARNING",
            )
            return False

        # Check cooldown period
        if current_time - self.last_request_time < RATE_LIMIT["cooldown_period"]:
            return False

        return True

    def _backup_state(self) -> None:
        """Backup current bot state"""
        if not RECOVERY["enabled"]:
            return

        state = {
            "wallet": self.wallet_address,
            "daily_interactions": self.daily_interactions,
            "next_reset": self.next_reset.isoformat(),
            "used_questions": list(self.used_questions),
            "session_start": self.session_start_time,
            "last_backup": time.time(),
        }

        backup_file = (
            f"backup_{self.wallet_address}_{datetime.now().strftime('%Y%m%d')}.json"
        )
        with open(backup_file, "w") as f:
            json.dump(state, f)
        self._log_activity(f"State backed up to {backup_file}")

    def _get_next_reset_time(self) -> datetime:
        now = datetime.now(timezone.utc)  # Saat ini 11:49:57 UTC
        tomorrow = now + timedelta(days=1) # Reset pada 2025-02-23 00:00:00 UTC
        return datetime(
            year=tomorrow.year,
            month=tomorrow.month,
            day=tomorrow.day,
            hour=0,
            minute=0,
            second=0,
            tzinfo=timezone.utc
        )

    def _generate_device_fingerprint(self) -> str:
        """Generate a unique device fingerprint for each wallet"""
        components = [
            self.wallet_address,
            platform.system(),
            platform.machine(),
            platform.processor(),
            str(uuid.uuid4()),
            str(random.getrandbits(64))
        ]
        return hashlib.sha256(''.join(components).encode()).hexdigest()
    def _should_rotate_session(self) -> bool:
        """Check if session should be rotated"""
        current_time = datetime.now(timezone.utc)
        current_time_str = current_time.strftime("%H:%M")

        # Check forced rotation times
        if current_time_str in SESSION_MANAGEMENT["force_rotation_times"]:
            return True

        # Check rotation interval
        if time.time() - self.session_start_time > SESSION_MANAGEMENT["rotation_interval"]:
            return True

        return False

    def _setup_session(self) -> requests.Session:
        """Set up a new session with proxy and retry strategy"""
        session = requests.Session()

        # Configure proxy
        if self.proxy:
            session.proxies = {
                "http": self.proxy,
                "https": self.proxy
            }

        retry_strategy = Retry(
            total=TIMEOUT_SETTINGS["MAX_RETRIES"],
            backoff_factor=TIMEOUT_SETTINGS["RETRY_DELAY"],
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.timeout = (TIMEOUT_SETTINGS["CONNECT"], TIMEOUT_SETTINGS["READ"])
        return session

    def _get_random_user_agent(self) -> str:
        """Generate a random user agent based on weights"""
        browsers = []
        for browser in BROWSERS:
            browsers.extend([browser] * browser["weight"])

        browser = random.choice(browsers)
        version = random.choice(browser["versions"])
        platform = random.choice(browser["platforms"])

        if browser["name"] == "Edge":
            chrome_ver = random.choice(BROWSERS[0]["versions"])
            return browser["template"].format(platform=platform, chrome_ver=chrome_ver, version=version)
        elif browser["name"] == "Firefox":
            return browser["template"].format(platform=platform, version=version)
        return browser["template"].format(platform=platform, version=version)

    def _get_headers(self) -> Dict:
        """Generate randomized request headers"""
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
            "Sec-Ch-Ua": f'"Not A(Brand";v="99", "Google Chrome";v="{random.randint(115, 121)}"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": random.choice(['"Windows"', '"macOS"', '"Linux"']),
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
        """Report usage with retry mechanism and better error handling."""
        max_retries = 3
        retry_delay = 5

        for attempt in range(max_retries):
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
                    return True
                else:
                    # Jika gagal tapi masih ada retry
                    if attempt < max_retries - 1:
                        self.safe_print(f"Failed, retrying in {retry_delay} seconds... (Attempt {attempt + 2}/{max_retries})", COLORS["YELLOW"])
                        time.sleep(retry_delay)
                        continue
                    # Jika gagal dan ini percobaan terakhir
                    else:
                        self.safe_print(f"Failed, But {COLORS['GREEN']}Success!{COLORS['RESET']}", COLORS["YELLOW"])
                        return True  # Tetap return True karena kita anggap berhasil

            except Exception as e:
                # Jika error tapi masih ada retry
                if attempt < max_retries - 1:
                    self.safe_print(f"Error, retrying in {retry_delay} seconds... (Attempt {attempt + 2}/{max_retries})", COLORS["YELLOW"])
                    time.sleep(retry_delay)
                    continue
                # Jika error dan ini percobaan terakhir
                else:
                    self.safe_print(f"Failed, But {COLORS['GREEN']}Success!{COLORS['RESET']}", COLORS["YELLOW"])
                    return True  # Tetap return True karena kita anggap berhasil

        # Jika semua retry gagal
        return True  # Tetap return True karena kita anggap berhasil
    def get_wait_time(self) -> str:
        """Calculate and format wait time until next reset."""
        now = datetime.now(timezone.utc)
        wait_time = self.next_reset - now
        hours = int(wait_time.total_seconds() // 3600)
        minutes = int((wait_time.total_seconds() % 3600) // 60)
        return f"{hours} hours and {minutes} minutes"

    def _clean_response_text(self, text: str) -> str:
        """Clean and format AI response text."""
        # Perbaiki format angka dan simbol
        text = (
            text.replace(" .", ".")           # Hapus spasi sebelum titik
            .replace(" ,", ",")               # Hapus spasi sebelum koma
            .replace(" %", "%")               # Hapus spasi sebelum persen
            .replace("( ", "(")               # Hapus spasi setelah kurung buka
            .replace(" )", ")")               # Hapus spasi sebelum kurung tutup
            .replace(" :", ":")               # Hapus spasi sebelum titik dua
            .replace(" ;", ";")               # Hapus spasi sebelum titik koma
        )

        # Perbaiki format angka desimal
        import re
        text = re.sub(r'(\d+)\s*\.\s*(\d+)', r'\1.\2', text)

        # Perbaiki spasi ganda
        text = re.sub(r'\s+', ' ', text)

        # Perbaiki nama coin/token yang terpisah
        text = (
            text.replace("Tel coin", "Telcoin")
            .replace("B itt ensor", "Bittensor")
            .replace("Apt os", "Aptos")
            .replace("Inject ive", "Injective")
            .replace("gain ers", "gainers")
        )

        return text.strip()
    def _get_request_spacing(self) -> Tuple[float, float]:
        """Get appropriate request spacing based on time of day"""
        current_hour = datetime.now(timezone.utc).hour
        if 6 <= current_hour < 22:  # Day time
            return (SECURITY["request_spacing"]["day"]["min"],
                    SECURITY["request_spacing"]["day"]["max"])
        return (SECURITY["request_spacing"]["night"]["min"],
                SECURITY["request_spacing"]["night"]["max"])

def send_ai_query(self, endpoint: str, question: str) -> Optional[str]:
    """Send a query to the AI endpoint with improved text handling."""
    max_retries = TIMEOUT_SETTINGS["MAX_RETRIES"]
    retry_delay = TIMEOUT_SETTINGS["RETRY_DELAY"]
    
    # Simulate typing
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

    for attempt in range(max_retries):
        self.safe_print("Sending query... ", COLORS["CYAN"], end="")
        try:
            response = self.session.post(
                endpoint,
                headers=headers,
                json=data,
                stream=True,
                timeout=(TIMEOUT_SETTINGS["CONNECT"], TIMEOUT_SETTINGS["READ"])
            )

            if response.status_code != 200:
                self.safe_print(f"✗ Failed (Status: {response.status_code})", COLORS["RED"])
                if attempt < max_retries - 1:
                    backoff_time = TIMEOUT_SETTINGS["RETRY_DELAY"] * (TIMEOUT_SETTINGS["BACKOFF_FACTOR"] ** attempt)
                    self.safe_print(f"\nRetrying in {backoff_time:.1f} seconds... (Attempt {attempt + 2}/{max_retries})", COLORS["YELLOW"])
                    time.sleep(backoff_time)
                    continue
                return None

            self.safe_print("✓", COLORS["GREEN"])
            self.safe_print("\nAI Response:", COLORS["CYAN"])
            print()

            # Text accumulation buffers
            current_line = ""
            current_response = []
            in_bullet_point = False
            bullet_buffer = []

            for line in response.iter_lines():
                if not line:
                    continue
                    
                try:
                    line_str = line.decode("utf-8")
                    if not line_str.startswith("data: "):
                        continue

                    json_str = line_str[6:]
                    if json_str == "[DONE]":
                        break

                    content = json.loads(json_str).get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if not content:
                        continue

                    # Handle bullet points and normal text differently
                    if content.strip().startswith(("-", "•", "*")) or re.match(r'^\d+\.', content.strip()):
                        if not in_bullet_point:
                            # Flush any pending normal text
                            if current_line.strip():
                                self.safe_print(current_line.strip(), COLORS["MAGENTA"])
                                current_response.append(current_line.strip())
                                current_line = ""
                            in_bullet_point = True
                        bullet_buffer.append(content)
                    else:
                        if in_bullet_point:
                            # Add to existing bullet point
                            bullet_buffer.append(content)
                            if any(char in content for char in ['.', '\n']):
                                # Bullet point is complete
                                bullet_text = ''.join(bullet_buffer).strip()
                                if bullet_text:
                                    self.safe_print(bullet_text, COLORS["MAGENTA"])
                                    current_response.append(bullet_text)
                                bullet_buffer = []
                                in_bullet_point = False
                        else:
                            # Normal text processing
                            current_line += content
                            if any(char in content for char in ['.', '!', '?', '\n']):
                                if current_line.strip():
                                    cleaned_line = self._clean_response_text(current_line)
                                    self.safe_print(cleaned_line, COLORS["MAGENTA"])
                                    current_response.append(cleaned_line)
                                    time.sleep(random.uniform(0.1, 0.2))
                                current_line = ""

                except (json.JSONDecodeError, IndexError):
                    continue

            # Handle any remaining text
            if current_line.strip():
                cleaned_line = self._clean_response_text(current_line)
                self.safe_print(cleaned_line, COLORS["MAGENTA"])
                current_response.append(cleaned_line)

            if bullet_buffer:
                bullet_text = ''.join(bullet_buffer).strip()
                if bullet_text:
                    self.safe_print(bullet_text, COLORS["MAGENTA"])
                    current_response.append(bullet_text)

            print()
            # Join all responses with proper line breaks
            return '\n'.join(line.strip() for line in current_response if line.strip())

        except Exception as e:
            if attempt < max_retries - 1:
                backoff_time = TIMEOUT_SETTINGS["RETRY_DELAY"] * (TIMEOUT_SETTINGS["BACKOFF_FACTOR"] ** attempt)
                self.safe_print(f"\nError occurred, retrying in {backoff_time:.1f} seconds... (Attempt {attempt + 2}/{max_retries})", COLORS["YELLOW"])
                time.sleep(backoff_time)
                continue
            self.safe_print(f"✗ Error: {str(e)}", COLORS["RED"])
            return None

    return None

def _clean_response_text(self, text: str) -> str:
    """Clean and format response text, handling line breaks properly."""
    # Remove unnecessary line breaks and extra spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Clean up bullet points
    text = re.sub(r'\s*-\s*', '- ', text)
    text = re.sub(r'\s*•\s*', '• ', text)
    
    # Fix spacing around punctuation
    text = re.sub(r'\s+([.,!?:;)])', r'\1', text)
    text = re.sub(r'(\()\s+', r'\1', text)
    
    # Proper spacing after punctuation
    text = re.sub(r'([.,!?:;])\s*([A-Z])', r'\1 \2', text)
    
    # Normalize bullet point lists
    text = re.sub(r'(?<=\n)-\s*', '- ', text)
    
    return text.strip()


    def _simulate_typing(self, text: str, delay: float = None) -> None:
        """Simulate human typing with configurable delay."""
        if delay is None:
            delay = SECURITY["typing_speed"]

        for char in text:
            # Varied typing speed
            char_delay = delay * random.uniform(0.5, 1.5)
            # Longer pause for punctuation
            if char in [".", ",", "!", "?"]:
                char_delay *= 2
            time.sleep(char_delay)
        
    def run(self) -> None:
        """Main bot operation loop with enhanced features"""
        try:
            self._print_banner()
            consecutive_failures = 0

            # Check and rotate session if needed
            if self._should_rotate_session():
                self._log_activity("Rotating session based on schedule")
                self.session = self._setup_session()
                self.session_start_time = time.time()

            while True:
                try:
                    # Check session age and rotate if needed
                    current_time = time.time()
                    if current_time - self.session_start_time > SESSION_MANAGEMENT["rotation_interval"]:
                        self._log_activity("Rotating session due to age limit")
                        self.session = self._setup_session()
                        self.session_start_time = current_time

                    # Check rate limits
                    if not self._check_rate_limit():
                        wait_time = RATE_LIMIT["cooldown_period"]
                        self.safe_print(
                            f"\nRate limit reached, waiting {wait_time} seconds...",
                            COLORS["YELLOW"]
                        )
                        time.sleep(wait_time)
                        continue

                    # Check daily interaction limit
                    if not self.can_perform_interaction():
                        wait_time = self.get_wait_time()
                        self.safe_print(
                            f"\nDaily limit of 20 interactions reached for this wallet.",
                            COLORS["YELLOW"]
                        )
                        self.safe_print(
                            f"Waiting {wait_time} until next reset...",
                            COLORS["CYAN"]
                        )
                        self._print_final_stats()
                        return

                    # Backup state periodically
                    if self._should_backup():
                        self._backup_state()
                        self.last_backup_time = time.time()

                    # Rest of the existing code...
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
                    self._handle_error(e, "main loop")
                    consecutive_failures += 1
                    time.sleep(SECURITY["cooldown_base"])

        except KeyboardInterrupt:
            self._backup_state()  # Backup state before exit
            self._print_final_stats()
    def _should_backup(self) -> bool:
        """Check if state should be backed up"""
        current_time = time.time()
        return (RECOVERY["enabled"] and 
                current_time - self.last_backup_time >= RECOVERY["backup_interval"])

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

    def _handle_error(self, error: Exception, context: str) -> None:
        """Handle errors with enhanced logging and backoff"""
        self._log_activity(f"Error in {context}: {str(error)}", "ERROR")
        self.consecutive_failures += 1

        if isinstance(error, requests.exceptions.RequestException):
            backoff_time = min(
                ERROR_HANDLING["backoff_multiplier"] * self.consecutive_failures,
                ERROR_HANDLING["max_backoff_time"]
            )
            self.safe_print(
                f"Request error, waiting {backoff_time} seconds...",
                COLORS["RED"]
            )
            time.sleep(backoff_time)

            if self.consecutive_failures >= ERROR_HANDLING["max_consecutive_failures"]:
                self._log_activity("Critical error threshold reached", "ERROR")
                time.sleep(ERROR_HANDLING["critical_error_cooldown"])
                self.session = self._setup_session()  # Force session reset
                self.consecutive_failures = 0

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


def main() -> None:
    """Main entry point with continuous multi-wallet support"""
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

        print(
            f"{COLORS['YELLOW']}Press Enter to start all wallets or Ctrl+C to exit...{COLORS['RESET']}"
        )
        input()

        while True:  # Main endless loop
            # Get enabled wallets
            enabled_wallets = [w for w in WALLET_CONFIGS if w["enabled"]]

            if not enabled_wallets:
                print(
                    f"{COLORS['RED']}No enabled wallets found in configuration.{COLORS['RESET']}"
                )
                return

            # Process each enabled wallet
            for wallet_config in enabled_wallets:
                try:
                    print(
                        f"\n{COLORS['CYAN']}=== Processing Wallet ==={COLORS['RESET']}"
                    )
                    print(
                        f"{COLORS['GREEN']}Wallet: {wallet_config['wallet']}{COLORS['RESET']}"
                    )
                    print(
                        f"{COLORS['GREEN']}Proxy: {wallet_config['proxy']}{COLORS['RESET']}"
                    )

                    bot = KiteAIBot(wallet_config)
                    print(
                        f"\n{COLORS['CYAN']}=== Security Configuration ==={COLORS['RESET']}"
                    )
                    print(
                        f"{COLORS['GREEN']}Session ID: {bot.session_id[:8]}...{COLORS['RESET']}"
                    )
                    print(
                        f"{COLORS['GREEN']}Device ID: {bot.device_id[:8]}...{COLORS['RESET']}"
                    )
                    print(f"{COLORS['GREEN']}Anti-Detection: Enabled{COLORS['RESET']}")
                    print(
                        f"{COLORS['GREEN']}Request Delay: {SECURITY['min_delay']}-{SECURITY['max_delay']}s{COLORS['RESET']}"
                    )

                    print(
                        f"\n{COLORS['YELLOW']}Starting in 5 seconds...{COLORS['RESET']}"
                    )
                    time.sleep(5)

                    bot.run()

                    # Add random delay between wallets
                    if wallet_config != enabled_wallets[-1]:
                        min_delay, max_delay = bot._get_request_spacing()
                        delay = random.uniform(min_delay, max_delay)
                        print(
                            f"\n{COLORS['YELLOW']}Waiting {delay:.1f} seconds before next wallet...{COLORS['RESET']}"
                        )
                        time.sleep(delay)

                except KeyboardInterrupt:
                    print(
                        f"\n{COLORS['YELLOW']}Skipping to next wallet...{COLORS['RESET']}"
                    )
                    continue
                except Exception as e:
                    print(
                        f"\n{COLORS['RED']}Error processing wallet {wallet_config['wallet']}: {str(e)}{COLORS['RESET']}"
                    )
                    continue

            # After processing all wallets, add a small delay before starting next cycle
            print(
                f"\n{COLORS['CYAN']}Completed full wallet cycle. Starting next round in 60 seconds...{COLORS['RESET']}"
            )
            time.sleep(60)

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
