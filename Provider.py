#!/usr/bin/env python3
"""
SmsBomber - Provider Handler Engine
Manages API configurations, request headers, payload serialization, and response verification.
"""

import copy
import json
import random
import urllib3
import requests

DEFAULT_TIMEOUT = 15
VERIFY_SSL = True

if not VERIFY_SSL:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36"
]

def load_providers(config_path="config.json"):
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f).get("providers", {})

PROVIDERS = load_providers()


class Provider:
    def __init__(self, target, proxy=None, verbose=False, cc="91", timeout=DEFAULT_TIMEOUT, config=None, dry_run=False):
        if config:
            self.config = config
        else:
            provider_pool = PROVIDERS.get(cc, PROVIDERS.get("multi", []))
            if not provider_pool:
                provider_pool = PROVIDERS.get("multi", [])
            self.config = random.choice(provider_pool)

        self.target = str(target).strip()
        self.cc = str(cc).strip()
        self.proxy = proxy if proxy else None
        self.verbose = verbose
        self.timeout = timeout
        self.dry_run = dry_run
        self.headers = self._headers()
        self.resp = None
        self.done = False

    def _headers(self):
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive"
        }
        if "headers" in self.config and isinstance(self.config["headers"], dict):
            headers.update(self.config["headers"])
        return headers

    def _prepare_data(self):
        # Deep copy to prevent mutating the shared config across threads
        data = copy.deepcopy(self.config.get("data", {}))
        
        if "cc_target" in self.config:
            cc_field = self.config["cc_target"]
            current_val = str(data.get(cc_field, ""))
            data[cc_field] = current_val + self.cc

        if "target_param" in self.config:
            target_field = self.config["target_param"]
            current_target = str(data.get(target_field, ""))
            data[target_field] = current_target + self.target

        return data

    def _get(self):
        url = self.config["url"].strip() + self.target
        if "cc_target" in self.config:
            sep = "&" if "?" in url else "?"
            url += f"{sep}{self.config['cc_target']}={self.cc}"
        return requests.get(
            url,
            headers=self.headers,
            timeout=self.timeout,
            proxies=self.proxy,
            verify=VERIFY_SSL
        )

    def _post(self):
        data = self._prepare_data()
        url = self.config["url"].strip()
        is_json = self.config.get("data_type", "").lower() == "json"

        if is_json:
            return requests.post(
                url,
                json=data,
                headers=self.headers,
                timeout=self.timeout,
                proxies=self.proxy,
                verify=VERIFY_SSL
            )
        else:
            return requests.post(
                url,
                data=data,
                headers=self.headers,
                timeout=self.timeout,
                proxies=self.proxy,
                verify=VERIFY_SSL
            )

    def start(self):
        if self.dry_run:
            self.done = True
            return

        method = self.config.get("method", "GET").upper()
        try:
            if method == "GET":
                self.resp = self._get()
            elif method == "POST":
                self.resp = self._post()
        finally:
            self.done = True

    def status(self):
        name = self.config.get("name", "Unknown")
        if self.dry_run:
            if self.verbose:
                print(f"[DRY-RUN] {name:<14} -> Simulated Dispatch")
            return True

        if self.resp is None:
            if self.verbose:
                print(f"[FAILED]  {name:<14} -> No response")
            return False

        identifier = str(self.config.get("identifier", ""))
        resp_text = self.resp.text
        is_success = (identifier in resp_text) or (self.resp.status_code in (200, 201, 202) and identifier.lower() in ("200", "true", "sent", "success"))

        if is_success:
            if self.verbose:
                print(f"\033[1;32m[SUCCESS]\033[0m {name:<14} -> HTTP {self.resp.status_code}")
            return True
        else:
            if self.verbose:
                print(f"\033[1;31m[FAILED]\033[0m  {name:<14} -> HTTP {self.resp.status_code}")
            return False
