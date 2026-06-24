"""
30 - Browser History Forensics
Project: Reconstruct browsing activity from a browser's own database, on a machine you own.

Browsers store history in a SQLite file. This tool reads that file, converts the
browser-specific timestamps into readable dates, and builds a searchable timeline of
visits. It opens the database read-only so the original is never changed.

Usage:
  python main.py "History"                       # Chrome/Edge history file
  python main.py places.sqlite --browser firefox
  python main.py "History" --search github --since 2026-01-01 --limit 50

Tip: copy the History file first, since the browser locks it while running.
Authorized use: only on machines and accounts you own or are authorized to examine.
"""

import argparse
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Chrome/Edge store time as microseconds since 1601-01-01 (the WebKit epoch).
WEBKIT_EPOCH = datetime(1601, 1, 1, tzinfo=timezone.utc)

QUERIES = {
    "chrome": "SELECT url, title, visit_count, last_visit_time FROM urls",
    "firefox": "SELECT url, title, visit_count, last_visit_date FROM moz_places",
}


def to_datetime(raw, browser):
    if not raw:
        return None
    if browser == "chrome":
        return WEBKIT_EPOCH + timedelta(microseconds=raw)
    # Firefox uses microseconds since the normal Unix epoch.
    return datetime.fromtimestamp(raw / 1_000_000, tz=timezone.utc)


def read_history(db_path: Path, browser: str):
    # Open read-only so we never modify the evidence.
    uri = f"file:{db_path}?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    try:
        rows = con.execute(QUERIES[browser]).fetchall()
    finally:
        con.close()

    visits = []
    for url, title, count, raw_time in rows:
        visits.append({
            "url": url,
            "title": title or "",
            "visits": count or 0,
            "when": to_datetime(raw_time, browser),
        })
    return visits


def main():
    parser = argparse.ArgumentParser(description="Build a timeline from browser history.")
    parser.add_argument("database", type=Path)
    parser.add_argument("--browser", choices=["chrome", "firefox"], default="chrome")
    parser.add_argument("--search", help="Only show URLs/titles containing this text.")
    parser.add_argument("--since", help="Only show visits on or after YYYY-MM-DD.")
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    if not args.database.exists():
        print(f"Not found: {args.database}")
        return

    visits = read_history(args.database, args.browser)

    if args.search:
        term = args.search.lower()
        visits = [v for v in visits if term in v["url"].lower() or term in v["title"].lower()]
    if args.since:
        since = datetime.strptime(args.since, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        visits = [v for v in visits if v["when"] and v["when"] >= since]

    # Newest first.
    visits.sort(key=lambda v: v["when"] or WEBKIT_EPOCH, reverse=True)

    print(f"{len(visits)} matching visit(s) (showing up to {args.limit}):\n")
    for v in visits[:args.limit]:
        when = v["when"].strftime("%Y-%m-%d %H:%M") if v["when"] else "unknown time"
        print(f"  {when}  ({v['visits']}x)  {v['title'][:50]}")
        print(f"      {v['url'][:90]}")


if __name__ == "__main__":
    main()
