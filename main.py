"""
HTTP Request Replayer from Excel
--------------------------------
Reads raw HTTP requests from an Excel file and replays them to a chosen target server.

Features:
- Interactive configuration (target, proxy, rate-limiting)
- Randomized request intervals to simulate natural traffic
- Displays live request insights, ETA, and average response times
- Saves all results (status, error, full request) back to Excel

Author: N Pavan Bhushan Reddy
GitHub: https://github.com/npavanbushanreddy/WAF-Bypass-Testing
Date: 2025-10-19
"""

import os
import sys
import time
import random
import threading
import math
import pandas as pd
import requests
from urllib.parse import urlparse
from tqdm import tqdm
import concurrent.futures
from datetime import datetime, timedelta
import argparse

INPUT_FILE = "Payload-Requests.xlsx"
OUTPUT_FILE = "Output_Result.xlsx"
TARGET_DOMAIN = None
MAX_WORKERS = 10
REQUEST_TIMEOUT = 30

def parse_http_request(raw_request: str):
    """Parse a raw HTTP request into method, path, headers, and body."""
    cleaned_request = raw_request.replace("_x000D_", "").replace("\r", "")
    lines = cleaned_request.split("\n")

    request_line = next((l.strip() for l in lines if l.strip()), None)
    if not request_line:
        raise ValueError("Empty HTTP request")

    try:
        method, path, protocol = request_line.split()
    except ValueError:
        raise ValueError("Invalid HTTP request line")

    headers, body_lines = {}, []
    header_ended = False
    start_index = lines.index(request_line) + 1 if request_line in lines else 1

    for line in lines[start_index:]:
        stripped = line.strip()
        if not header_ended:
            if not stripped:
                header_ended = True
            elif ": " in stripped:
                key, value = stripped.split(": ", 1)
                headers[key.strip()] = value.strip()
            else:
                header_ended = True
                body_lines.append(line.rstrip("\\r"))
        else:
            body_lines.append(line.rstrip("\\r"))

    body = "\\n".join(body_lines).strip()
    complete_request = (
        f"{method} {path} {protocol}\\n"
        + "\\n".join(f"{k}: {v}" for k, v in headers.items())
        + ("\n\n" + body if body else "")
    )
    return method, path, headers, body, complete_request

def build_schedule(total_requests: int, requests_per_minute: int) -> list:
    """Build a randomized schedule of timestamps ensuring <= requests_per_minute per minute."""
    if requests_per_minute <= 0:
        raise ValueError("requests_per_minute must be > 0")

    now = time.time()
    schedule = []
    windows = math.ceil(total_requests / requests_per_minute)
    assigned = 0

    for w in range(windows):
        remaining = total_requests - assigned
        in_window = min(requests_per_minute, remaining)
        offsets = sorted(random.uniform(0, 60) for _ in range(in_window))
        start = now + w * 60
        for off in offsets:
            schedule.append(start + off)
            assigned += 1

    return schedule

def send_request(raw_request, index, session, results, start_time, total_requests):
    """Send a single request and print status, timing, and ETA summary."""
    try:
        method, path, headers, body, full_req = parse_http_request(raw_request)
        full_url = f"http://{TARGET_DOMAIN}{path}"

        if urlparse(full_url).hostname != TARGET_DOMAIN:
            return index, None, "Invalid host in request", full_req

        req_start = time.time()
        response = session.request(
            method=method, url=full_url, headers=headers, data=body or None, timeout=REQUEST_TIMEOUT
        )
        elapsed = time.time() - req_start

        with threading.Lock():
            results.append(elapsed)
            done = len(results)
            avg_time = sum(results) / done
            percent = (done / total_requests) * 100 if total_requests else 100

            elapsed_total = time.time() - start_time
            est_total = (elapsed_total / done) * total_requests if done > 0 else 0
            remaining = max(0, est_total - elapsed_total)
            eta = datetime.now() + timedelta(seconds=remaining)

            mins, secs = divmod(int(remaining), 60)
            rem_str = f"{mins}m {secs}s" if mins else f"{secs}s"

            print(f"\\n📊 Request #{index+1}")
            print(f"  ➜ Sent At       : {datetime.now().strftime('%H:%M:%S')}")
            print(f"  ➜ ETA (Finish)  : {eta.strftime('%H:%M:%S')}  (~{rem_str} left)")
            print(f"  ➜ Method        : {method}")
            print(f"  ➜ URL           : {full_url}")
            print(f"  ➜ Status        : {response.status_code}")
            print(f"  ➜ Time Taken    : {elapsed:.2f}s | Avg: {avg_time:.2f}s")
            print(f"  ➜ Progress      : {done}/{total_requests} ({percent:.1f}%)\\n")

        return index, response.status_code, None, full_req

    except Exception as e:
        return index, None, f"Error: {e}", raw_request

