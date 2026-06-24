"""
20 - OSINT Username Hunter
Project: Check whether a username exists across many sites during an OSINT investigation.

Requests each site's profile URL for a username and decides "present" or "absent" from
the response, running the checks concurrently for speed. Sites are configurable so you
can grow the list.

Usage:
  python main.py johndoe
  python main.py johndoe --sites sites.json

Authorized use: for legitimate OSINT on public profiles. Respect each site's terms.
"""

import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

# name -> {url: profile template with {}, absent: marker text that means "not found"}
DEFAULT_SITES = {
    "GitHub": {"url": "https://github.com/{}", "absent": None},
    "Reddit": {"url": "https://www.reddit.com/user/{}", "absent": None},
    "Instagram": {"url": "https://www.instagram.com/{}/", "absent": None},
    "Twitter/X": {"url": "https://x.com/{}", "absent": None},
    "GitLab": {"url": "https://gitlab.com/{}", "absent": None},
    "Pinterest": {"url": "https://www.pinterest.com/{}/", "absent": None},
}

HEADERS = {"User-Agent": "Mozilla/5.0 (osint-username-hunter; learning project)"}


def check_site(name: str, conf: dict, username: str) -> tuple:
    """Return (name, url, found_bool_or_None)."""
    url = conf["url"].format(username)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
    except requests.RequestException:
        return name, url, None  # could not determine

    if resp.status_code == 404:
        return name, url, False
    if resp.status_code == 200:
        marker = conf.get("absent")
        if marker and marker.lower() in resp.text.lower():
            return name, url, False
        return name, url, True
    return name, url, None


def hunt(username: str, sites: dict, workers: int = 8):
    results = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(check_site, name, conf, username)
                   for name, conf in sites.items()]
        for fut in as_completed(futures):
            results.append(fut.result())
    return sorted(results)


def main():
    parser = argparse.ArgumentParser(description="Find a username across sites.")
    parser.add_argument("username")
    parser.add_argument("--sites", help="JSON file of extra sites to check.")
    args = parser.parse_args()

    sites = dict(DEFAULT_SITES)
    if args.sites:
        with open(args.sites, "r", encoding="utf-8") as f:
            sites.update(json.load(f))

    print(f"Hunting for '{args.username}' across {len(sites)} site(s)...\n")
    for name, url, found in hunt(args.username, sites):
        mark = "FOUND  " if found else "absent " if found is False else "unknown"
        print(f"  [{mark}] {name:12} {url}")


if __name__ == "__main__":
    main()
