import time

import urllib.request
import urllib.error

import argparse

RETRY_DELAY_SECONDS = 10
TIMEOUT_SECONDS = 30

def main():
    parser = argparse.ArgumentParser(description="test server response")
    parser.add_argument("--port", type=int, default=2993, help="Port number of the server to test")
    args = parser.parse_args()

    url = f"http://localhost:{args.port}/v1/models"

    while True:
        try:
            with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as resp:
                # Any HTTP response means the connection succeeded
                status = getattr(resp, "status", None) or resp.getcode()
                print(f"Connected: HTTP {status}")
                return
        except urllib.error.HTTPError as e:
            # HTTP error still means we connected successfully
            print(f"Connected (HTTP error): HTTP {e.code}")
            return
        except Exception as e:
            print(f"Connection failed: {e}. Retrying in {RETRY_DELAY_SECONDS} seconds...")
            time.sleep(RETRY_DELAY_SECONDS)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass