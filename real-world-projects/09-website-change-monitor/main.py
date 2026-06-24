"""
09 - Website Change Monitor
Project: Get told when a web page changes instead of refreshing it yourself.

Fetches a page, saves a snapshot, and on later runs compares the new version against
the saved one and prints exactly what changed. Use --watch to keep checking on an
interval.

Usage:
  python main.py https://example.com
  python main.py https://example.com --watch --interval 300
"""

import argparse
import difflib
import hashlib
import time
from pathlib import Path

import requests

SNAPSHOT_DIR = Path(__file__).parent / ".snapshots"
HEADERS = {"User-Agent": "change-monitor/1.0 (learning project)"}


def fetch(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    return response.text


def snapshot_path(url: str) -> Path:
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return SNAPSHOT_DIR / f"{key}.txt"


def diff_text(old: str, new: str, context: int = 1) -> str:
    """Return a readable unified diff between two versions of the page."""
    lines = difflib.unified_diff(
        old.splitlines(), new.splitlines(),
        fromfile="previous", tofile="current", lineterm="", n=context,
    )
    return "\n".join(lines)


def check_once(url: str) -> bool:
    """Fetch the page and compare to the snapshot. Returns True if it changed."""
    SNAPSHOT_DIR.mkdir(exist_ok=True)
    snap = snapshot_path(url)
    new = fetch(url)

    if not snap.exists():
        snap.write_text(new, encoding="utf-8")
        print(f"Baseline saved for {url}")
        return False

    old = snap.read_text(encoding="utf-8")
    if old == new:
        print(f"No change: {url}")
        return False

    print(f"CHANGED: {url}")
    diff = diff_text(old, new)
    # Show a trimmed diff so a big page does not flood the screen.
    shown = diff.splitlines()
    for line in shown[:40]:
        print(f"  {line}")
    if len(shown) > 40:
        print(f"  ... ({len(shown) - 40} more diff lines)")
    snap.write_text(new, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Watch a web page for changes.")
    parser.add_argument("url")
    parser.add_argument("--watch", action="store_true", help="Keep checking on an interval.")
    parser.add_argument("--interval", type=int, default=300,
                        help="Seconds between checks in --watch mode (default 300).")
    args = parser.parse_args()

    try:
        if not args.watch:
            check_once(args.url)
            return
        print(f"Watching {args.url} every {args.interval}s. Press Ctrl-C to stop.")
        while True:
            check_once(args.url)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")
    except requests.RequestException as exc:
        print(f"Could not fetch the page: {exc}")


if __name__ == "__main__":
    main()
