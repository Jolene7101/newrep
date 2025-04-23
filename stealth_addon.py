# mitmproxy stealth & analysis addon
# Save as stealth_addon.py and run: mitmproxy -s stealth_addon.py --listen-port 8080
from mitmproxy import http
import random
import time
import json

# List of realistic user agents (add more as needed)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
]

# Log all requests/responses to a file for later analysis
def log_to_file(entry):
    with open("mitmproxy_traffic_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def request(flow: http.HTTPFlow) -> None:
    # Randomize User-Agent for every request
    flow.request.headers["user-agent"] = random.choice(USER_AGENTS)
    # Add common browser headers
    flow.request.headers["accept-language"] = "en-US,en;q=0.9"
    flow.request.headers["accept-encoding"] = "gzip, deflate, br"
    flow.request.headers["upgrade-insecure-requests"] = "1"
    # Remove headers that may reveal automation
    flow.request.headers.pop("x-requested-with", None)
    # Log request
    log_to_file({
        "timestamp": time.time(),
        "type": "request",
        "method": flow.request.method,
        "url": flow.request.pretty_url,
        "headers": dict(flow.request.headers),
        "cookies": dict(flow.request.cookies),
        "body": flow.request.get_text()[:500],
    })

def response(flow: http.HTTPFlow) -> None:
    # Log response
    log_to_file({
        "timestamp": time.time(),
        "type": "response",
        "status_code": flow.response.status_code,
        "url": flow.request.pretty_url,
        "headers": dict(flow.response.headers),
        "body": flow.response.get_text()[:500],
    })
    # Example: Detect and log anti-bot/captcha pages
    if any(x in flow.response.get_text() for x in ["cf-chl-bypass", "captcha", "cloudflare"]):
        print(f"[mitmproxy] Possible anti-bot detected at {flow.request.pretty_url}")
