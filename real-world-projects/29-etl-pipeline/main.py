"""
29 - ETL Pipeline
Project: Pull data from an API, clean it, store it, and report on a schedule.

A small Extract-Transform-Load pipeline: it fetches JSON records from an API, validates
and reshapes them, loads them into SQLite (skipping rows it already has, so re-runs are
incremental), and prints a summary report. Use --watch to run it on an interval.

Usage:
  python main.py
  python main.py --db data.db --report
  python main.py --watch --interval 600

Default source is jsonplaceholder.typicode.com/posts (a free demo API).
"""

import argparse
import sqlite3
import time
from pathlib import Path

import requests

DEFAULT_URL = "https://jsonplaceholder.typicode.com/posts"
DEFAULT_DB = Path(__file__).parent / "etl.db"


def extract(url: str):
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    return resp.json()


def transform(records):
    """Keep valid rows and reshape them into the columns we store."""
    clean = []
    for r in records:
        if not isinstance(r, dict) or "id" not in r:
            continue
        clean.append({
            "id": r["id"],
            "user_id": r.get("userId"),
            "title": (r.get("title") or "").strip(),
            "title_length": len((r.get("title") or "").strip()),
        })
    return clean


def load(db_path: Path, rows):
    con = sqlite3.connect(db_path)
    con.execute("""CREATE TABLE IF NOT EXISTS posts (
                     id INTEGER PRIMARY KEY, user_id INTEGER,
                     title TEXT, title_length INTEGER)""")
    before = con.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    con.executemany(
        "INSERT OR IGNORE INTO posts (id, user_id, title, title_length) VALUES (?,?,?,?)",
        [(r["id"], r["user_id"], r["title"], r["title_length"]) for r in rows],
    )
    con.commit()
    after = con.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    con.close()
    return after - before  # number of new rows inserted


def report(db_path: Path):
    con = sqlite3.connect(db_path)
    total = con.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    avg_len = con.execute("SELECT AVG(title_length) FROM posts").fetchone()[0] or 0
    top_users = con.execute(
        "SELECT user_id, COUNT(*) c FROM posts GROUP BY user_id ORDER BY c DESC LIMIT 3"
    ).fetchall()
    con.close()
    print(f"Rows stored: {total}")
    print(f"Average title length: {avg_len:.1f} chars")
    print("Top users by post count:", ", ".join(f"user {u}={c}" for u, c in top_users))


def run_once(url: str, db_path: Path):
    rows = transform(extract(url))
    new = load(db_path, rows)
    print(f"Pulled {len(rows)} record(s); {new} new row(s) inserted.")
    report(db_path)


def main():
    parser = argparse.ArgumentParser(description="Run a small ETL pipeline.")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--report", action="store_true", help="Just print the report and exit.")
    parser.add_argument("--watch", action="store_true", help="Run repeatedly on an interval.")
    parser.add_argument("--interval", type=int, default=600, help="Seconds between runs.")
    args = parser.parse_args()

    if args.report:
        report(args.db)
        return

    try:
        if not args.watch:
            run_once(args.url, args.db)
            return
        print(f"Running every {args.interval}s. Ctrl-C to stop.")
        while True:
            run_once(args.url, args.db)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")
    except requests.RequestException as exc:
        print(f"Extract failed: {exc}")


if __name__ == "__main__":
    main()
