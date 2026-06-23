"""
01 - Pwned Password Checker
Project: Check whether a password has appeared in known breaches, without sending
the password anywhere.

How it stays private (k-anonymity):
  1. Hash the password with SHA-1.
  2. Send only the FIRST 5 characters of that hash to the Have I Been Pwned API.
  3. The API returns every breached hash that starts with those 5 characters.
  4. We search that list locally for the rest of our hash.
The full password and the full hash never leave this machine.

Usage:
  python main.py                 # type a password (hidden) and check it
  python main.py -f list.txt     # check every password in a file, one per line
"""

import argparse
import getpass
import hashlib
import sys

import requests

HIBP_RANGE_URL = "https://api.pwnedpasswords.com/range/"


def pwned_count(password: str) -> int:
    """Return how many times a password appears in known breaches (0 if none)."""
    # SHA-1 hex digest, uppercased to match the API's format.
    sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]

    response = requests.get(HIBP_RANGE_URL + prefix, timeout=10)
    response.raise_for_status()

    # Each line looks like "SUFFIX:COUNT". Find the line matching our suffix.
    for line in response.text.splitlines():
        line_suffix, _, count = line.partition(":")
        if line_suffix == suffix:
            return int(count)
    return 0


def report(password: str) -> None:
    count = pwned_count(password)
    if count:
        print(f"  BREACHED: seen {count:,} times. Do not use this password.")
    else:
        print("  OK: not found in any known breach.")


def check_file(path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        passwords = [line.strip() for line in f if line.strip()]
    print(f"Checking {len(passwords)} password(s) from {path}...")
    for pw in passwords:
        print(f"- {pw}")
        report(pw)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check passwords against the Have I Been Pwned database."
    )
    parser.add_argument("-f", "--file", help="Check every password listed in a file.")
    args = parser.parse_args()

    try:
        if args.file:
            check_file(args.file)
        else:
            # getpass hides what you type so the password is not shown on screen.
            password = getpass.getpass("Password to check (hidden): ")
            if not password:
                print("No password entered.")
                return
            report(password)
    except requests.RequestException as exc:
        print(f"Network error talking to the API: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
