<div align="center">

# 🚀 SmsBomber
### *Automated API Resilience & Rate-Limiting Assessment Framework*

A multi-threaded Python security utility designed to test and audit the rate-limiting resilience, gateway throttling, and endpoint concurrency of SMS verification and OTP authentication endpoints.

[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Stars](https://img.shields.io/github/stars/cyb3rdr4g0n17/SmsBomber?style=for-the-badge&color=ffb703)](https://github.com/cyb3rdr4g0n17/SmsBomber/stargazers)
[![Forks](https://img.shields.io/github/forks/cyb3rdr4g0n17/SmsBomber?style=for-the-badge&color=00f5d4)](https://github.com/cyb3rdr4g0n17/SmsBomber/network/members)

[⚠️ Legal Disclaimer](#️-legal-disclaimer) • [✨ Key Features](#-features) • [🚀 Quick Start](#-quick-start) • [⌨️ CLI Reference](#️-command-line-options) • [🧩 Adding Providers](#-custom-provider-configuration)

---

</div>

> [!WARNING]
> ### ⚠️ LEGAL & ETHICAL DISCLAIMER
> This software is distributed **strictly for educational research, authorized penetration testing, and security auditing of your own systems and API endpoints**.
> Unauthorized testing against third-party systems without prior explicit written permission is strictly prohibited. The author (`cyb3rdr4g0n17`) assumes **no responsibility or legal liability** for any misuse, disruptions, or damages resulting from this tool. Use responsibly and defensively.

---

## 🛡️ Why Use SmsBomber for Security Auditing?

Modern web and mobile applications frequently expose public registration and OTP authentication endpoints. When these endpoints lack robust rate-limiting, IP throttling, and CAPTCHA safeguards:
* SMS gateway balances can be drained by automated bots.
* Attackers can abuse public endpoints to conduct telephony denial-of-service (TDoS).
* Infrastructure can experience resource starvation under concurrent bursts.

**SmsBomber simulates burst traffic** across multi-threaded workers to evaluate whether an endpoint's defensive rate-limiting mechanisms trigger as expected.

---

## ✨ Features

* ⚡ **Multi-Threaded Concurrency:** Powered by Python's `concurrent.futures.ThreadPoolExecutor` for configurable concurrent dispatch testing.
* 🛡️ **Thread-Safe Memory Engine:** Fully isolated payload cloning (`copy.deepcopy`) guarantees payloads never suffer from memory corruption under parallel thread execution.
* 🌐 **Dynamic Custom Proxy Support:** Support for custom HTTP, HTTPS, and SOCKS5 proxies (`--proxy`) to evaluate geo-distributed rate-limiting behavior.
* 🎭 **Rotating User-Agents:** Randomizes realistic mobile and desktop browser headers across each request cycle.
* 🧪 **Dry-Run Mode (`--dry-run`):** Safely validates CLI parameters, thread counts, and provider mappings without generating live network traffic.
* 🔍 **Provider Audit Mode (`--verify`):** Tests every configured API endpoint in `config.json` individually to check uptime, API schema shifts, and success response criteria.
* ⏱️ **Pacing & Throttling Control:** Optional `--delay` flag allows granular inter-request timing to determine precise gateway throttling thresholds.

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
# Clone the repository
git clone https://github.com/cyb3rdr4g0n17/SmsBomber.git
cd SmsBomber

# Install dependencies
pip install -r requirements.txt
```

### 2. Basic Usage Examples

#### Run standard audit (20 requests, 10 threads):
```bash
python bomber.py 9876543210
```

#### Safe simulation (Dry-Run):
```bash
python bomber.py 9876543210 --sms 15 --dry-run --verbose
```

#### Rate-limit threshold test with 0.5s delay and custom threads:
```bash
python bomber.py 9876543210 --sms 50 --threads 5 --delay 0.5
```

#### Audit all configured providers:
```bash
python bomber.py 9876543210 --verify
```

#### Route requests through an intercepting proxy (e.g. Burp Suite or OWASP ZAP):
```bash
python bomber.py 9876543210 --sms 10 --proxy http://127.0.0.1:8080
```

---

## ⌨️ Command-Line Options

```
usage: bomber.py [-h] [--sms SMS] [--country COUNTRY] [--threads THREADS]
                 [--delay DELAY] [--timeout TIMEOUT] [--proxy PROXY]
                 [--verify] [--dry-run] [--verbose]
                 TARGET
```

| Flag | Shorthand | Type | Default | Description |
|:---|:---:|:---:|:---:|:---|
| `TARGET` | *Positional* | `str` | *Required* | Target phone number (7 to 15 digits, without country prefix). |
| `--sms` | `-s` | `int` | `20` | Total number of requests to dispatch. |
| `--country` | `-c` | `str` | `91` | Country dialing code (without `+`). |
| `--threads` | `-t` | `int` | `10` | Maximum concurrent worker threads. |
| `--delay` | `-d` | `float` | `0.0` | Delay in seconds between requests. |
| `--timeout` | | `int` | `15` | HTTP request timeout in seconds. |
| `--proxy` | `-p` | `str` | `None` | Proxy URL (e.g. `http://user:pass@host:port`). |
| `--verify` | `-V` | `flag` | `False` | Provider verification mode (tests all endpoints once). |
| `--dry-run` | | `flag` | `False` | Simulate requests without sending live network traffic. |
| `--verbose` | `-v` | `flag` | `False` | Detailed per-request logging in real-time. |

---

## 🧩 Custom Provider Configuration

All target API endpoints are declared inside [`config.json`](config.json). You can easily add your own endpoints for rate-limit auditing:

### GET Request Provider:
```json
{
  "name": "my_api_get",
  "method": "GET",
  "url": "https://api.example.com/v1/auth/request-otp?phone=",
  "identifier": "true"
}
```

### POST Request Provider (JSON Payload):
```json
{
  "name": "my_api_post",
  "method": "POST",
  "url": "https://api.example.com/v1/auth/request-otp",
  "target_param": "phoneNumber",
  "data_type": "json",
  "data": {
    "phoneNumber": ""
  },
  "headers": {
    "X-Client-Version": "1.0.0"
  },
  "identifier": "OTP_SENT"
}
```

---

## 📜 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

<div align="center">
  <sub>Developed & Maintained for Defensive Security Research by <b><a href="https://github.com/cyb3rdr4g0n17">Rahul Singh (cyb3rdr4g0n17)</a></b></sub>
</div>