def send_request_at(raw_request, index, session, results, scheduled_time, start_time, total_requests):
    """Send the request according to its scheduled time."""
    try:
        if scheduled_time:
            delay = scheduled_time - time.time()
            if delay > 0:
                # responsive sleep loop
                end = time.time() + delay
                while time.time() < end:
                    time.sleep(min(0.5, end - time.time()))
        return send_request(raw_request, index, session, results, start_time, total_requests)
    except Exception as e:
        return index, None, f"Error in scheduled send: {e}", None

def user_setup():
    """Prompt for target, proxy, and rate-limit configuration."""
    print("\\n🛠  Configuration Setup\\n")
    global TARGET_DOMAIN
    TARGET_DOMAIN = input("Enter target website (domain only, e.g., demo.testfire.net): ").strip()
    if not TARGET_DOMAIN:
        TARGET_DOMAIN = "demo.testfire.net"
        print("⚠ Using default: demo.testfire.net")

    use_proxy = input("Use proxy (e.g., BurpSuite)? (Yes/No): ").strip().lower()
    if use_proxy == "yes":
        proxy_host = input("Proxy Host [127.0.0.1]: ").strip() or "127.0.0.1"
        proxy_port = input("Proxy Port [8080]: ").strip() or "8080"
        proxies = {"http": f"http://{proxy_host}:{proxy_port}"}
        print(f"✅ Proxy enabled ({proxy_host}:{proxy_port})")
    else:
        proxies = None
        print("🚫 Proxy disabled")

    use_limit = input("Enable rate limiting? (Yes/No): ").strip().lower()
    if use_limit == "yes":
        try:
            rpm = int(input("Enter requests per minute: ").strip())
            if rpm <= 0:
                raise ValueError
            print(f"✅ Rate limiting set to {rpm} req/min")
        except ValueError:
            rpm = 5
            print("⚠ Invalid value — using default 5 req/min")
    else:
        rpm = None
        print("🚫 Rate limiting disabled")

    print("\\n--------------------------------------")
    print(f"Target Domain : {TARGET_DOMAIN}")
    print(f"Proxy Enabled : {'Yes' if proxies else 'No'}")
    print(f"Rate Limiting : {'Yes' if rpm else 'No'}")
    print("--------------------------------------\\n")

    return proxies, rpm

def main():
    """Main entry: read Excel, replay requests, and log results."""
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Input file '{INPUT_FILE}' not found.")
        sys.exit(1)

    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    # parse CLI args (supports --dry-run to avoid real network calls in CI)
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--dry-run', action='store_true', help='Simulate requests without sending network calls')
    args, _ = parser.parse_known_args()
    dry_run = bool(args.dry_run)

    proxies, rpm = user_setup()

    df = pd.read_excel(INPUT_FILE)
    df["Http-Requests"] = df["Http-Requests"].str.replace("_x000D_", "", regex=False)
    df["Status"] = pd.NA
    df["Error"] = None
    df["Complete HTTP Request"] = None

    session = requests.Session()
    if proxies:
        session.proxies = proxies
    session.timeout = REQUEST_TIMEOUT

    results = []
    total = len(df.index)
    start = time.time()

    schedule = build_schedule(total, rpm) if rpm else None
    if schedule:
        preview = [datetime.fromtimestamp(t).strftime("%H:%M:%S") for t in schedule[:min(5, len(schedule))]]
        print(f"🔀 Schedule generated (first {len(preview)}): {preview}\\n")
    else:
        print("⚠ No scheduling — sending immediately.\\n")

    print(f"🚀 Starting replay to {TARGET_DOMAIN}...\\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(
                send_request_at, df.at[i, "Http-Requests"], i, session, results,
                schedule[i] if schedule else None, start, total, dry_run
            ): i
            for i in df.index
        }

        with tqdm(total=len(futures), desc="Processing Requests", unit="req", ncols=100) as pbar:
            for future in concurrent.futures.as_completed(futures):
                i, status, error, full_req = future.result()
                df.at[i, "Status"] = status if status is not None else pd.NA
                df.at[i, "Error"] = error
                df.at[i, "Complete HTTP Request"] = full_req
                pbar.update(1)

    df.to_excel(OUTPUT_FILE, index=False)
    print(f"\\n✅ Completed! Results saved to '{OUTPUT_FILE}'")
    if results:
        print(f"📊 Average response time: {sum(results)/len(results):.2f}s")

if __name__ == "__main__":
    main()
