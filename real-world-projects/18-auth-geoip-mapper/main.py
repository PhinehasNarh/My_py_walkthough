"""
18 - Auth-Attempt GeoIP Mapper
Project: See where login attempts against your server are coming from.

Parses failed-login lines from SSH auth logs or web access logs, pulls out the source
IPs, looks up their country/city in a MaxMind GeoLite2 database, and summarizes the
attempts by location. Without a database it still ranks the noisiest IPs.

Get the free GeoLite2-City.mmdb from https://www.maxmind.com (account required).

Usage:
  python main.py auth.log
  python main.py access.log --geodb GeoLite2-City.mmdb --top 15

Authorized use: analyze logs from systems you operate.
"""

import argparse
import re
from collections import Counter
from pathlib import Path

IP_RE = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3})")
# Lines that indicate an authentication failure.
FAIL_HINTS = ("Failed password", "authentication failure", "Invalid user",
              "Failed login", '" 401 ', '" 403 ')


def extract_failed_ips(path: Path):
    counts = Counter()
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if any(hint in line for hint in FAIL_HINTS):
                match = IP_RE.search(line)
                if match:
                    counts[match.group(1)] += 1
    return counts


def open_geo(geodb):
    if not geodb:
        return None
    try:
        import geoip2.database
        return geoip2.database.Reader(geodb)
    except Exception as exc:
        print(f"(GeoIP database unavailable: {exc})")
        return None


def locate(reader, ip: str) -> str:
    try:
        r = reader.city(ip)
        city = r.city.name or "?"
        country = r.country.name or "?"
        return f"{city}, {country}"
    except Exception:
        return "unknown location"


def main():
    parser = argparse.ArgumentParser(description="Map failed-login source IPs.")
    parser.add_argument("logfile", type=Path)
    parser.add_argument("--geodb", help="Path to GeoLite2-City.mmdb.")
    parser.add_argument("--top", type=int, default=20, help="Show the top N IPs.")
    args = parser.parse_args()

    if not args.logfile.is_file():
        print(f"Not a file: {args.logfile}")
        return

    counts = extract_failed_ips(args.logfile)
    if not counts:
        print("No failed-login lines recognized.")
        return

    reader = open_geo(args.geodb)
    by_country = Counter()

    print(f"Top {args.top} source IP(s) of failed logins:\n")
    for ip, n in counts.most_common(args.top):
        location = locate(reader, ip) if reader else ""
        if reader:
            by_country[location.split(", ")[-1]] += n
        print(f"  {n:5} attempts  {ip:16} {location}")

    if by_country:
        print("\nBy country:")
        for country, n in by_country.most_common():
            print(f"  {n:5}  {country}")
    if reader:
        reader.close()


if __name__ == "__main__":
    main()
